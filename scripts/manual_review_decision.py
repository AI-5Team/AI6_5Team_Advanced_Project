from __future__ import annotations

from datetime import datetime
import json
from typing import Any


CHECKLIST_ITEMS = [
    {
        "id": "main_subject_identity",
        "label": "메인 피사체 보존",
        "question": "메인 음식 또는 제품의 형태와 핵심 구성은 원본과 같은가",
    },
    {
        "id": "peripheral_layout",
        "label": "주변 구성 보존",
        "question": "반찬, 그릇, 배경 소품의 배치와 수량이 본선 허용 범위 안에 있는가",
    },
    {
        "id": "text_qr_intrusion",
        "label": "텍스트 침입 없음",
        "question": "원본에 없던 문자, 로고, QR, UI 파편이 새로 생기지 않았는가",
    },
    {
        "id": "motion_packaging_fit",
        "label": "모션 패키징 적합",
        "question": "움직임이 짧은 숏폼 광고 패키징에 쓸 만큼 읽히는가",
    },
    {
        "id": "promotion_readiness",
        "label": "승격 준비도",
        "question": "지금 기준으로 accept lane에 올려도 서비스 품질 리스크가 감당 가능한가",
    },
]

VALID_CHECK_STATUSES = {"pending", "pass", "hold", "fail"}
VALID_FINAL_DECISIONS = {"hold", "promote", "reject"}


def build_candidate_key(entry: dict[str, Any]) -> str:
    return f"{entry['benchmarkId']}::{entry['label']}::{entry['provider']}"


def build_manual_review_packet(entry: dict[str, Any]) -> dict[str, Any]:
    suggested_focus: list[str] = []
    if float(entry.get("midFrameMse") or 0.0) > 3000.0:
        suggested_focus.append("peripheral_identity_drift")
    if float(entry.get("motionAvgRgbDiff") or 0.0) >= 15.0:
        suggested_focus.append("high_motion_consistency")

    return {
        "candidateKey": build_candidate_key(entry),
        "benchmarkId": entry["benchmarkId"],
        "label": entry["label"],
        "provider": entry["provider"],
        "decision": entry["decision"],
        "gateReason": entry["gateReason"],
        "reviewCategory": entry["reviewCategory"],
        "recommendedAction": entry["recommendedAction"],
        "imagePath": entry["imagePath"],
        "sourceVideoPath": entry["sourceVideoPath"],
        "contactSheetPath": entry["contactSheetPath"],
        "summaryPath": entry["summaryPath"],
        "midFrameMse": entry["midFrameMse"],
        "motionAvgRgbDiff": entry["motionAvgRgbDiff"],
        "suggestedFocus": suggested_focus,
        "checklist": [
            {
                "id": item["id"],
                "label": item["label"],
                "question": item["question"],
                "status": "pending",
                "notes": "",
            }
            for item in CHECKLIST_ITEMS
        ],
    }


def build_manual_review_packet_report(queue_report: dict[str, Any]) -> dict[str, Any]:
    entries = queue_report.get("entries", [])
    packets = [build_manual_review_packet(entry) for entry in entries if isinstance(entry, dict)]
    return {
        "entryCount": len(packets),
        "candidateKeys": [packet["candidateKey"] for packet in packets],
        "packets": packets,
    }


def _normalize_check_status(status: str) -> str:
    normalized = str(status).strip().lower()
    if normalized not in VALID_CHECK_STATUSES:
        raise ValueError(f"invalid checklist status: {status!r}")
    return normalized


def _normalize_final_decision(decision: str) -> str:
    normalized = str(decision).strip().lower()
    if normalized not in VALID_FINAL_DECISIONS:
        raise ValueError(f"invalid final decision: {decision!r}")
    return normalized


def apply_manual_review_decision(
    packet: dict[str, Any],
    *,
    reviewer: str,
    final_decision: str,
    summary_note: str,
    checklist_statuses: dict[str, str] | None = None,
    checklist_notes: dict[str, str] | None = None,
    decided_at: str | None = None,
) -> dict[str, Any]:
    checklist_statuses = checklist_statuses or {}
    checklist_notes = checklist_notes or {}
    final_decision = _normalize_final_decision(final_decision)

    reviewed_checklist: list[dict[str, Any]] = []
    status_counts: dict[str, int] = {}
    known_ids = {item["id"] for item in packet.get("checklist", [])}

    for checklist_id in checklist_statuses:
        if checklist_id not in known_ids:
            raise ValueError(f"unknown checklist id: {checklist_id!r}")
    for checklist_id in checklist_notes:
        if checklist_id not in known_ids:
            raise ValueError(f"unknown checklist id: {checklist_id!r}")

    for item in packet.get("checklist", []):
        checklist_id = str(item["id"])
        status = _normalize_check_status(checklist_statuses.get(checklist_id, item["status"]))
        notes = str(checklist_notes.get(checklist_id, item.get("notes", "")))
        status_counts[status] = status_counts.get(status, 0) + 1
        reviewed_checklist.append({**item, "status": status, "notes": notes})

    return {
        "candidateKey": packet["candidateKey"],
        "reviewer": reviewer,
        "decidedAt": decided_at or datetime.now().astimezone().isoformat(timespec="seconds"),
        "finalDecision": final_decision,
        "summaryNote": summary_note,
        "statusCounts": status_counts,
        "packet": {
            **packet,
            "checklist": reviewed_checklist,
        },
    }


def render_manual_review_decision_markdown(decision: dict[str, Any], *, experiment_id: str) -> str:
    packet = decision["packet"]
    lines = [
        f"# {experiment_id} Manual Review Decision",
        "",
        "## Candidate",
        "",
        f"- candidate key: `{decision['candidateKey']}`",
        f"- reviewer: `{decision['reviewer']}`",
        f"- decided at: `{decision['decidedAt']}`",
        f"- final decision: `{decision['finalDecision']}`",
        f"- summary note: `{decision['summaryNote']}`",
        "",
        "## Metrics",
        "",
        f"- midFrameMse: `{packet['midFrameMse']}`",
        f"- motionAvgRgbDiff: `{packet['motionAvgRgbDiff']}`",
        f"- suggested focus: `{json.dumps(packet['suggestedFocus'], ensure_ascii=False)}`",
        "",
        "## Checklist",
        "",
        "| id | status | label | notes |",
        "| --- | --- | --- | --- |",
    ]

    for item in packet.get("checklist", []):
        lines.append(f"| {item['id']} | {item['status']} | {item['label']} | {item['notes']} |")

    lines.extend(
        [
            "",
            "## Paths",
            "",
            f"- image: `{packet['imagePath']}`",
            f"- source video: `{packet['sourceVideoPath']}`",
            f"- contact sheet: `{packet['contactSheetPath']}`",
            f"- summary: `{packet['summaryPath']}`",
            "",
        ]
    )
    return "\n".join(lines) + "\n"
