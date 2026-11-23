"""Sending a publication plan to PyST, against a fake server."""

import pytest
from tests.test_pyst_publication import (
    CONFIG,
    ORG,
    ORG_SCHEME,
    PROD,
    PROD_SCHEME,
    UNITS,
    demo_relations,
    demo_terms,
)

from sentier_vocab.pyst.publication import api_path, build_plan
from sentier_vocab.pyst.push import PushError, push, remove


class FakeServer:
    """Remembers what it holds; answers like PyST (200, 409 on duplicates, 404, 422)."""

    def __init__(self, schemes=()):
        self.schemes = set(schemes)
        self.concepts = {}
        self.pairs = set()
        self.calls = []
        self.fail_on = None

    def request(self, method, path, json=None):
        self.calls.append((method, path))
        if self.fail_on and self.fail_on in path:
            return 500, "boom"
        kind = path.split("/")[3]
        if kind == "relationships":
            pairs = {
                (d["@id"], next(v for k, v in d.items() if k != "@id")[0]["@id"]) for d in json
            }
            if method == "DELETE":
                self.pairs -= pairs
                return 200, ""
            if pairs & self.pairs:
                source, target = sorted(pairs & self.pairs)[0]
                return (
                    409,
                    f"Relationship between source `{source}` and target `{target}` already exists",
                )
            self.pairs |= pairs
            return 200, ""
        store = self.schemes if kind == "concept_schemes" else self.concepts
        if method == "DELETE":
            if path not in {api_path(kind, iri) for iri in store}:
                return 404, "missing"
            iri = next(i for i in store if api_path(kind, i) == path)
            store.discard(iri) if isinstance(store, set) else store.pop(iri)
            return 204, ""
        iri = json["@id"]
        if iri in store:
            return 409, "exists"
        if kind == "concept_schemes":
            store.add(iri)
        else:
            scheme = json["http://www.w3.org/2004/02/skos/core#inScheme"][0]["@id"]
            if scheme not in self.schemes:
                return 422, "At least one of the specified concept schemes must be in the database"
            store[iri] = json
        return 200, ""


@pytest.fixture
def plan():
    return build_plan(demo_terms(), demo_relations(), CONFIG)


def test_push_creates_schemes_then_concepts_then_relationships(plan):
    server = FakeServer(schemes=[UNITS])
    report = push(plan, server, log=lambda *_: None)
    assert server.schemes == {UNITS, ORG_SCHEME, PROD_SCHEME}
    assert len(server.concepts) == 5
    assert server.pairs == {(ORG + "cow", ORG + "animal"), (PROD + "milk", ORG + "cow")}
    assert report == {
        "schemes": {"created": 2, "existing": 0},
        "concepts": {"created": 5, "existing": 0},
        "relationships": {"created": 2, "existing": 0},
    }
    kinds = [path.split("/")[3] for _, path in server.calls]
    assert kinds == sorted(kinds, key=["concept_schemes", "concepts", "relationships"].index)


def test_push_never_posts_an_existing_scheme(plan):
    server = FakeServer(schemes=[UNITS])
    push(plan, server, log=lambda *_: None)
    assert ("POST", api_path("concept_schemes", UNITS)) not in server.calls


def test_a_second_push_changes_nothing(plan):
    server = FakeServer(schemes=[UNITS])
    push(plan, server, log=lambda *_: None)
    report = push(plan, server, log=lambda *_: None)
    assert report == {
        "schemes": {"created": 0, "existing": 2},
        "concepts": {"created": 0, "existing": 5},
        "relationships": {"created": 0, "existing": 2},
    }
    assert len(server.concepts) == 5 and len(server.pairs) == 2


def test_a_partly_loaded_batch_of_relationships_is_completed(plan):
    server = FakeServer(schemes=[UNITS])
    server.pairs = {(ORG + "cow", ORG + "animal")}
    report = push(plan, server, log=lambda *_: None)
    assert report["relationships"] == {"created": 1, "existing": 1}
    assert (PROD + "milk", ORG + "cow") in server.pairs


def test_push_of_one_scheme_leaves_the_others_alone(plan):
    server = FakeServer(schemes=[UNITS])
    push(plan, server, only=[PROD_SCHEME], log=lambda *_: None)
    assert server.schemes == {UNITS, PROD_SCHEME}
    assert set(server.concepts) == {PROD + "milk"}
    assert server.pairs == {(PROD + "milk", ORG + "cow")}


def test_an_unknown_scheme_name_is_refused(plan):
    with pytest.raises(PushError, match="not in the plan"):
        push(plan, FakeServer(), only=["https://example.org/nope"], log=lambda *_: None)


def test_a_server_error_stops_the_push(plan):
    server = FakeServer(schemes=[UNITS])
    server.fail_on = "cow"
    with pytest.raises(PushError, match="500"):
        push(plan, server, log=lambda *_: None, attempts=1)


def test_remove_deletes_what_push_created_and_keeps_the_existing_scheme(plan):
    server = FakeServer(schemes=[UNITS])
    server.concepts[UNITS + "unit/KiloGM"] = {"@id": UNITS + "unit/KiloGM"}
    push(plan, server, log=lambda *_: None)
    remove(plan, server, log=lambda *_: None)
    assert server.schemes == {UNITS}
    assert set(server.concepts) == {UNITS + "unit/KiloGM"}
    assert server.pairs == set()


def test_remove_on_an_empty_server_is_harmless(plan):
    server = FakeServer(schemes=[UNITS])
    remove(plan, server, log=lambda *_: None)
    assert server.schemes == {UNITS}
