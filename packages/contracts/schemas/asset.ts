export type AssetWarningCode =
  | "LOW_BRIGHTNESS"
  | "LOW_RESOLUTION"
  | "POSSIBLE_BLUR"
  | "OFF_CENTER_SUBJECT";

export interface UploadAssetInputFile {
  fileName: string;
  mimeType: string;
  sizeBytes: number;
}

export interface UploadAssetRequest {
  files: UploadAssetInputFile[];
}

export interface UploadedAssetItem {
  assetId: string;
  fileName: string;
  width: number;
  height: number;
  warnings: AssetWarningCode[];
}

export interface UploadAssetsResponse {
  projectId: string;
  assets: UploadedAssetItem[];
}
