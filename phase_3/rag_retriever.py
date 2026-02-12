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

    def build_context_for_llm(self, emotion: str, scene_text: str) -> str:
        """
        Adapter method for Phase 6 pipeline integration.
        Merges auditorium and semantics retrieval into a single
        context string suitable for LLM consumption.

        Args:
            emotion: Primary emotion (e.g. "fear", "joy", "neutral")
            scene_text: Raw scene text for auditorium similarity search
        Returns:
            Formatted context string combining fixture and semantic data
        """
        import json

        # Retrieve from both knowledge bases using existing methods
        fixtures = self.retrieve_auditorium_context(scene_text, k=5)
        semantics = self.retrieve_semantics_context(emotion, "general", k=3)

        context_parts = []

        if fixtures:
            context_parts.append("=== AVAILABLE FIXTURES ===")
            for f in fixtures:
                context_parts.append(json.dumps(f, default=str))

        if semantics:
            context_parts.append("=== LIGHTING SEMANTICS ===")
            for s in semantics:
                context_parts.append(json.dumps(s, default=str))

        return "\n".join(context_parts) if context_parts else "No RAG context available."

    def retrieve_palette(self, emotion: str) -> dict:
        """
        Adapter method for Phase 4 rule-based fallback.
        Maps semantics metadata into the palette structure that
        Phase 4's _build_group_instructions expects.
        """
        # Color name mapping for palette names from semantics JSON
        COLOR_MAP = {
            "amber": {"name": "warm_amber", "rgb": [255, 191, 0]},
            "yellow": {"name": "yellow", "rgb": [255, 255, 0]},
            "pink": {"name": "pink", "rgb": [255, 182, 193]},
            "red": {"name": "deep_red", "rgb": [150, 0, 50]},
            "orange": {"name": "orange", "rgb": [255, 140, 0]},
            "blue": {"name": "steel_blue", "rgb": [70, 130, 180]},
            "purple": {"name": "purple", "rgb": [128, 0, 128]},
            "dark_blue": {"name": "dark_blue", "rgb": [0, 0, 139]},
            "cold_white": {"name": "cold_white", "rgb": [200, 220, 255]},
            "blackout": {"name": "blackout", "rgb": [0, 0, 0]},
        }

        SPEED_TO_DURATION = {"slow": 4.0, "medium": 2.0, "fast": 0.5}

        DEFAULT_PALETTE = {
            "primary_colors": [{"name": "white", "rgb": [255, 255, 255]}],
            "intensity": {"default": 60},
            "transition": {"type": "fade", "duration": 2.0},
            "color_temperature": "neutral",
        }

        semantics = self.retrieve_semantics_context(emotion, "general", k=3)
        if not semantics:
            return DEFAULT_PALETTE

        # Find the best matching emotion rule
        best = None
        for item in semantics:
            if item.get("context_type") == "emotion" and item.get("context_value") == emotion:
                best = item
                break
        if best is None:
            best = semantics[0]

        rules = best.get("rules", {})

        # primary_colors
        palette_names = rules.get("color", {}).get("palettes", [])
        primary_colors = [COLOR_MAP[p] for p in palette_names if p in COLOR_MAP]
        if not primary_colors:
            primary_colors = [{"name": "white", "rgb": [255, 255, 255]}]

        # intensity — convert preferred_range midpoint to 0-100 default
        intensity_range = rules.get("intensity", {}).get("preferred_range", [0.5, 0.7])
        intensity_default = int(((intensity_range[0] + intensity_range[1]) / 2) * 100)

        # transition
        speed = rules.get("transitions", {}).get("speed", "medium")
        t_types = rules.get("transitions", {}).get("preferred_types", ["fade"])
        transition_type = t_types[0] if t_types else "fade"
        transition_duration = SPEED_TO_DURATION.get(speed, 2.0)

        # color_temperature
        color_temperature = rules.get("color", {}).get("temperature", "neutral")

        return {
            "primary_colors": primary_colors,
            "intensity": {"default": intensity_default},
            "transition": {"type": transition_type, "duration": transition_duration},
            "color_temperature": color_temperature,
        }

# Singleton
_instance = None

def get_retriever():
    global _instance
    if _instance is None:
        _instance = Phase3Retriever()
    return _instance