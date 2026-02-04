"""
Phase 3 RAG Retriever (LangChain + FAISS)
Exposes the Auditorium and Semantics knowledge bases to the rest of the system.
"""

import os
from typing import Dict, List, Any
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

# Define paths relative to this file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RAG_DIR = os.path.join(BASE_DIR, "rag")
AUDITORIUM_INDEX = os.path.join(RAG_DIR, "auditorium")
SEMANTICS_INDEX = os.path.join(RAG_DIR, "lighting_semantics")

class Phase3Retriever:
    """
    The official interface for Phase 3.
    Use this class to query physical hardware or design rules.
    """
    
    def __init__(self):
        print("📥 Initializing Phase 3 RAG Engine...")
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        self.auditorium_db = self._load_index(AUDITORIUM_INDEX)
        self.semantics_db = self._load_index(SEMANTICS_INDEX)
        
    def _load_index(self, path: str):
        try:
            if os.path.exists(path):
                return FAISS.load_local(path, self.embeddings, allow_dangerous_deserialization=True)
            else:
                print(f"⚠️ Warning: Index not found at {path}")
                return None
        except Exception as e:
            print(f"❌ Error loading index {path}: {e}")
            return None

    def retrieve_auditorium_context(self, query: str, k: int = 5) -> List[Dict]:
        """
        Query the physical hardware available.
        Args:
            query: Natural language description (e.g. "spotlight for podium")
            k: Number of fixtures to trigger
        Returns:
            List of fixture metadata files
        """
        if not self.auditorium_db:
            return []
            
        docs = self.auditorium_db.similarity_search(query, k=k)
        return [doc.metadata for doc in docs]

    def retrieve_semantics_context(self, emotion: str, script_type: str, k: int = 3) -> List[Dict]:
        """
        Query the design rules.
        Args:
            emotion: "fear", "joy", etc.
            script_type: "drama", "formal", etc.
        Returns:
            List of design rule metadata files
        """
        if not self.semantics_db:
            return []
            
        query = f"{emotion} {script_type}"
        docs = self.semantics_db.similarity_search(query, k=k)
        return [doc.metadata for doc in docs]

# Singleton
_instance = None

def get_retriever():
    global _instance
    if _instance is None:
        _instance = Phase3Retriever()
    return _instance