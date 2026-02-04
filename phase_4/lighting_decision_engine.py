"""
Lighting Decision Engine (Phase 4)

Converts scene emotions → lighting INTENT (not execution details).

Key design principles:
- Outputs groups, not individual fixtures
- Uses semantic parameters (intensity, color, focus_area)
- NO DMX channels here — that's adapter/Phase 8 responsibility
- LangChain for prompt formatting and structured output
- NO direct dependency on Phase 3 schemas (uses interface)
"""

import os
from typing import Dict, List, Any, Optional, Protocol
from enum import Enum
from pydantic import BaseModel, Field

# Import config
from config import (
    LLM_MODEL,
    LLM_TEMPERATURE,
    LLM_MAX_TOKENS,
    LANGCHAIN_VERBOSE,
    FALLBACK_TO_RULES
)

# Try to import LangChain libraries
try:
    from langchain_openai import ChatOpenAI
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.output_parsers import PydanticOutputParser
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    print("Warning: langchain-openai not installed. Using rule-based generation only.")


# =============================================================================
# RETRIEVER PROTOCOL (Interface for Phase 3 — we don't own Phase 3)
# =============================================================================

class RetrieverProtocol(Protocol):
    """Protocol for knowledge retriever — Phase 3 implements this"""
    def retrieve_palette(self, emotion: str) -> Dict: ...
    def build_context_for_llm(self, emotion: str, scene_text: str) -> str: ...


class SimpleRetriever:
    """Fallback retriever when Phase 3 is not available"""
    
    DEFAULT_PALETTES = {
        "joy": {
            "primary_colors": [{"name": "warm_amber", "rgb": [255, 191, 0]}],
            "intensity": {"default": 80},
            "transition": {"type": "fade", "duration": 2.0},
            "color_temperature": "warm"
        },
        "sadness": {
            "primary_colors": [{"name": "steel_blue", "rgb": [70, 130, 180]}],
            "intensity": {"default": 40},
            "transition": {"type": "fade", "duration": 4.0},
            "color_temperature": "cool"
        },
        "fear": {
            "primary_colors": [{"name": "dark_red", "rgb": [139, 0, 0]}],
            "intensity": {"default": 25},
            "transition": {"type": "flicker", "duration": 1.0},
            "effects": ["flicker"],
            "color_temperature": "cool"
        },
        "anger": {
            "primary_colors": [{"name": "deep_red", "rgb": [150, 0, 50]}],
            "intensity": {"default": 90},
            "transition": {"type": "snap", "duration": 0.5},
            "color_temperature": "warm"
        },
        "neutral": {
            "primary_colors": [{"name": "white", "rgb": [255, 255, 255]}],
            "intensity": {"default": 60},
            "transition": {"type": "fade", "duration": 2.0},
            "color_temperature": "neutral"
        }
    }
    
    def retrieve_palette(self, emotion: str) -> Dict:
        return self.DEFAULT_PALETTES.get(emotion.lower(), self.DEFAULT_PALETTES["neutral"])
    
    def build_context_for_llm(self, emotion: str, scene_text: str) -> str:
        palette = self.retrieve_palette(emotion)
        return f"Emotion: {emotion}, Suggested colors: {palette.get('primary_colors', [])}"


def get_retriever() -> RetrieverProtocol:
    """
    Get the knowledge retriever.
    Attempts to use Phase 3 retriever if available, otherwise uses simple fallback.
    """
    try:
        from pipeline.rag_retriever import get_retriever as get_rag_retriever
        return get_rag_retriever()
    except ImportError:
        print("Phase 3 retriever not available. Using simple fallback.")
        return SimpleRetriever()


# =============================================================================
# ENUMS
# =============================================================================

class TransitionType(str, Enum):
    """Supported transition types"""
    FADE = "fade"
    SNAP = "snap"
    SMOOTH = "smooth"
    PULSE = "pulse"
    FLICKER = "flicker"
    STROBE = "strobe"
    CUT = "cut"
    CROSSFADE = "crossfade"


class FocusArea(str, Enum):
    """Stage focus areas"""
    CENTER_STAGE = "center_stage"
    STAGE_LEFT = "stage_left"
    STAGE_RIGHT = "stage_right"
    UPSTAGE = "upstage"
    DOWNSTAGE = "downstage"
    FULL_STAGE = "full_stage"
    AUDIENCE = "audience"


# =============================================================================
# PYDANTIC OUTPUT MODELS (Architecturally Correct)
# =============================================================================

class Transition(BaseModel):
    """Transition specification"""
    type: TransitionType = Field(default=TransitionType.FADE)
    duration_seconds: float = Field(default=2.0, ge=0.0, le=30.0)


