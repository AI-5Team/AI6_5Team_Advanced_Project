import { Suspense } from "react";
import { SimpleWorkbench } from "@/components/simple-workbench";

export default function Page() {
  return (
    <Suspense fallback={<div className="app-shell" style={{ paddingTop: 32 }}>화면을 준비하고 있습니다.</div>}>
      <SimpleWorkbench />
    </Suspense>
  );
}
