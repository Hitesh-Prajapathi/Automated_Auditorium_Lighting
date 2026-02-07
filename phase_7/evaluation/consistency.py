"""
Consistency metrics for evaluating LLM decision stability.

Metrics defined here:
- Jaccard similarity (group overlap)
- Determinism score (structural matching)
- Drift score (sequence stability)

IMPORTANT: Determinism is defined STRUCTURALLY, not bytewise:
- Same group_ids selected
- Same transition types
- Intensity within ε = ±0.05
"""
from typing import List, Tuple, Set

# Tolerance for intensity comparison
INTENSITY_EPSILON = 0.05


def compute_jaccard_similarity(set_a: Set, set_b: Set) -> float:
    """
    Compute Jaccard similarity between two sets.
    
    J(A, B) = |A ∩ B| / |A ∪ B|
    
    Args:
        set_a: First set
        set_b: Second set
    
    Returns:
        Similarity score between 0.0 and 1.0
    """
    if not set_a and not set_b:
        return 1.0
    intersection = len(set_a & set_b)
    union = len(set_a | set_b)
    return intersection / union if union > 0 else 0.0


def compute_determinism_score(
    instruction_a: dict,
    instruction_b: dict,
    epsilon: float = INTENSITY_EPSILON
) -> Tuple[float, dict]:
    """
    Compute structural determinism between two LightingInstructions.
    
    Determinism is defined STRUCTURALLY (not bytewise):
    - Same group_ids selected
    - Same transition types
    - Intensity within ε tolerance
    
    This definition is fair, reproducible, and defensible in papers.
    
    Args:
        instruction_a: First LightingInstruction
        instruction_b: Second LightingInstruction
        epsilon: Intensity tolerance (default ±0.05)
    
    Returns:
        Tuple of (score 0-1, breakdown dict)
    """
    groups_a = {g["group_id"]: g for g in instruction_a.get("groups", []) if "group_id" in g}
    groups_b = {g["group_id"]: g for g in instruction_b.get("groups", []) if "group_id" in g}
    
    # 1. Group ID match (Jaccard)
    ids_a, ids_b = set(groups_a.keys()), set(groups_b.keys())
    group_match = compute_jaccard_similarity(ids_a, ids_b)
    
    # 2. Parameter match for common groups
    common_ids = ids_a & ids_b
    param_matches = []
    intensity_matches = []
    transition_matches = []
    
    for gid in common_ids:
        ga, gb = groups_a[gid], groups_b[gid]
        
        # Intensity check (within epsilon)
        int_a = ga.get("parameters", {}).get("intensity", 0)
        int_b = gb.get("parameters", {}).get("intensity", 0)
        intensity_ok = abs(int_a - int_b) <= epsilon
        intensity_matches.append(intensity_ok)
        
        # Transition type check
        trans_a = (ga.get("transition") or {}).get("type")
        trans_b = (gb.get("transition") or {}).get("type")
        transition_ok = trans_a == trans_b
        transition_matches.append(transition_ok)
        
        param_matches.append(intensity_ok and transition_ok)
    
    if param_matches:
        param_score = sum(param_matches) / len(param_matches)
    else:
        # If no common groups, check if both are empty (perfect match) or disjoint (mismatch)
        if not ids_a and not ids_b:
            param_score = 1.0
        else:
            param_score = 0.0
    
    # Combined score (average of group match and parameter match)
    score = (group_match + param_score) / 2
    
    return score, {
        "group_match": group_match,
        "param_score": param_score,
        "intensity_epsilon": epsilon,
        "common_groups": len(common_ids),
        "intensity_matches": sum(intensity_matches),
        "transition_matches": sum(transition_matches)
    }


def compute_drift_score(instructions: List[dict]) -> float:
    """
    Compute drift across a sequence of instructions.
    
    Drift measures how much lighting decisions change across
    consecutive scenes. Lower is better (less drift = more stable).
    
    Args:
        instructions: List of LightingInstruction dicts in order
    
    Returns:
        Average drift score (0.0 = no drift, 1.0 = complete change)
    """
    if len(instructions) < 2:
        return 0.0
    
    drifts = []
    for i in range(1, len(instructions)):
        score, _ = compute_determinism_score(instructions[i-1], instructions[i])
        drifts.append(1.0 - score)  # Drift = 1 - similarity
    
    return sum(drifts) / len(drifts)
