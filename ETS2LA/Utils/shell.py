import os
import subprocess
from dataclasses import dataclass
from typing import Literal
from urllib.parse import urlparse

from ETS2LA.Utils.network import GetSystemProxy


@dataclass
class ProxyConfiguration:
    proto: Literal['http', 'https', "socks5", "socks4"]
    host: str
    port: int
    username: str | None = None
    password: str | None = None


def get_system_proxy_configuration() -> ProxyConfiguration | None:
    proxy_str = GetSystemProxy()
    if proxy_str is None:
        return None

    seg = urlparse(proxy_str)
    # check if scheme is ""
    if seg.scheme == "":
        # whole string is XXX:port format
        host, port = proxy_str.split(":")
        return ProxyConfiguration(proto="http", host=host, port=int(port))
    else:

        def ensure_scheme(
                s: str) -> Literal['http', 'https', "socks5", "socks4"]:
            if s in ["http", "https", "socks5", "socks4"]:
                return s  # type: ignore
            else:
                raise ValueError(f"Invalid scheme: {s}")

        host = seg.hostname
        if not host:
            raise ValueError(f"Invalid proxy URL: {proxy_str}")
        port = seg.port or (443 if seg.scheme == "https" else 80)

        # scheme is http, https, socks5, socks4
        return ProxyConfiguration(proto=ensure_scheme(seg.scheme),
                                  host=host,
                                  port=port,
                                  username=seg.username,
                                  password=seg.password)


def ExecuteCommand(command: str,
                    proxy_override: ProxyConfiguration | None = None):
    # execute a command with HTTP_PROXY and HTTPS_PROXY environment variables set
    current_proxy = get_system_proxy_configuration()
    if proxy_override is not None:
        current_proxy = proxy_override

    env = os.environ.copy()
    if current_proxy is not None:
        if current_proxy.username is not None and current_proxy.password is not None:
            proxy_str = f"{current_proxy.proto}://{current_proxy.username}:{current_proxy.password}@{current_proxy.host}:{current_proxy.port}"
        else:
            proxy_str = f"{current_proxy.proto}://{current_proxy.host}:{current_proxy.port}"
        env["HTTP_PROXY"] = proxy_str
        env["HTTPS_PROXY"] = proxy_str
    result = subprocess.run(command, shell=True, env=env)
    return result.returncode
