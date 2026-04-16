from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from hybrid_source_selection import collect_hybrid_source_candidates
from manual_review_decision import build_candidate_key
from manual_review_registry import collect_manual_review_decisions


SERVICE_LANE_BY_LABEL = {
    "맥주": "drink_glass_lane",
    "규카츠": "tray_full_plate_lane",
}


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def infer_service_lane(label: str) -> str:
    return SERVICE_LANE_BY_LABEL.get(label, f"label::{label}")


def _candidate_sort_key(item: dict[str, Any]) -> tuple[int, float, float, str]:
    selection_mode = str(item.get("selectionMode") or "")
    selection_rank = 0 if selection_mode == "benchmark_gate" else 1
    return (
        selection_rank,
        -float(item.get("motionAvgRgbDiff") or 0.0),
        float(item.get("midFrameMse") or 0.0),
        str(item.get("provider") or ""),
    )


def _stringify_path(path_value: Any) -> str | None:
    if path_value in {None, ""}:
        return None
    return str(path_value)


def _build_inventory_item(candidate: dict[str, Any], *, approval_source: str, selection_mode: str) -> dict[str, Any]:
    label = str(candidate.get("label") or "")
    return {
        "candidateKey": str(candidate.get("candidateKey") or ""),
        "serviceLane": infer_service_lane(label),
        "approvalSource": approval_source,
        "selectionMode": selection_mode,
        "benchmarkId": str(candidate.get("benchmarkId") or ""),
        "label": label,
        "provider": str(candidate.get("provider") or ""),
        "gateDecision": str(candidate.get("decision") or ""),
        "gateReason": str(candidate.get("gateReason") or ""),
        "role": str(candidate.get("role") or ""),
        "imagePath": _stringify_path(candidate.get("imagePath")),
        "sourceVideoPath": _stringify_path(candidate.get("sourceVideoPath")),
        "contactSheetPath": _stringify_path(candidate.get("contactSheetPath")),
        "summaryPath": _stringify_path(candidate.get("summaryPath")),
        "midFrameMse": float(candidate.get("midFrameMse") or 0.0),
        "motionAvgRgbDiff": float(candidate.get("motionAvgRgbDiff") or 0.0),
        "reviewFinalDecision": candidate.get("reviewFinalDecision"),
        "reviewDecisionPath": _stringify_path(candidate.get("reviewDecisionPath")),
        "reviewer": candidate.get("reviewer"),
        "reviewDecidedAt": candidate.get("reviewDecidedAt"),
    }


def collect_approved_hybrid_inventory(
    benchmark_summaries: list[Path],
    *,
    decisions_root: Path | None = None,
) -> list[dict[str, Any]]:
    candidates_by_key: dict[str, dict[str, Any]] = {}
    inventory_by_key: dict[str, dict[str, Any]] = {}

    for summary_path in benchmark_summaries:
        summary = read_json(summary_path)
        for candidate in collect_hybrid_source_candidates(summary):
            candidate_key = str(candidate.get("candidateKey") or "")
            if not candidate_key:
                continue
            candidates_by_key[candidate_key] = candidate
            if candidate.get("decision") == "accept" and candidate.get("role") == "hybrid_source_candidate":
                inventory_by_key[candidate_key] = _build_inventory_item(
                    candidate,
                    approval_source="benchmark_accept",
                    selection_mode="benchmark_gate",
                )

    if decisions_root is not None:
        for decision in collect_manual_review_decisions(decisions_root):
            if decision.get("finalDecision") != "promote":
                continue
            candidate_key = str(decision.get("candidateKey") or "")
            if not candidate_key:
                continue
            candidate = candidates_by_key.get(candidate_key)
            if candidate is None:
                packet = read_json(Path(decision["decisionPath"])).get("packet") or {}
                candidate = {
                    "candidateKey": candidate_key,
                    "benchmarkId": str(packet.get("benchmarkId") or decision.get("benchmarkId") or ""),
                    "label": str(packet.get("label") or decision.get("label") or ""),
                    "provider": str(packet.get("provider") or decision.get("provider") or ""),
                    "decision": str(packet.get("decision") or "manual_review"),
                    "gateReason": str(packet.get("gateReason") or ""),
                    "role": "hybrid_source_candidate",
                    "imagePath": packet.get("imagePath"),
                    "sourceVideoPath": packet.get("sourceVideoPath"),
                    "contactSheetPath": packet.get("contactSheetPath"),
                    "summaryPath": packet.get("summaryPath"),
                    "midFrameMse": float(packet.get("midFrameMse") or 0.0),
                    "motionAvgRgbDiff": float(packet.get("motionAvgRgbDiff") or 0.0),
                }
                if not candidate.get("candidateKey"):
                    candidate["candidateKey"] = build_candidate_key(candidate)

            promoted_item = _build_inventory_item(
                {
                    **candidate,
                    "reviewFinalDecision": decision.get("finalDecision"),
                    "reviewDecisionPath": decision.get("decisionPath"),
                    "reviewer": decision.get("reviewer"),
                    "reviewDecidedAt": decision.get("decidedAt"),
                },
                approval_source="manual_review_promote",
                selection_mode="promoted_manual_review",
            )
            inventory_by_key[candidate_key] = promoted_item

    return sorted(inventory_by_key.values(), key=lambda item: (item["serviceLane"], item["label"], _candidate_sort_key(item)))


def build_approved_hybrid_inventory_report(
    benchmark_summaries: list[Path],
    *,
    decisions_root: Path | None = None,
) -> dict[str, Any]:
    items = collect_approved_hybrid_inventory(benchmark_summaries, decisions_root=decisions_root)

    lane_counts: dict[str, int] = {}
    label_counts: dict[str, int] = {}
    approval_source_counts: dict[str, int] = {}
    recommended_by_lane: dict[str, dict[str, Any]] = {}
    recommended_by_label: dict[str, dict[str, Any]] = {}

    for item in items:
        lane = str(item["serviceLane"])
        label = str(item["label"])
        approval_source = str(item["approvalSource"])
        lane_counts[lane] = lane_counts.get(lane, 0) + 1
        label_counts[label] = label_counts.get(label, 0) + 1
        approval_source_counts[approval_source] = approval_source_counts.get(approval_source, 0) + 1

        lane_current = recommended_by_lane.get(lane)
        if lane_current is None or _candidate_sort_key(item) < _candidate_sort_key(lane_current):
            recommended_by_lane[lane] = item

        label_current = recommended_by_label.get(label)
        if label_current is None or _candidate_sort_key(item) < _candidate_sort_key(label_current):
            recommended_by_label[label] = item

    return {
        "benchmarkSummaries": [str(path) for path in benchmark_summaries],
        "decisionsRoot": str(decisions_root) if decisions_root else None,
        "itemCount": len(items),
        "laneCounts": lane_counts,
        "labelCounts": label_counts,
        "approvalSourceCounts": approval_source_counts,
        "recommendedByLane": recommended_by_lane,
        "recommendedByLabel": recommended_by_label,
        "items": items,
    }
