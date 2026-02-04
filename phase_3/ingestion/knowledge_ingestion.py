"""
Knowledge Ingestion Script (Phase 3)
Builds FAISS vector stores for Auditorium Knowledge and Lighting Semantics.
"""

import json
import os
from typing import List, Dict
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document

# Paths
# Relative to project root if running as module, or relative to this file
BASE_DIR = "phase_3"
DATA_DIR = os.path.join(BASE_DIR, "knowledge")
SCHEMA_DIR = os.path.join(BASE_DIR, "schemas")
RAG_DIR = os.path.join(BASE_DIR, "rag")

AUDITORIUM_SOURCE = os.path.join(DATA_DIR, "auditorium", "fixtures.json")
SEMANTICS_SOURCE = os.path.join(DATA_DIR, "semantics", "baseline_semantics.json")

AUDITORIUM_INDEX = os.path.join(RAG_DIR, "auditorium")
SEMANTICS_INDEX = os.path.join(RAG_DIR, "lighting_semantics")

def load_json(filepath: str) -> List[Dict]:
    with open(filepath, 'r') as f:
        return json.load(f)

def create_fixture_documents(fixtures: List[Dict]) -> List[Document]:
    """Convert fixture JSON into LangChain Documents"""
    docs = []
    for fixture in fixtures:
        # Create a descriptive text for embedding
        # "Moving Head at FOH with RGB, Zoom capabilities"
        caps = ", ".join(fixture.get("capabilities", []))
        pos = fixture.get("position", {})
        pos_str = f"x:{pos.get('x')} y:{pos.get('y')} z:{pos.get('z')}"
        
        content = (
            f"Fixture: {fixture.get('fixture_type')} "
            f"ID: {fixture.get('fixture_id')} "
            f"Group: {fixture.get('group_id')} "
            f"Capabilities: {caps} "
            f"Position: {pos_str}"
        )
        
        # Metadata preserves the structured data for Phase 4
        metadata = fixture
        docs.append(Document(page_content=content, metadata=metadata))
    return docs

def create_semantics_documents(semantics: List[Dict]) -> List[Document]:
    """Convert semantics JSON into LangChain Documents"""
    docs = []
    for rule in semantics:
        # Create descriptive text for embedding
        # "Design rule for Fear emotion: Low intensity, cool colors"
        context_type = rule.get("context_type")
        context_value = rule.get("context_value")
        comment = rule.get("_comment", "")
        
        content = (
            f"Context: {context_type} = {context_value}. "
            f"Description: {comment}"
        )
        
        metadata = rule
        docs.append(Document(page_content=content, metadata=metadata))
    return docs

def main():
    print("🚀 Starting Phase 3 Knowledge Ingestion...")
    
    # Initialize Embeddings (Local/Free)
    print("📥 Loading Embedding Model (HuggingFace)...")
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    # 1. Process Auditorium Knowledge
    if os.path.exists(AUDITORIUM_SOURCE):
        print(f"💡 Processing Fixtures from {AUDITORIUM_SOURCE}...")
        fixtures = load_json(AUDITORIUM_SOURCE)
        fixture_docs = create_fixture_documents(fixtures)
        
        print(f"   - Creating Vector Index for {len(fixture_docs)} fixtures...")
        auditorium_db = FAISS.from_documents(fixture_docs, embeddings)
        auditorium_db.save_local(AUDITORIUM_INDEX)
        print("   ✅ Auditorium RAG Index Saved.")
    else:
        print(f"❌ Error: {AUDITORIUM_SOURCE} not found.")

    # 2. Process Lighting Semantics
    if os.path.exists(SEMANTICS_SOURCE):
        print(f"🎨 Processing Semantics from {SEMANTICS_SOURCE}...")
        semantics = load_json(SEMANTICS_SOURCE)
        semantics_docs = create_semantics_documents(semantics)
        
        print(f"   - Creating Vector Index for {len(semantics_docs)} rules...")
        semantics_db = FAISS.from_documents(semantics_docs, embeddings)
        semantics_db.save_local(SEMANTICS_INDEX)
        print("   ✅ Semantics RAG Index Saved.")
    else:
        print(f"❌ Error: {SEMANTICS_SOURCE} not found.")

    print("\n🎉 Phase 3 Ingestion Complete!")
    print(f"   - Auditorium Index: {AUDITORIUM_INDEX}")
    print(f"   - Semantics Index: {SEMANTICS_INDEX}")

if __name__ == "__main__":
    main()
