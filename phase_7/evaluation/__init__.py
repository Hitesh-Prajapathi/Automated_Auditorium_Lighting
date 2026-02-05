"""
Phase 7 Evaluation Module

Contains metrics for:
- Consistency (Jaccard + drift)
- Coverage (group utilization)
- Stability (cross-run consistency)
"""
from .consistency import (
    compute_jaccard_similarity,
    compute_determinism_score,
    compute_drift_score,
    extract_group_ids,
    INTENSITY_EPSILON
)
from .coverage import (
    compute_group_coverage,
    compute_parameter_diversity
)
from .stability import (
    compute_cross_run_stability
)

__all__ = [
    'compute_jaccard_similarity',
    'compute_determinism_score',
    'compute_drift_score',
    'extract_group_ids',
    'compute_group_coverage',
    'compute_parameter_diversity',
    'compute_cross_run_stability',
    'INTENSITY_EPSILON'
]
