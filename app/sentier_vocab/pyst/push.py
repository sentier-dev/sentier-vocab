"""Send a publication plan to a PyST server, or take it back out.

A push only adds: it posts schemes, then concepts, then relationships, and
treats "already exists" (409) as done, so it can be stopped and run again. It
never updates or deletes, and never posts a scheme marked ``existing``.
``remove`` is the way back: it deletes exactly the plan's relationships,
concepts and (non-existing) schemes.
"""

from __future__ import annotations

import os
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Callable, Iterable, Protocol

import httpx

from sentier_vocab.pyst.publication import Plan, Scheme, api_path, relationship_pair

BATCH = 200
RETRY_STATUS = frozenset({502, 503, 504})
API_KEY_ENV = "PYST_API_KEY"


class PushError(RuntimeError):
    """The server refused something, or the request cannot be made."""


class Server(Protocol):
    def request(self, method: str, path: str, json: object = None) -> tuple[int, str]: ...


class HttpServer:
    """A PyST server over HTTP. One connection pool, shared by the worker threads."""

    def __init__(self, url: str, api_key: str, timeout: float = 120.0):
        self._http = httpx.Client(
            base_url=url,
            headers={"x-pyst-auth-token": api_key},
            timeout=timeout,
            transport=httpx.HTTPTransport(retries=5),
        )

    def request(self, method: str, path: str, json: object = None) -> tuple[int, str]:
        response = self._http.request(method, path, json=json)
        return response.status_code, response.text


def connect(url: str) -> HttpServer:
    """Server at ``url``, with the write key taken from the environment."""
    api_key = os.environ.get(API_KEY_ENV)
    if not api_key:
        raise PushError(f"set {API_KEY_ENV} to the server's write key")
    return HttpServer(url, api_key)


def _call(
    server: Server, method: str, path: str, json: object, ok: Iterable[int], attempts: int
) -> int:
    """Status of the call if it is one of ``ok``; retries gateway errors, raises otherwise."""
    for attempt in range(1, attempts + 1):
        status, text = server.request(method, path, json)
        if status in ok:
            return status
        if status not in RETRY_STATUS or attempt == attempts:
            raise PushError(f"{method} {path}: {status} {text[:500]}")
        time.sleep(2 * attempt)
    raise PushError(f"{method} {path}: no attempt made")


def _selected(plan: Plan, only: Iterable[str] | None) -> tuple[Scheme, ...]:
    if not only:
        return plan.schemes
    wanted = set(only)
    unknown = wanted - {scheme.iri for scheme in plan.schemes}
    if unknown:
        raise PushError(f"schemes not in the plan: {sorted(unknown)}")
    return tuple(scheme for scheme in plan.schemes if scheme.iri in wanted)


def _relationships(plan: Plan, schemes: tuple[Scheme, ...]) -> list[dict]:
    subjects = {doc["@id"] for scheme in schemes for doc in scheme.concepts}
    return [doc for doc in plan.relationships if doc["@id"] in subjects]


def _count(statuses: Iterable[int]) -> dict[str, int]:
    statuses = list(statuses)
    existing = sum(1 for status in statuses if status == 409)
    return {"created": len(statuses) - existing, "existing": existing}


def _post_relationships(server: Server, batch: list[dict], attempts: int) -> list[int]:
    """One call for the batch; if any pair is already there, one call per pair."""
    path = api_path("relationships")
    if _call(server, "POST", path, batch, (200, 409), attempts) == 200:
        return [200] * len(batch)
    return [_call(server, "POST", path, [doc], (200, 409), attempts) for doc in batch]


def push(
    plan: Plan,
    server: Server,
    only: Iterable[str] | None = None,
    workers: int = 1,
    attempts: int = 3,
    log: Callable[[str], None] = print,
) -> dict[str, dict[str, int]]:
    """Add the plan (or the schemes named in ``only``) to the server."""
    schemes = _selected(plan, only)

    def post(kind: str, document: dict) -> int:
        path = api_path(kind, document["@id"])
        return _call(server, "POST", path, document, (200, 409), attempts)

    scheme_statuses = [
        post("concept_schemes", scheme.document) for scheme in schemes if scheme.document
    ]
    concept_statuses: list[int] = []
    with ThreadPoolExecutor(max_workers=workers) as pool:
        for scheme in schemes:
            started = time.monotonic()
            statuses = list(pool.map(lambda doc: post("concepts", doc), scheme.concepts))
            concept_statuses += statuses
            log(
                f"{scheme.iri}: {len(statuses)} concepts "
                f"({_count(statuses)['existing']} already there) "
                f"in {time.monotonic() - started:.0f} s"
            )
    relationships = _relationships(plan, schemes)
    relationship_statuses: list[int] = []
    for start in range(0, len(relationships), BATCH):
        relationship_statuses += _post_relationships(
            server, relationships[start : start + BATCH], attempts
        )
    log(f"{len(relationship_statuses)} relationships")
    return {
        "schemes": _count(scheme_statuses),
        "concepts": _count(concept_statuses),
        "relationships": _count(relationship_statuses),
    }


def remove(
    plan: Plan,
    server: Server,
    only: Iterable[str] | None = None,
    workers: int = 1,
    attempts: int = 3,
    log: Callable[[str], None] = print,
) -> dict[str, int]:
    """Delete the plan's relationships, concepts and non-existing schemes from the server."""
    schemes = _selected(plan, only)
    relationships = _relationships(plan, schemes)
    for start in range(0, len(relationships), BATCH):
        batch = relationships[start : start + BATCH]
        _call(server, "DELETE", api_path("relationships"), batch, (200,), attempts)

    def delete(kind: str, iri: str) -> int:
        return _call(server, "DELETE", api_path(kind, iri), None, (204, 404), attempts)

    deleted = 0
    with ThreadPoolExecutor(max_workers=workers) as pool:
        for scheme in schemes:
            iris = [doc["@id"] for doc in scheme.concepts]
            statuses = list(pool.map(lambda iri: delete("concepts", iri), iris))
            found = sum(1 for status in statuses if status == 204)
            deleted += found
            log(f"{scheme.iri}: {found} of {len(iris)} concepts were there and are removed")
    removed_schemes = sum(
        1
        for scheme in schemes
        if not scheme.existing and delete("concept_schemes", scheme.iri) == 204
    )
    return {
        "relationships": len({relationship_pair(doc) for doc in relationships}),
        "concepts": deleted,
        "schemes": removed_schemes,
    }