class LightingParameters(BaseModel):
    """Semantic lighting parameters — NO DMX here"""
    intensity: float = Field(
        description="Intensity level 0.0-100.0 percent",
        ge=0.0, le=100.0
    )
    color: str = Field(
        description="Color name or hex code, e.g. 'warm_amber', 'deep_red', '#FF5500'"
    )
    focus_area: Optional[FocusArea] = Field(
        default=None,
        description="Where light is focused on stage"
    )
    color_temperature: Optional[str] = Field(
        default=None,
        description="warm, neutral, cool"
    )


class GroupLightingInstruction(BaseModel):
    """Lighting instruction for a fixture GROUP (not individual fixtures)"""
    group_id: str = Field(
        description="Group identifier: 'front_wash', 'back_light', 'side_fill', 'specials', 'ambient'"
    )
    parameters: LightingParameters = Field(
        description="Semantic lighting parameters"
    )
    transition: Transition = Field(
        default_factory=Transition,
        description="How to transition to this state"
    )


class TimeWindow(BaseModel):
    """Time window for the lighting instruction"""
    start_time: float = Field(ge=0.0)
    end_time: float = Field(ge=0.0)
    
    @property
    def duration(self) -> float:
        return self.end_time - self.start_time


class LightingInstruction(BaseModel):
    """Complete lighting instruction output from Phase 4
    
    This is the contract between LLM Decision Engine and downstream systems.
    Contains INTENT only — no DMX, no fixture IDs.
    """
    scene_id: str = Field(description="Scene identifier from Phase 1")
    emotion: str = Field(description="Detected emotion driving this instruction")
    time_window: TimeWindow = Field(description="When this instruction applies")
    groups: List[GroupLightingInstruction] = Field(
        description="Lighting instructions per group"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Optional metadata (reasoning, debug info). Stripped before Phase 5."
    )


# =============================================================================
# GROUP DEFINITIONS (These map to fixtures in adapter layer)
# =============================================================================

LIGHTING_GROUPS = {
    "front_wash": {
        "description": "Primary audience-facing illumination",
        "typical_fixtures": ["PAR", "fresnel"]
    },
    "back_light": {
        "description": "Separation from background, silhouettes",
        "typical_fixtures": ["PAR", "LED_bar"]
    },
    "side_fill": {
        "description": "Side lighting for depth and dimension",
        "typical_fixtures": ["PAR", "ellipsoidal"]
    },
    "specials": {
        "description": "Focused highlights, spotlights",
        "typical_fixtures": ["moving_head", "followspot"]
    },
    "ambient": {
        "description": "Overall wash, atmosphere",
        "typical_fixtures": ["RGB_wash", "cyclorama"]
    }
}


# =============================================================================
# PROMPT TEMPLATES
# =============================================================================

SYSTEM_PROMPT = """You are a professional lighting designer for theatre.
Your job is to specify lighting INTENT for scenes, not hardware details.

RULES:
1. Think in GROUPS: front_wash, back_light, side_fill, specials, ambient
2. Use SEMANTIC parameters: intensity (0-100), color (name or hex), focus_area
3. DO NOT specify DMX channels or fixture IDs — that happens later
4. Match lighting to emotion: warm for joy, cool for sadness, contrast for drama
5. Consider smooth transitions for most scenes

AVAILABLE GROUPS:
- front_wash: Primary audience-facing illumination
- back_light: Separation from background
- side_fill: Side lighting for depth
- specials: Focused highlights
- ambient: Overall atmosphere

{format_instructions}"""

USER_PROMPT = """Design lighting for this scene:

SCENE: {scene_text}
EMOTION: {emotion}
DURATION: {duration} seconds

CONTEXT FROM VENUE:
{context}

Specify lighting intent for appropriate groups."""


# =============================================================================
# LIGHTING DECISION ENGINE
# =============================================================================

