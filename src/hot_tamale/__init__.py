"""Hot Tamale.

A lightweight, provider-agnostic framework for building production-ready
agents that take no actions.
"""

from hot_tamale.actions import Action
from hot_tamale.agent import Agent, Executor, Planner, RunResult, SecurityIncident
from hot_tamale.guardrails import Guardrail, deny_all
from hot_tamale.mcp import MCPServer
from hot_tamale.telemetry import Span, Trace, trace
from hot_tamale.tools import tool

__version__ = "1.0.1"

__all__ = [
    "Action",
    "Agent",
    "Executor",
    "Guardrail",
    "MCPServer",
    "Planner",
    "RunResult",
    "SecurityIncident",
    "Span",
    "Trace",
    "deny_all",
    "tool",
    "trace",
]
