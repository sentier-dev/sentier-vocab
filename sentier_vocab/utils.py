import re
from pathlib import Path

import requests
from loguru import logger
from platformdirs import user_data_dir
from rdflib import Graph

from sentier_vocab.errors import GraphFilterError


def get_filename(response: requests.Response, url: str) -> str:
    """
    Get filename from response headers or URL.
    """
    if "Content-Disposition" in response.headers.keys():
        filename = re.findall("filename=(.+)", response.headers["Content-Disposition"])[0]
    else:
        filename = url.split("/")[-1]
    if filename[0] in "'\"":
        filename = filename[1:]
    if filename[-1] in "'\"":
        filename = filename[:-1]
    if not filename:
        raise ValueError("Can't determine suitable filename")
    return filename


def streaming_download(
    url: str, filename: str | None = None, dirpath: Path | None = None, chunk_size: int = 4096 * 8
) -> Path:
    """
    Download file from URL.

    Parameters
    ----------
    url : str
        URL to download from.
    filename : str, optional
        Filename to save to. If not given, will be determined from URL.
    dirpath : Path, optional
        Directory to save to. If not given, will be current working directory.
    chunk_size : int, optional
        Chunk size to use when downloading.

    Returns
    -------
    pathlib.Path
        Path to downloaded file.
    """
    response = requests.get(url, stream=True)
    if response.status_code != 200:
        raise ValueError(f"URL {url} returns status code {response.status_code}")

    total_length = response.headers.get("content-length")
    filename = filename or get_filename(response, url)
    dirpath = Path(dirpath) if dirpath else Path(user_data_dir("sentier.dev", "dds"))
    dirpath.mkdir(parents=True, exist_ok=True)
    filepath = dirpath / filename

    with open(filepath, "wb") as f:
        logger.info(f"Downloading {filename} to {filepath}")
        if not total_length:
            f.write(response.content)
        else:
            total_length = int(total_length)
            for data in response.iter_content(chunk_size=chunk_size):
                f.write(data)

    return filepath


def get_one_in_graph(graph: Graph, criteria: tuple) -> tuple:
    candidates = list(graph.triples(criteria))
    if len(candidates) == 1:
        return candidates[0]
    else:
        ERROR = f"""
Given criteria produced {len(candidates)} results; needed exactly 1.
Criteria: {criteria}"""
        if candidates:
            ERROR += "\n\t" + "\n\t".join(str(line) for line in candidates)
        raise GraphFilterError(ERROR)
