"""
Phase 6: Orchestration & Pipeline Control

The ORCHESTRATION SPINE of the Automated Auditorium Lighting system.
Controls execution order, enables/disables phases, passes data between phases.

Phase 6 is orchestration-only and does not influence system decisions.
"""

from .config_models import (
    PipelineConfig,
    PhaseStatus,
    PhaseResult,
    PipelineResult,
    SceneRef,
)

from .errors import (
    Phase6Error,
    HardFailureError,
    NonFatalError,
    ConfigurationError,
    ContractViolationError,
    PhaseNotImplementedError,
)

from .state_tracker import (
    StateTracker,
    ExecutionState,
)

from .pipeline_runner import PipelineRunner

from .batch_executor import BatchExecutor

__all__ = [
    # Configuration
    "PipelineConfig",
    "PhaseStatus",
    "PhaseResult",
    "PipelineResult",
    "SceneRef",
    
    # Errors
    "Phase6Error",
    "HardFailureError",
    "NonFatalError",
    "ConfigurationError",
    "ContractViolationError",
    "PhaseNotImplementedError",
    
    # State
    "StateTracker",
    "ExecutionState",
    
    # Runners
    "PipelineRunner",
    "BatchExecutor",
]