class LightingDecisionEngine:
    """
    Phase 4: Convert scene emotions to lighting INTENT
    
    Uses LangChain for LLM-based generation with Pydantic output parsing.
    Falls back to rule-based generation if LLM fails.
    """
    
    def __init__(self, use_llm: bool = False, api_key: Optional[str] = None):
        """
        Initialize decision engine
        
        Args:
            use_llm: Whether to use LLM (requires API key)
            api_key: OpenAI API key (or set OPENAI_API_KEY env var)
        """
        self.retriever = get_retriever()
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        self.use_llm = use_llm and LANGCHAIN_AVAILABLE and bool(self.api_key)
        
        self.chain = None
        if self.use_llm:
            self.chain = self._create_llm_chain()
    
    def _create_llm_chain(self):
        """Create LangChain chain with prompt template and output parser"""
        parser = PydanticOutputParser(pydantic_object=LightingInstruction)
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT),
            ("user", USER_PROMPT)
        ])
        prompt = prompt.partial(format_instructions=parser.get_format_instructions())
        
        llm = ChatOpenAI(
            model=LLM_MODEL,
            api_key=self.api_key,
            temperature=LLM_TEMPERATURE,
            max_tokens=LLM_MAX_TOKENS,
            verbose=LANGCHAIN_VERBOSE
        )
        
        return prompt | llm | parser
    
    def generate_instruction(self, scene_data: Dict) -> LightingInstruction:
        """
        Generate lighting instruction for a scene
        
        Args:
            scene_data: Scene dictionary from Phase 1
            
        Returns:
            LightingInstruction with semantic lighting intent
        """
        emotion = scene_data.get("emotion", {}).get("primary_emotion", "neutral")
        scene_text = scene_data.get("content", {}).get("text", "")
        scene_id = scene_data.get("scene_id", "unknown")
        timing = scene_data.get("timing", {})
        
        if self.use_llm and self.chain:
            try:
                return self._generate_with_llm(scene_id, emotion, scene_text, timing)
            except Exception as e:
                print(f"LLM generation failed: {e}")
                if FALLBACK_TO_RULES:
                    print("Falling back to rule-based generation.")
                else:
                    raise
        
        return self._generate_with_rules(scene_id, emotion, scene_text, timing)
    
    def _generate_with_llm(
        self, 
        scene_id: str, 
        emotion: str, 
        scene_text: str, 
        timing: Dict
    ) -> LightingInstruction:
        """Generate using LangChain LLM chain"""
        context = self.retriever.build_context_for_llm(emotion, scene_text)
        
        response: LightingInstruction = self.chain.invoke({
            "scene_text": scene_text,
            "emotion": emotion,
            "duration": timing.get("duration", 0),
            "context": context
        })
        
        # Inject timing and metadata
        response.time_window = TimeWindow(
            start_time=timing.get("start_time", 0),
            end_time=timing.get("end_time", 0)
        )
        response.metadata = {"generation_method": "llm"}
        
        return response
    
    def _generate_with_rules(
        self, 
        scene_id: str, 
        emotion: str, 
        scene_text: str, 
        timing: Dict
    ) -> LightingInstruction:
        """Generate using rule-based system"""
        palette = self.retriever.retrieve_palette(emotion)
        
        # Build group instructions from palette
        groups = self._build_group_instructions(palette)
        
        return LightingInstruction(
            scene_id=scene_id,
            emotion=emotion,
            time_window=TimeWindow(
                start_time=timing.get("start_time", 0),
                end_time=timing.get("end_time", 0)
            ),
            groups=groups,
            metadata={"generation_method": "rule_based"}
        )
    
    def _build_group_instructions(self, palette: Dict) -> List[GroupLightingInstruction]:
        """Build group instructions from mood palette"""
        instructions = []
        
        # Get palette values
        primary_colors = palette.get("primary_colors", [{"name": "white", "rgb": [255, 255, 255]}])
        color = primary_colors[0].get("name", "white")
        
        intensity_config = palette.get("intensity", {"default": 50})
        intensity = intensity_config.get("default", 50)
        
        transition_config = palette.get("transition", {"type": "fade", "duration": 2.0})
        try:
            transition_type = TransitionType(transition_config.get("type", "fade"))
        except ValueError:
            transition_type = TransitionType.FADE
            
        transition = Transition(
            type=transition_type,
            duration_seconds=transition_config.get("duration", 2.0)
        )
        
        # Front wash — always present
        instructions.append(GroupLightingInstruction(
            group_id="front_wash",
            parameters=LightingParameters(
                intensity=intensity,
                color=color,
                focus_area=FocusArea.FULL_STAGE
            ),
            transition=transition
        ))
        
        # Back light — slightly dimmer
        instructions.append(GroupLightingInstruction(
            group_id="back_light",
            parameters=LightingParameters(
                intensity=intensity * 0.7,
                color=color,
                focus_area=FocusArea.FULL_STAGE
            ),
            transition=transition
        ))
        
        # Ambient for emotional scenes
        if palette.get("effects"):
            secondary_color = primary_colors[1].get("name", color) if len(primary_colors) > 1 else color
            instructions.append(GroupLightingInstruction(
                group_id="ambient",
                parameters=LightingParameters(
                    intensity=intensity * 0.3,
                    color=secondary_color,
                    color_temperature=palette.get("color_temperature", "neutral")
                ),
                transition=transition
            ))
        
        return instructions


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def generate_lighting_instruction(scene_data: Dict, use_llm: bool = False) -> LightingInstruction:
    """Generate lighting instruction for a single scene"""
    engine = LightingDecisionEngine(use_llm=use_llm)
    return engine.generate_instruction(scene_data)


def batch_generate_instructions(scenes: List[Dict], use_llm: bool = False) -> List[LightingInstruction]:
    """Generate lighting instructions for multiple scenes"""
    engine = LightingDecisionEngine(use_llm=use_llm)
    return [engine.generate_instruction(scene) for scene in scenes]
