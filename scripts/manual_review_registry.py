from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def iter_manual_review_decision_files(decisions_root: Path) -> list[Path]:
    if not decisions_root.exists():
        return []
    return sorted(path for path in decisions_root.rglob("decision.json") if path.is_file())


def collect_manual_review_decisions(decisions_root: Path) -> list[dict[str, Any]]:
    decisions: list[dict[str, Any]] = []

    for decision_path in iter_manual_review_decision_files(decisions_root):
        payload = read_json(decision_path)
        if not isinstance(payload, dict):
            continue
        candidate_key = str(payload.get("candidateKey") or "")
        final_decision = str(payload.get("finalDecision") or "")
        reviewer = str(payload.get("reviewer") or "")
        decided_at = str(payload.get("decidedAt") or "")
        summary_note = str(payload.get("summaryNote") or "")
        packet = payload.get("packet") if isinstance(payload.get("packet"), dict) else {}
        decisions.append(
            {
                "candidateKey": candidate_key,
                "finalDecision": final_decision,
                "reviewer": reviewer,
                "decidedAt": decided_at,
                "summaryNote": summary_note,
                "decisionPath": str(decision_path),
                "benchmarkId": str(packet.get("benchmarkId") or ""),
                "label": str(packet.get("label") or ""),
                "provider": str(packet.get("provider") or ""),
                "reviewCategory": str(packet.get("reviewCategory") or ""),
            }
        )

    return decisions


def build_manual_review_registry_report(decisions_root: Path) -> dict[str, Any]:
    decisions = collect_manual_review_decisions(decisions_root)
    decision_counts: dict[str, int] = {}
    for entry in decisions:
        decision = str(entry["finalDecision"])
        decision_counts[decision] = decision_counts.get(decision, 0) + 1

    promoted = [entry for entry in decisions if entry["finalDecision"] == "promote"]
    return {
        "entryCount": len(decisions),
        "decisionCounts": decision_counts,
        "promotedCandidateKeys": [entry["candidateKey"] for entry in promoted],
        "decisions": decisions,
    }


def load_promoted_manual_review_registry(decisions_root: Path) -> dict[str, dict[str, Any]]:
    promoted: dict[str, dict[str, Any]] = {}
    for entry in collect_manual_review_decisions(decisions_root):
        if entry["finalDecision"] != "promote":
            continue
        promoted[entry["candidateKey"]] = entry
    return promoted
