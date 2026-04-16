import { HistoryBoard } from "@/components/history-board";

export default async function HistoryPage({
  searchParams,
}: {
  searchParams: Promise<{ projectId?: string }>;
}) {
  const params = await searchParams;
  return <HistoryBoard initialProjectId={params.projectId ?? null} />;
}
