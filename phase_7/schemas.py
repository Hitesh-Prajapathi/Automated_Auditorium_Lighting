"""
Internal trace schema for Phase 7.
NOT a contract — used for internal validation only.

This module defines pydantic models for:
- Trace entries (individual logging records)
- RAG context references (opaque identifiers only)
- Complete trace logs
"""
from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from datetime import datetime


class RAGContextRef(BaseModel):
    """
    Opaque RAG reference — NO content, NO embeddings, NO scores.
    
    Only document_id and chunk_id are allowed for traceability.
    """
    document_id: str
    chunk_id: Optional[str] = None


class TraceEntry(BaseModel):
    """
    Single trace entry for a lighting decision.
    
    Captures input/output hashes for reproducibility
    without storing actual content.
    """
    run_id: UUID
    seed: Optional[int] = None
    scene_id: str
    timestamp: float
    input_hash: str                              # Hash of input scene
    output_hash: str                             # Hash of lighting instruction
    rag_context_ids: List[RAGContextRef] = []    # Opaque refs only
    metadata: Optional[dict] = None


class TraceLog(BaseModel):
    """Collection of trace entries for a complete run."""
    run_id: UUID
    created_at: str
    entries: List[TraceEntry]
