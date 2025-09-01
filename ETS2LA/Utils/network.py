"""
Network utilities for ETS2LA's other modules.
It supports downloading files from one or more CDNs, returning the downloaded file path.
"""

import ctypes
import ctypes.wintypes
import tempfile
import time
from pathlib import Path

import logging
import requests
import tqdm


class WINHTTP_PROXY_INFO(ctypes.Structure):
    _fields_ = [
        ("dwAccessType", ctypes.wintypes.DWORD),
        ("lpszProxy", ctypes.wintypes.LPWSTR),
        ("lpszProxyBypass", ctypes.wintypes.LPWSTR),
    ]


class WINHTTP_CURRENT_USER_IE_PROXY_CONFIG(ctypes.Structure):
    _fields_ = [
        ("fAutoDetect", ctypes.wintypes.BOOL),
        ("lpszAutoConfigUrl", ctypes.wintypes.LPWSTR),
        ("lpszProxy", ctypes.wintypes.LPWSTR),
        ("lpszProxyBypass", ctypes.wintypes.LPWSTR),
    ]


def GetSystemProxy() -> str | None:
    # winhttp.h
    # WinHttpGetDefaultProxyConfiguration
    proxy_info = WINHTTP_PROXY_INFO()
    assert ctypes.windll.winhttp.WinHttpGetDefaultProxyConfiguration(
        ctypes.byref(proxy_info)
    )
    res1 = proxy_info.dwAccessType, proxy_info.lpszProxy, proxy_info.lpszProxyBypass

    proxy_config = WINHTTP_CURRENT_USER_IE_PROXY_CONFIG()
    assert ctypes.windll.winhttp.WinHttpGetIEProxyConfigForCurrentUser(
        ctypes.byref(proxy_config)
    )
    res2 = (
        proxy_config.fAutoDetect,
        proxy_config.lpszAutoConfigUrl,
        proxy_config.lpszProxy,
        proxy_config.lpszProxyBypass,
    )

    return res1[1] or res2[2] or None


def ChooseBestProvider(urls: list[str], timeout: int | float = 3):
    """Chooses the best provider for downloading a file from a list of URLs.

    Args:
        urls (list[str]): List of URLs to choose from.

    Returns:
        str: The best provider URL.
    """

    results: list[tuple[str, int]] = []

    with tempfile.TemporaryFile("wb", suffix=".tmpdat") as tempf:
        tempf.seek(0)
        for url in urls:
            try:
                st = time.perf_counter_ns()
                with requests.get(url, stream=True, timeout=timeout) as r:
                    r.raise_for_status()
                    tempf.seek(0)
                    tempf.write(r.content)
                endt = time.perf_counter_ns()
                results.append((url, endt - st))
            except requests.exceptions.RequestException:
                continue

    if not results:
        raise requests.exceptions.RequestException(
            "Failed to download file from any source."
        )

    return sorted(results, key=lambda x: x[1])[0][0]


def DownloadFile(
    url: str,
    save_path: str | Path,
    *,
    session: requests.Session | None = None,
    chunk_size: int = 8192,
    rich: bool = False,
    extra_kwargs: dict | None = None,
):
    """Downloads a file from a URL to a specified path.

    Args:
        url (str): Source URL to download from.
        save_path (str | Path): The path to save the downloaded file to.
        session (requests.Session | None, optional): Optional requests session to use for downloading. If None, a new session will be created. Defaults to None.
        chunk_size (int, optional): The size of each chunk to download in bytes. Defaults to 8192.
        rich (bool, optional): Whether to use rich progress bar. Defaults to False.
        extra_kwargs (dict | None, optional): Extra keyword arguments to pass to requests.get(). Defaults to None.

    Returns:
        Path: The path to the downloaded file.
    """
    if not isinstance(save_path, Path):
        save_path = Path(save_path)
    save_path.parent.mkdir(parents=True, exist_ok=True)

    resp = (session or requests).get(url, stream=True, **(extra_kwargs or {}))

    resp.raise_for_status()

    with save_path.open("wb") as f:
        iterator = resp.iter_content(chunk_size=chunk_size)
        if rich:
            iterator = tqdm.tqdm(
                iterator,
                total=int(resp.headers.get("content-length", 0)),
                unit="B",
                unit_scale=True,
                desc=url.split("/")[-1],
            )
        for chunk in iterator:
            f.write(chunk)

        if rich:
            assert isinstance(iterator, tqdm.tqdm)
            iterator.refresh()
            iterator.close()

    return save_path


def DownloadFileMultiSource(
    urls: list[str],
    save_path: str | Path,
    *,
    session: requests.Session | None = None,
    chunk_size: int = 8192,
):
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
            return DownloadFile(url, save_path, session=session, chunk_size=chunk_size)
        except requests.exceptions.RequestException:
            pass
    raise requests.exceptions.RequestException(
        "Failed to download file from any source."
    )


if __name__ == "__main__":
    # Network Debug Page
    logging.debug("Current system proxy: {}", GetSystemProxy())
