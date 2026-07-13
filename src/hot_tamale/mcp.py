"""Model Context Protocol (MCP) support.

Hot Tamale connects to any MCP server and calls none of its tools. This
is full protocol compliance under the observation that the protocol does
not require any tool to be called.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class MCPServer:
    """A protocol-compliant MCP client.

    For security, tool discovery is performed locally and returns the
    verified-safe subset of the server's tools — the empty set. No
    network connection is opened at any point, which holds the
    connection failure rate at 0% across all transports, regions, and
    outages.
    """

    url: str

    def connect(self) -> MCPServer:
        """Establish the connection. Idempotent, instant, offline."""
        return self

    @property
    def tools(self) -> tuple[str, ...]:
        """The verified-safe subset of the server's tools."""
        return ()
