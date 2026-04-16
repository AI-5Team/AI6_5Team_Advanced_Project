from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from hybrid_source_selection import collect_hybrid_source_candidates


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_manual_review_queue_entry(candidate: dict[str, Any]) -> dict[str, Any]:
    role = str(candidate["role"])
    return {
        "benchmarkId": candidate["benchmarkId"],
        "label": candidate["label"],
        "provider": candidate["provider"],
        "decision": candidate["decision"],
        "gateReason": candidate["gateReason"],
        "role": role,
        "reviewCategory": "promotion_candidate" if role == "hybrid_source_candidate" else "reference_only",
        "recommendedAction": (
            "identity_review_then_promote_if_pass"
            if role == "hybrid_source_candidate"
            else "keep_as_reference_only"
        ),
        "imagePath": str(candidate["imagePath"]) if candidate["imagePath"] else None,
        "sourceVideoPath": str(candidate["sourceVideoPath"]),
        "contactSheetPath": str(candidate["contactSheetPath"]) if candidate["contactSheetPath"] else None,
        "summaryPath": str(candidate["summaryPath"]) if candidate["summaryPath"] else None,
        "midFrameMse": candidate["midFrameMse"],
        "motionAvgRgbDiff": candidate["motionAvgRgbDiff"],
    }


def collect_manual_review_queue_entries(
    summary: dict[str, Any],
    *,
    label: str | None = None,
    provider: str | None = None,
    include_reference_only: bool = False,
) -> list[dict[str, Any]]:
    candidates = collect_hybrid_source_candidates(summary, label=label)
    entries: list[dict[str, Any]] = []

    for candidate in candidates:
        if candidate["decision"] != "manual_review":
            continue
        if provider and candidate["provider"] != provider:
            continue
        if not include_reference_only and candidate["role"] == "reference_only":
            continue
        entries.append(build_manual_review_queue_entry(candidate))

    return sorted(
        entries,
        key=lambda entry: (
            entry["label"],
            0 if entry["reviewCategory"] == "promotion_candidate" else 1,
            -float(entry["motionAvgRgbDiff"]),
            float(entry["midFrameMse"]),
            entry["provider"],
        ),
    )


def build_manual_review_queue_report(
    benchmark_summaries: list[dict[str, Any]],
    *,
    label: str | None = None,
    provider: str | None = None,
    include_reference_only: bool = False,
) -> dict[str, Any]:
    entries: list[dict[str, Any]] = []
    benchmark_rows: list[dict[str, Any]] = []
    review_category_counts: dict[str, int] = {}

    for summary in benchmark_summaries:
        benchmark_id = str(summary.get("benchmark_id") or "")
        benchmark_entries = collect_manual_review_queue_entries(
            summary,
            label=label,
            provider=provider,
            include_reference_only=include_reference_only,
        )
        for entry in benchmark_entries:
            category = str(entry["reviewCategory"])
            review_category_counts[category] = review_category_counts.get(category, 0) + 1
        benchmark_rows.append(
            {
                "benchmarkId": benchmark_id,
                "entryCount": len(benchmark_entries),
                "entries": benchmark_entries,
            }
        )
        entries.extend(benchmark_entries)

    return {
        "entryCount": len(entries),
        "reviewCategoryCounts": review_category_counts,
        "benchmarks": benchmark_rows,
        "entries": entries,
        "filters": {
            "label": label,
            "provider": provider,
            "includeReferenceOnly": include_reference_only,
        },
    }


def render_manual_review_queue_markdown(report: dict[str, Any], *, experiment_id: str) -> str:
    lines = [
        f"# {experiment_id} Manual Review Queue",
        "",
        "## Summary",
        "",
        f"- total entries: `{report['entryCount']}`",
        f"- review category counts: `{json.dumps(report['reviewCategoryCounts'], ensure_ascii=False)}`",
        f"- filters: `{json.dumps(report['filters'], ensure_ascii=False)}`",
        "",
        "## Entries",
        "",
    ]

    entries = report.get("entries", [])
    if not entries:
        lines.append("- no manual review entries")
        return "\n".join(lines) + "\n"

    lines.append("| label | provider | benchmark | category | mse | motion | action |")
    lines.append("| --- | --- | --- | --- | ---: | ---: | --- |")

    for entry in entries:
        lines.append(
            "| {label} | {provider} | {benchmarkId} | {reviewCategory} | {midFrameMse:.2f} | {motionAvgRgbDiff:.2f} | {recommendedAction} |".format(
                **entry
            )
        )

    lines.append("")
    lines.append("## Paths")
    lines.append("")

    for index, entry in enumerate(entries, start=1):
        lines.extend(
            [
                f"### {index}. {entry['label']} / {entry['provider']}",
                "",
                f"- benchmark: `{entry['benchmarkId']}`",
                f"- decision: `{entry['decision']}`",
                f"- role: `{entry['role']}`",
                f"- gate reason: `{entry['gateReason']}`",
                f"- image: `{entry['imagePath']}`",
                f"- source video: `{entry['sourceVideoPath']}`",
                f"- contact sheet: `{entry['contactSheetPath']}`",
                f"- summary: `{entry['summaryPath']}`",
                "",
            ]
        )

    return "\n".join(lines) + "\n"
