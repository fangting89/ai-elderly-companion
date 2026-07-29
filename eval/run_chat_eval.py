"""Run the chat tagging eval set and report pass rate against known answers.

Usage: uv run python eval/run_chat_eval.py
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.chat import TAG_SCHEMA, TAG_SYSTEM_PROMPT  # noqa: E402
from backend.claude_client import TAG_MODEL, call_structured  # noqa: E402

CASES_PATH = Path(__file__).parent / "chat_eval_cases.json"


def main() -> None:
    cases = json.loads(CASES_PATH.read_text())
    passed = 0
    for i, case in enumerate(cases, start=1):
        messages = [*case["context"], {"role": "user", "content": case["message"]}]
        tags = call_structured(
            model=TAG_MODEL,
            system=TAG_SYSTEM_PROMPT,
            messages=messages,
            tool_name="tag_message",
            tool_description="Classify the sentiment and repetition of the latest message.",
            tool_schema=TAG_SCHEMA,
        )
        ok = (
            tags["sentiment"] == case["expected_sentiment"]
            and tags["repeated_question_flag"] == case["expected_repeated_question_flag"]
        )
        passed += ok
        status = "PASS" if ok else "FAIL"
        print(
            f"[{status}] case {i}: got sentiment={tags['sentiment']!r} "
            f"repeated={tags['repeated_question_flag']!r} (expected "
            f"sentiment={case['expected_sentiment']!r} "
            f"repeated={case['expected_repeated_question_flag']!r})"
        )
    print(f"\n{passed}/{len(cases)} passed")


if __name__ == "__main__":
    main()
