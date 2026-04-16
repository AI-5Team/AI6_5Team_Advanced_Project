import { SceneLabPageContent } from "@/components/scene-lab";
import { listScenePlanArtifacts } from "@/lib/scene-plan";

export default function SceneLabPage() {
  const scenePlanLinks = listScenePlanArtifacts().map((item) => ({
    href: `/scene-frame/${item.recommendedSceneIds[0]}?artifact=${item.key}`,
    label: item.title,
    summary: `${item.templateId} · ${item.purpose} 기준 실제 생성 artifact를 바로 렌더합니다.`,
  }));

  return <SceneLabPageContent scenePlanLinks={scenePlanLinks} />;
}
