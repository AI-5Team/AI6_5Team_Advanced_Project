from __future__ import annotations

import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPTS_ROOT = REPO_ROOT / "scripts"
if str(SCRIPTS_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_ROOT))

from manual_review_registry import build_manual_review_registry_report, load_promoted_manual_review_registry


def write_decision(decisions_root: Path, *, candidate_key: str, final_decision: str) -> None:
    target = decisions_root / candidate_key.replace("::", "__")
    target.mkdir(parents=True, exist_ok=True)
    payload = {
        "candidateKey": candidate_key,
        "finalDecision": final_decision,
        "reviewer": "codex",
        "decidedAt": "2026-04-14T16:10:00+09:00",
        "summaryNote": "test",
        "packet": {
            "benchmarkId": "EXP-239",
            "label": "규카츠",
            "provider": "sora2_current_best",
            "reviewCategory": "promotion_candidate",
        },
    }
    (target / "decision.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def test_manual_review_registry_report_and_promoted_lookup(tmp_path: Path) -> None:
    decisions_root = tmp_path / "decisions"
    write_decision(decisions_root, candidate_key="EXP-239::규카츠::sora2_current_best", final_decision="hold")
    write_decision(decisions_root, candidate_key="EXP-238::맥주::sora2_current_best", final_decision="promote")

    report = build_manual_review_registry_report(decisions_root)
    promoted = load_promoted_manual_review_registry(decisions_root)

    assert report["entryCount"] == 2
    assert report["decisionCounts"] == {"hold": 1, "promote": 1}
    assert report["promotedCandidateKeys"] == ["EXP-238::맥주::sora2_current_best"]
    assert "EXP-238::맥주::sora2_current_best" in promoted
    assert "EXP-239::규카츠::sora2_current_best" not in promoted
