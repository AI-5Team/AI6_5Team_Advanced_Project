export interface AssistPackage {
  mediaUrl: string;
  caption: string;
  hashtags: string[];
  thumbnailText?: string | null;
}

export interface AssistCompleteRequest {
  confirmedByUser: true;
  completedAt: string;
}

export interface AssistCompleteResponse {
  uploadJobId: string;
  status: "assisted_completed";
}
