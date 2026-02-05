"""
Unified metrics computation engine for Phase 7.

<<<<<<< HEAD
Provides a single interface to compute all research-grade metrics:
- Consistency (determinism, drift)
- Coverage (group utilization)
- Stability (cross-run)

=======
>>>>>>> phase_7
IMPORTANT: This engine is OBSERVATIONAL ONLY.
It does NOT influence execution.
"""
import json
from pathlib import Path
from typing import List, Optional, Set

from .evaluation.consistency import (
    compute_determinism_score,
    compute_drift_score,
    compute_jaccard_similarity,
    extract_group_ids
)
from .evaluation.coverage import (
    compute_group_coverage,
    compute_parameter_diversity
)
from .evaluation.stability import (
    compute_cross_run_stability
)


class MetricsEngine:
    """
    Computes research-grade metrics for lighting decisions.
    
    IMPORTANT: This engine is OBSERVATIONAL ONLY.
<<<<<<< HEAD
    It does NOT influence execution or modify lighting intent.
    
    Usage:
        engine = MetricsEngine(available_groups={"G1", "G2", "G3"})
        
        # Evaluate single instruction
        result = engine.evaluate_instruction(instruction)
        
        # Compare two instructions
        comparison = engine.evaluate_pair(instr_a, instr_b)
    """
    
    def __init__(self, available_groups: Optional[Set[str]] = None):
        """
        Initialize metrics engine.
        
        Args:
            available_groups: Set of all available group IDs in the auditorium.
                             Used for coverage calculation.
        """
        self.available_groups = available_groups or set()
    
    def evaluate_instruction(self, instruction: dict) -> dict:
        """
        Compute all metrics for a single instruction.
        
        Args:
            instruction: LightingInstruction dict
        
        Returns:
            Dict with coverage and diversity metrics
        """
=======
    """
    
    def __init__(self, available_groups: Optional[Set[str]] = None):
        self.available_groups = available_groups or set()
    
    def evaluate_instruction(self, instruction: dict) -> dict:
        """Compute all metrics for a single instruction."""
>>>>>>> phase_7
        return {
            "coverage": compute_group_coverage(instruction, self.available_groups),
            "diversity": compute_parameter_diversity(instruction)
        }
    
    def evaluate_pair(
        self,
        instruction_a: dict,
        instruction_b: dict,
        epsilon: float = 0.05
    ) -> dict:
<<<<<<< HEAD
        """
        Compare two instructions for consistency.
        
        Args:
            instruction_a: First LightingInstruction
            instruction_b: Second LightingInstruction
            epsilon: Intensity tolerance
        
        Returns:
            Dict with determinism score and breakdown
        """
=======
        """Compare two instructions for consistency."""
>>>>>>> phase_7
        score, breakdown = compute_determinism_score(
            instruction_a, instruction_b, epsilon
        )
        return {
            "determinism_score": score,
            "breakdown": breakdown,
            "jaccard_groups": compute_jaccard_similarity(
                extract_group_ids(instruction_a),
                extract_group_ids(instruction_b)
            )
        }
    
    def evaluate_sequence(self, instructions: List[dict]) -> dict:
<<<<<<< HEAD
        """
        Evaluate a sequence of instructions for drift.
        
        Args:
            instructions: List of LightingInstruction dicts
        
        Returns:
            Dict with drift score and count
        """
=======
        """Evaluate a sequence of instructions for drift."""
>>>>>>> phase_7
        return {
            "drift_score": compute_drift_score(instructions),
            "num_instructions": len(instructions)
        }
    
    def evaluate_runs(
        self,
        runs: List[List[dict]],
        epsilon: float = 0.05
    ) -> dict:
<<<<<<< HEAD
        """
        Evaluate cross-run stability.
        
        Args:
            runs: List of runs, each containing LightingInstructions
            epsilon: Intensity tolerance
        
        Returns:
            Dict with stability metrics
        """
=======
        """Evaluate cross-run stability."""
>>>>>>> phase_7
        return compute_cross_run_stability(runs, epsilon)
    
    def generate_report(
        self,
        instructions: List[dict],
        runs: Optional[List[List[dict]]] = None
    ) -> dict:
<<<<<<< HEAD
        """
        Generate comprehensive metrics report.
        
        Args:
            instructions: Primary run instructions
            runs: Optional additional runs for stability
        
        Returns:
            Complete metrics report
        """
=======
        """Generate comprehensive metrics report."""
>>>>>>> phase_7
        report = {
            "summary": {
                "num_instructions": len(instructions),
                "available_groups": len(self.available_groups)
            },
            "sequence_metrics": self.evaluate_sequence(instructions),
            "instruction_metrics": []
        }
        
<<<<<<< HEAD
        # Per-instruction metrics
=======
>>>>>>> phase_7
        for i, instr in enumerate(instructions):
            report["instruction_metrics"].append({
                "index": i,
                "scene_id": instr.get("scene_id"),
                **self.evaluate_instruction(instr)
            })
        
<<<<<<< HEAD
        # Stability if multiple runs provided
=======
>>>>>>> phase_7
        if runs and len(runs) > 1:
            report["stability_metrics"] = self.evaluate_runs(runs)
        
        return report
