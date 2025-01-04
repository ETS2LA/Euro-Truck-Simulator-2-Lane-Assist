"""
Network utilities for ETS2LA's other modules.
It supports downloading files from one or more CDNs, returning the downloaded file path.
"""

from pathlib import Path
import requests
import tqdm


def DownloadFile(url: str,
                 save_path: str | Path,
                 *,
                 session: requests.Session | None = None,
                 chunk_size: int = 8192,
                 rich: bool = False):
    """Downloads a file from a URL to a specified path.

    Args:
        url (str): Source URL to download from.
        save_path (str | Path): The path to save the downloaded file to.
        session (requests.Session | None, optional): Optional requests session to use for downloading. If None, a new session will be created. Defaults to None.
        chunk_size (int, optional): The size of each chunk to download in bytes. Defaults to 8192.

    Returns:
        Path: The path to the downloaded file.
    """
    if not isinstance(save_path, Path):
        save_path = Path(save_path)
    save_path.parent.mkdir(parents=True, exist_ok=True)

    resp = (session or requests).get(url, stream=True)

    resp.raise_for_status()

    with save_path.open('wb') as f:
        iterator = resp.iter_content(chunk_size=chunk_size)
        if rich:
            iterator = tqdm.tqdm(iterator,
                                 total=int(
                                     resp.headers.get('content-length', 0)),
                                 unit='B',
                                 unit_scale=True,
                                 desc=url.split('/')[-1])
        for chunk in iterator:
            f.write(chunk)

        if rich:
            assert isinstance(iterator, tqdm.tqdm)
            iterator.refresh()
            iterator.close()

    return save_path


def DownloadFileMultiSource(urls: list[str],
                            save_path: str | Path,
                            *,
                            session: requests.Session | None = None,
                            chunk_size: int = 8192):
    """Downloads a file from multiple URLs to a specified path.

    Args:
        urls (list[str]): List of source URLs to download from.
        save_path (str | Path): The path to save the downloaded file to.
        session (requests.Session | None, optional): Optional requests session to use for downloading. If None, a new session will be created. Defaults to None.
        chunk_size (int, optional): The size of each chunk to download in bytes. Defaults to 8192.

    Returns:
        Path: The path to the downloaded file.
    """
    for url in urls:
        try:
            return DownloadFile(url,
                                save_path,
                                session=session,
                                chunk_size=chunk_size)
        except requests.exceptions.RequestException:
            pass
    raise requests.exceptions.RequestException(
        "Failed to download file from any source.")
