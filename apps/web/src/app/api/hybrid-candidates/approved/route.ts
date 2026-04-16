import { readFile } from "node:fs/promises";
import { resolve } from "node:path";
import { NextRequest } from "next/server";
import type { ApprovedHybridCandidateItem, ApprovedHybridInventoryResponse } from "@/lib/contracts";
import { fail, ok } from "@/lib/route-utils";

const DEFAULT_REPORT_RELATIVE_PATH = "docs/experiments/artifacts/exp-254-approved-hybrid-candidate-inventory/report.json";
const REPO_ROOT = resolve(process.cwd(), "..", "..");

function selectRecommendedItem(items: ApprovedHybridCandidateItem[]) {
  if (!items.length) return null;
  return [...items].sort((left, right) => {
    const leftSelectionRank = left.selectionMode === "benchmark_gate" ? 0 : 1;
    const rightSelectionRank = right.selectionMode === "benchmark_gate" ? 0 : 1;
    if (leftSelectionRank !== rightSelectionRank) return leftSelectionRank - rightSelectionRank;

    const motionDiff = (right.motionAvgRgbDiff ?? 0) - (left.motionAvgRgbDiff ?? 0);
    if (motionDiff !== 0) return motionDiff;

    const mseDiff = (left.midFrameMse ?? 0) - (right.midFrameMse ?? 0);
    if (mseDiff !== 0) return mseDiff;

    return left.provider.localeCompare(right.provider);
  })[0] ?? null;
}

function buildInventoryView(
  report: { items?: unknown },
  options?: { label?: string | null; serviceLane?: string | null },
): ApprovedHybridInventoryResponse {
  const items = Array.isArray(report.items)
    ? report.items.filter((item): item is ApprovedHybridCandidateItem => typeof item === "object" && item !== null)
    : [];
  const filteredItems = items.filter((item) => {
    if (options?.label && item.label !== options.label) return false;
    if (options?.serviceLane && item.serviceLane !== options.serviceLane) return false;
    return true;
  });

  const laneCounts: Record<string, number> = {};
  const labelCounts: Record<string, number> = {};
  const approvalSourceCounts: Record<string, number> = {};
  const groupedByLane: Record<string, ApprovedHybridCandidateItem[]> = {};
  const groupedByLabel: Record<string, ApprovedHybridCandidateItem[]> = {};

  filteredItems.forEach((item) => {
    laneCounts[item.serviceLane] = (laneCounts[item.serviceLane] ?? 0) + 1;
    labelCounts[item.label] = (labelCounts[item.label] ?? 0) + 1;
    approvalSourceCounts[item.approvalSource] = (approvalSourceCounts[item.approvalSource] ?? 0) + 1;
    groupedByLane[item.serviceLane] = [...(groupedByLane[item.serviceLane] ?? []), item];
    groupedByLabel[item.label] = [...(groupedByLabel[item.label] ?? []), item];
  });

  const recommendedByLane = Object.fromEntries(
    Object.entries(groupedByLane)
      .map(([lane, laneItems]) => [lane, selectRecommendedItem(laneItems)] as const)
      .filter((entry): entry is [string, ApprovedHybridCandidateItem] => entry[1] !== null),
  );
  const recommendedByLabel = Object.fromEntries(
    Object.entries(groupedByLabel)
      .map(([label, labelItems]) => [label, selectRecommendedItem(labelItems)] as const)
      .filter((entry): entry is [string, ApprovedHybridCandidateItem] => entry[1] !== null),
  );

  return {
    itemCount: filteredItems.length,
    laneCounts,
    labelCounts,
    approvalSourceCounts,
    recommendedByLane,
    recommendedByLabel,
    items: filteredItems,
  };
}

async function loadInventoryReport() {
  const configuredPath = process.env.APP_APPROVED_HYBRID_INVENTORY_REPORT_PATH?.trim();
  const candidatePaths = [
    configuredPath,
    resolve(process.cwd(), DEFAULT_REPORT_RELATIVE_PATH),
    resolve(REPO_ROOT, DEFAULT_REPORT_RELATIVE_PATH),
  ].filter((value): value is string => Boolean(value));

  for (const path of candidatePaths) {
    try {
      const raw = await readFile(path, "utf-8");
      return JSON.parse(raw) as { items?: unknown };
    } catch {
      continue;
    }
  }

  throw new Error("HYBRID_INVENTORY_NOT_READY");
}

export async function GET(request: NextRequest) {
  try {
    const report = await loadInventoryReport();
    const label = request.nextUrl.searchParams.get("label");
    const serviceLane = request.nextUrl.searchParams.get("serviceLane");
    return ok(buildInventoryView(report, { label, serviceLane }));
  } catch {
    return fail("HYBRID_INVENTORY_NOT_READY", "승인된 hybrid inventory를 아직 읽을 수 없습니다.", 404);
  }
}
