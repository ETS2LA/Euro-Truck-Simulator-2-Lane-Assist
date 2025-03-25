import logging
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
    try:
        proxy_str = GetSystemProxy()
        if proxy_str is None:
            return None

        seg = urlparse(proxy_str)
        # check if scheme is ""
        if seg.scheme == "":
            sections = proxy_str.split(";")
            for section in sections:
                if "=" in section:
                    key, section = section.split("=")
                    if key not in ["http", "https"]: continue
                
                try:
                    host, port = section.split(":")
                except ValueError:
                    continue
                if not host: continue
                if not port.isdigit(): continue
                # use the first available
                return ProxyConfiguration(proto="http", host=host, port=int(port))
            return None
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
    except Exception as e:
        logging.error(f"Failed to get system proxy configuration: {e}")
        return None


def ExecuteCommand(command: str,
                   proxy_override: ProxyConfiguration | None = None,
                   silent: bool = False) -> int:

    current_proxy = get_system_proxy_configuration()
    env = os.environ.copy()
    if proxy_override is not None:
        current_proxy = proxy_override

        if current_proxy is not None:
            if current_proxy.username is not None and current_proxy.password is not None:
                proxy_str = f"{current_proxy.proto}://{current_proxy.username}:{current_proxy.password}@{current_proxy.host}:{current_proxy.port}"
            else:
                proxy_str = f"{current_proxy.proto}://{current_proxy.host}:{current_proxy.port}"
            env["HTTP_PROXY"] = proxy_str
            env["HTTPS_PROXY"] = proxy_str
    
    if silent:
        result = subprocess.run(command, shell=True, env=env, capture_output=True)
    else:
        result = subprocess.run(command, shell=True, env=env)
    
    return result.returncode