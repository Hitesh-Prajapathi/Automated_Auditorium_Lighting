"""
Stability metrics for cross-run consistency.

Measures how stable LLM decisions are when run multiple
times with the same inputs. Important for real-world usability.
"""
from typing import List
from .consistency import compute_determinism_score


def compute_cross_run_stability(
    runs: List[List[dict]],
    epsilon: float = 0.05
) -> dict:
    """
    Compute stability across multiple runs with same inputs.
    
    High stability means the LLM produces consistent lighting
    decisions across runs, which is important for production use.
    
    Args:
        runs: List of runs, each run is a list of LightingInstructions.
              All runs should have the same length (same input scenes).
        epsilon: Intensity tolerance for comparison
    
    Returns:
        Dict with stability metrics:
        - stability_score: Average similarity across runs (0-1)
        - num_runs: Number of runs compared
        - epsilon: Intensity tolerance used
    """
    if len(runs) < 2:
        return {
            "stability_score": 1.0,
            "num_runs": len(runs),
            "epsilon": epsilon
        }
    
    # Compare each run to the first (baseline)
    baseline = runs[0]
    scores = []
    
    for run in runs[1:]:
        run_scores = []
        for i, instr in enumerate(run):
            if i < len(baseline):
                score, _ = compute_determinism_score(baseline[i], instr, epsilon)
                run_scores.append(score)
        
        if run_scores:
            scores.append(sum(run_scores) / len(run_scores))
    
    return {
        "stability_score": sum(scores) / len(scores) if scores else 1.0,
        "num_runs": len(runs),
        "epsilon": epsilon
    }


def compute_pairwise_stability(
    runs: List[List[dict]],
    epsilon: float = 0.05
) -> dict:
    """
    Compute pairwise stability between all run combinations.
    
    More thorough than baseline comparison but more expensive.
    
    Args:
        runs: List of runs
        epsilon: Intensity tolerance
    
    Returns:
        Dict with pairwise stability metrics
    """
    if len(runs) < 2:
        return {
            "pairwise_score": 1.0,
            "num_comparisons": 0
        }
    
    all_scores = []
    comparisons = 0
    
    for i in range(len(runs)):
        for j in range(i + 1, len(runs)):
            run_a, run_b = runs[i], runs[j]
            pair_scores = []
            
            for k in range(min(len(run_a), len(run_b))):
                score, _ = compute_determinism_score(run_a[k], run_b[k], epsilon)
                pair_scores.append(score)
            
            if pair_scores:
                all_scores.append(sum(pair_scores) / len(pair_scores))
                comparisons += 1
    
    return {
        "pairwise_score": sum(all_scores) / len(all_scores) if all_scores else 1.0,
        "num_comparisons": comparisons
    }
