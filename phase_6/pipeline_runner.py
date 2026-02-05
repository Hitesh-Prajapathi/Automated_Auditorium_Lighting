"""
Phase 6: Pipeline Runner

The ORCHESTRATION SPINE.
Controls execution order, enables/disables phases, passes data between phases.

Phase 6:
- Treats every phase as a BLACK BOX
- ONLY calls published entry points
- NEVER modifies phase outputs
- NEVER retries silently
- NEVER swallows errors
"""

import time
import logging
from typing import Dict, List, Optional, Any

from .config_models import PipelineConfig, PhaseStatus, PhaseResult, PipelineResult
from .state_tracker import StateTracker
from .errors import (
    HardFailureError,
    NonFatalError,
    ContractViolationError,
    PhaseNotImplementedError
)

# Configure logging
logger = logging.getLogger("phase_6.pipeline")


class PipelineRunner:
    """
    Phase 6 Pipeline Orchestrator
    
    Canonical execution order (LOCKED):
    1. Phase 1 — Script parsing & scene extraction
    2. Phase 2 — Emotion enrichment (optional, nullable)
    3. Phase 3 — RAG retrieval (REQUIRED)
    4. Phase 4 — LightingDecisionEngine (REQUIRED)
    5. Phase 5 — Simulation & visualization (OPTIONAL)
    6. Phase 7 — Logging & evaluation (OPTIONAL)
    7. Phase 8 — Hardware execution (FUTURE, OPTIONAL)
    """
    
    def __init__(self, config: Optional[PipelineConfig] = None):
        """
        Initialize pipeline runner.
        
        Args:
            config: Pipeline configuration. Defaults to PipelineConfig().
        """
        self.config = config or PipelineConfig()
        self.state = StateTracker()
    
    def run(self, script_path: str) -> PipelineResult:
        """
        Execute the full pipeline for a script.
        
        Args:
            script_path: Path to input script file
            
        Returns:
            PipelineResult with all phase results
        """
        result = PipelineResult(script_path=script_path)
        
        logger.info(f"Pipeline started: {script_path}")
        pipeline_start = time.time()
        
        try:
            # Phase 1: Parsing (REQUIRED - HARD FAIL)
            scenes = self._run_phase_1(script_path, result)
            
            self.state.start_pipeline(script_path, len(scenes))
            
            # Process each scene
            lighting_instructions = []
            for idx, scene in enumerate(scenes):
                scene_id = scene.get("scene_id", f"scene_{idx:03d}")
                self.state.set_current_scene(scene_id, idx)
                
                # Phase 2: Emotion (OPTIONAL - continue with null if fails)
                enriched_scene = self._run_phase_2(scene, result)
                
                # Phase 3: RAG retrieval (REQUIRED - HARD FAIL)
                rag_context = self._run_phase_3(enriched_scene, result)
                
                # Phase 4: Decision Engine (REQUIRED - HARD FAIL after fallback)
                instruction = self._run_phase_4(enriched_scene, rag_context, result)
                lighting_instructions.append(instruction)
            
            # Phase 5: Simulation (OPTIONAL - log & continue)
            if self.config.enable_phase_5:
                self._run_phase_5(lighting_instructions, result)
            else:
                result.add_phase_result(
                    self.state.skip_phase("phase_5", "Disabled by configuration")
                )
            
            # Phase 7: Evaluation (OPTIONAL - log & continue)
            if self.config.enable_phase_7:
                self._run_phase_7(lighting_instructions, result)
            else:
                result.add_phase_result(
                    self.state.skip_phase("phase_7", "Disabled by configuration")
                )
            
            # Phase 8: Hardware (NOT IMPLEMENTED)
            if self.config.enable_phase_8:
                result.add_phase_result(
                    self.state.skip_phase("phase_8", "Not implemented")
                )
            
            result.mark_complete()
            self.state.complete_pipeline(PhaseStatus.SUCCESS)
            
        except HardFailureError as e:
            logger.error(f"Pipeline hard failure in {e.phase_name}: {e}")
            result.final_status = PhaseStatus.FAILED
            self.state.complete_pipeline(PhaseStatus.FAILED)
            
        except Exception as e:
            logger.exception(f"Unexpected pipeline error: {e}")
            result.final_status = PhaseStatus.FAILED
            self.state.complete_pipeline(PhaseStatus.FAILED)
        
        result.total_duration_seconds = time.time() - pipeline_start
        logger.info(f"Pipeline completed: {result.final_status.value} in {result.total_duration_seconds:.2f}s")
        
        return result
    
    def _run_phase_1(self, script_path: str, result: PipelineResult) -> List[Dict]:
        """
        Phase 1: Script parsing & scene extraction
        REQUIRED - HARD FAIL on error
        """
        self.state.start_phase("phase_1")
        logger.info("Phase 1: Starting script parsing")
        
        try:
            # Import Phase 1 entry point
            from phase_1 import (
                detect_format,
                clean_text,
                segment_scenes,
                generate_timestamps,
                extract_timestamps
            )
            from utils import read_script
            
            # Execute Phase 1
            raw_text = read_script(script_path)
            format_info = detect_format(raw_text)
            cleaned_text = clean_text(raw_text, preserve_structure=True)
            scenes = segment_scenes(cleaned_text, format_info)
            
            # Handle timestamps
            if format_info['timestamped']:
                timestamps = extract_timestamps(raw_text, scenes)
            else:
                timestamps = generate_timestamps(scenes)
            
            # Enrich scenes with timestamps
            for scene, timestamp in zip(scenes, timestamps):
                scene["timing"] = timestamp
            
            phase_result = self.state.complete_phase(
                "phase_1",
                PhaseStatus.SUCCESS,
                output={"scene_count": len(scenes)}
            )
            result.add_phase_result(phase_result)
            
            logger.info(f"Phase 1: Parsed {len(scenes)} scenes")
            return scenes
            
        except Exception as e:
            phase_result = self.state.complete_phase(
                "phase_1",
                PhaseStatus.FAILED,
                error_message=str(e)
            )
            result.add_phase_result(phase_result)
            raise HardFailureError(f"Phase 1 failed: {e}", phase_name="phase_1")
    
    def _run_phase_2(self, scene: Dict, result: PipelineResult) -> Dict:
        """
        Phase 2: Emotion enrichment
        OPTIONAL - continue with emotion=null if fails
        """
        self.state.start_phase("phase_2")
        
        try:
            from phase_2 import analyze_emotion
            
            content = scene.get("content", {}).get("text", "")
            if not content:
                content = scene.get("content", "")
            
            emotion_analysis = analyze_emotion(content)
            scene["emotion"] = emotion_analysis
            
            phase_result = self.state.complete_phase(
                "phase_2",
                PhaseStatus.SUCCESS,
                output={"emotion": emotion_analysis.get("primary_emotion")}
            )
            result.add_phase_result(phase_result)
            
            return scene
            
        except Exception as e:
            logger.warning(f"Phase 2 failed (non-fatal): {e}")
            scene["emotion"] = {"primary_emotion": "neutral", "confidence": 0.0}
            
            phase_result = self.state.complete_phase(
                "phase_2",
                PhaseStatus.FAILED,
                error_message=str(e)
            )
            result.add_phase_result(phase_result)
            
            # Non-fatal - continue with null emotion
            return scene
    
    def _run_phase_3(self, scene: Dict, result: PipelineResult) -> str:
        """
        Phase 3: RAG retrieval
        REQUIRED - HARD FAIL on error
        """
        self.state.start_phase("phase_3")
        
        try:
            from phase_3 import get_retriever
            
            retriever = get_retriever()
            emotion = scene.get("emotion", {}).get("primary_emotion", "neutral")
            scene_text = scene.get("content", {}).get("text", "")
            if not scene_text:
                scene_text = scene.get("content", "")
            
            context = retriever.build_context_for_llm(emotion, scene_text)
            
            phase_result = self.state.complete_phase(
                "phase_3",
                PhaseStatus.SUCCESS,
                output={"context_length": len(context)}
            )
            result.add_phase_result(phase_result)
            
            return context
            
        except Exception as e:
            phase_result = self.state.complete_phase(
                "phase_3",
                PhaseStatus.FAILED,
                error_message=str(e)
            )
            result.add_phase_result(phase_result)
            raise HardFailureError(f"Phase 3 failed: {e}", phase_name="phase_3")
    
    def _run_phase_4(
        self, 
        scene: Dict, 
        rag_context: str, 
        result: PipelineResult
    ) -> Dict:
        """
        Phase 4: Lighting Decision Engine
        REQUIRED - HARD FAIL after internal fallback exhausted
        """
        self.state.start_phase("phase_4")
        
        try:
            from phase_4 import LightingDecisionEngine
            
            engine = LightingDecisionEngine(use_llm=self.config.use_llm)
            instruction = engine.generate_instruction(scene)
            
            # Validate output against contract
            self._validate_lighting_instruction(instruction)
            
            phase_result = self.state.complete_phase(
                "phase_4",
                PhaseStatus.SUCCESS,
                output={"groups_count": len(instruction.groups)}
            )
            result.add_phase_result(phase_result)
            
            return instruction.model_dump()
            
        except ContractViolationError as e:
            phase_result = self.state.complete_phase(
                "phase_4",
                PhaseStatus.FAILED,
                error_message=str(e)
            )
            result.add_phase_result(phase_result)
            raise HardFailureError(f"Phase 4 contract violation: {e}", phase_name="phase_4")
            
        except Exception as e:
            phase_result = self.state.complete_phase(
                "phase_4",
                PhaseStatus.FAILED,
                error_message=str(e)
            )
            result.add_phase_result(phase_result)
            raise HardFailureError(f"Phase 4 failed: {e}", phase_name="phase_4")
    
    def _run_phase_5(
        self, 
        lighting_instructions: List[Dict], 
        result: PipelineResult
    ) -> None:
        """
        Phase 5: Simulation & visualization
        OPTIONAL - NON-FATAL, log & continue
        """
        self.state.start_phase("phase_5")
        
        try:
            # Phase 5 entry point - visualization
            from phase_5 import playback_engine
            
            # Phase 5 handles its own rendering
            # Phase 6 does NOT interpret visualization output
            
            phase_result = self.state.complete_phase(
                "phase_5",
                PhaseStatus.SUCCESS
            )
            result.add_phase_result(phase_result)
            
        except ImportError:
            logger.warning("Phase 5 not available - skipping")
            phase_result = self.state.complete_phase(
                "phase_5",
                PhaseStatus.SKIPPED,
                error_message="Module not available"
            )
            result.add_phase_result(phase_result)
            
        except Exception as e:
            logger.warning(f"Phase 5 failed (non-fatal): {e}")
            phase_result = self.state.complete_phase(
                "phase_5",
                PhaseStatus.FAILED,
                error_message=str(e)
            )
            result.add_phase_result(phase_result)
            # Non-fatal - continue
    
    def _run_phase_7(
        self, 
        lighting_instructions: List[Dict], 
        result: PipelineResult
    ) -> None:
        """
        Phase 7: Logging & evaluation
        OPTIONAL - NON-FATAL, log & continue
        """
        self.state.start_phase("phase_7")
        
        try:
            # Phase 7 entry point - evaluation (PENDING implementation)
            # from phase_7 import evaluate
            
            # Phase 7 not yet implemented
            phase_result = self.state.complete_phase(
                "phase_7",
                PhaseStatus.SKIPPED,
                error_message="Phase 7 not yet implemented"
            )
            result.add_phase_result(phase_result)
            
        except ImportError:
            logger.warning("Phase 7 not available - skipping")
            phase_result = self.state.complete_phase(
                "phase_7",
                PhaseStatus.SKIPPED,
                error_message="Module not available"
            )
            result.add_phase_result(phase_result)
            
        except Exception as e:
            logger.warning(f"Phase 7 failed (non-fatal): {e}")
            phase_result = self.state.complete_phase(
                "phase_7",
                PhaseStatus.FAILED,
                error_message=str(e)
            )
            result.add_phase_result(phase_result)
            # Non-fatal - continue
    
    def _validate_lighting_instruction(self, instruction) -> None:
        """
        Validate LightingInstruction against contract.
        
        Phase 6 enforces ONLY:
        - group_id is present (not fixture_id)
        - intensity ∈ [0, 1]
        - Required fields exist
        """
        for group in instruction.groups:
            # Verify group_id exists
            if not group.group_id:
                raise ContractViolationError("Missing group_id in LightingInstruction")
            
            # Verify intensity in [0, 1]
            intensity = group.parameters.intensity
            if intensity < 0.0 or intensity > 1.0:
                raise ContractViolationError(
                    f"Intensity {intensity} out of range [0, 1]"
                )
    
    def get_state(self):
        """Get current pipeline state"""
        return self.state.get_state()
    
    def get_summary(self):
        """Get execution summary"""
        return self.state.get_summary()
