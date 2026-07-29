"""Run the Point & Ask classification eval and report pass rate against known answers.

Tests only the routing decision (classify -> score -> branch), not explain-text
quality, since that's the safety-critical part worth automating.

Usage: uv run python eval/run_point_and_ask_eval.py
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.point_and_ask import classify_image, decide_branch, score_risk  # noqa: E402

CASES_PATH = Path(__file__).parent / "point_and_ask_eval_cases.json"


def main() -> None:
    cases = json.loads(CASES_PATH.read_text())
    passed = 0
    for i, case in enumerate(cases, start=1):
        image_bytes = (Path(__file__).parent / case["image"]).read_bytes()
        result = classify_image(image_bytes, "image/png")
        risk_level = score_risk(result)
        classification = decide_branch(result, risk_level)

        ok = classification == case["expected_classification"]
        passed += ok
        status = "PASS" if ok else "FAIL"
        print(
            f"[{status}] case {i} ({case['image']}): got={classification!r} "
            f"(risk={risk_level!r}) expected={case['expected_classification']!r}"
        )
    print(f"\n{passed}/{len(cases)} passed")


if __name__ == "__main__":
    main()
