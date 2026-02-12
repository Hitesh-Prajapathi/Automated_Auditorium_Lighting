import json
from phase_6 import PipelineRunner, PipelineConfig

if __name__ == "__main__":
    config = PipelineConfig(
        enable_phase_5=True,
        enable_phase_7=True,
        use_llm=False  # Deterministic baseline — rule-based
    )

    runner = PipelineRunner(config)
    result = runner.run("data/raw_scripts/Script-1.txt")

    print("\n========== PIPELINE RESULT ==========")
    print("Final Status:", result.final_status)
    print()

    # Print per-phase results
    for pr in result.phase_results:
        print(f"  {pr.phase_name}: {pr.status.value}", end="")
        if pr.output:
            print(f"  → {pr.output}")
        elif pr.error_message:
            print(f"  ⚠ {pr.error_message}")
        else:
            print()

    print("=====================================\n")
