"""
Phase 7 — Evaluation & Metrics

Observational logging and metrics for research support.
This phase is FULLY REMOVABLE without affecting system execution.

IMPORTANT: Phase 7 must NEVER:
- Import from phase_4 or other phases
- Call LLM APIs
- Modify lighting intent
- Influence execution
"""
from .trace_logger import TraceLogger
from .metrics import MetricsEngine
from .schemas import TraceEntry, TraceLog, RAGContextRef

__all__ = [
    'TraceLogger',
    'MetricsEngine',
    'TraceEntry',
    'TraceLog',
    'RAGContextRef'
]
