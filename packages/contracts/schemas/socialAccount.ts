import type { Channel } from "../enums/channel";
import type { SocialAccountSummary } from "./common";

export interface SocialAccountsResponse {
  items: SocialAccountSummary[];
}

export interface ConnectSocialAccountResponse {
  channel: Channel;
  status: "connecting";
  redirectUrl: string;
}

export interface SocialAccountCallbackResponse {
  channel: Channel;
  status: "connected";
  socialAccountId: string;
}
