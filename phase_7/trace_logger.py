"""
Trace logger for Phase 7.
Observes and logs execution traces WITHOUT influencing execution.

IMPORTANT: This logger is PASSIVE — it does not:
- Call Phase 4 functions
- Invoke LLM
- Modify lighting intent
"""
import json
import hashlib
from datetime import datetime
from uuid import uuid4
from pathlib import Path
from typing import Optional, List

from .schemas import TraceEntry, TraceLog, RAGContextRef


class TraceLogger:
    """
    Logs execution traces for reproducibility and metrics.
    
    This logger observes pre-generated outputs and creates trace
    records for analysis. It NEVER generates or modifies data.
    
    Usage:
        logger = TraceLogger(output_dir=Path("traces/"), seed=42)
        
        # Load pre-generated data (not generated here!)
        with open("data/lighting_cues/scene_001.json") as f:
            instruction = json.load(f)
        
        logger.log_decision(scene, instruction)
        logger.save()
    """
    
    def __init__(self, output_dir: Path, seed: Optional[int] = None):
        """
        Initialize trace logger.
        
        Args:
            output_dir: Directory to save trace logs
            seed: Optional seed for reproducibility tracking
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.run_id = uuid4()
        self.seed = seed
        self.entries: List[TraceEntry] = []
    
    @staticmethod
    def compute_hash(data: dict) -> str:
        """
        Compute deterministic hash of JSON-serializable data.
        
        Uses sorted keys to ensure consistent hashing regardless
        of dictionary key ordering.
        """
        json_str = json.dumps(data, sort_keys=True, default=str)
        return hashlib.sha256(json_str.encode()).hexdigest()[:16]
    
    def log_decision(
        self,
        scene: dict,
        lighting_instruction: dict,
        rag_context_ids: Optional[List[dict]] = None
    ) -> TraceEntry:
        """
        Log a single lighting decision.
        
        IMPORTANT: Data must be loaded from files, NOT generated.
        
        Args:
            scene: Scene JSON (loaded from file, NOT generated)
            lighting_instruction: LightingInstruction JSON (loaded from file)
            rag_context_ids: Opaque identifiers only (document_id, chunk_id)
                             NO content, embeddings, or scores!
        
        Returns:
            TraceEntry object
        """
        refs = []
        if rag_context_ids:
            refs = [RAGContextRef(**ctx) for ctx in rag_context_ids]
        
        entry = TraceEntry(
            run_id=self.run_id,
            seed=self.seed,
            scene_id=scene.get("scene_id", "unknown"),
            timestamp=datetime.now().timestamp(),
            input_hash=self.compute_hash(scene),
            output_hash=self.compute_hash(lighting_instruction),
            rag_context_ids=refs
        )
        self.entries.append(entry)
        return entry
    
    def save(self) -> Path:
        """
        Save trace log to JSON file.
        
        Returns:
            Path to saved trace file
        """
        trace_log = TraceLog(
            run_id=self.run_id,
            created_at=datetime.now().isoformat(),
            entries=self.entries
        )
        output_file = self.output_dir / f"trace_{self.run_id}.json"
        with open(output_file, 'w') as f:
            json.dump(trace_log.model_dump(mode='json'), f, indent=2)
        return output_file
    
    def get_entry_count(self) -> int:
        """Return number of logged entries."""
        return len(self.entries)
    
    def clear(self) -> None:
        """Clear all entries (for testing purposes)."""
        self.entries = []
