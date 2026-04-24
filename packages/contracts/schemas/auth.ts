export interface AuthUser {
  id: string;
  email: string;
  name: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  name: string;
  birthDate: string;
  agreedToTerms: true;
  agreedToPrivacy: true;
  agreedToAge14: true;
  agreedToOverseasTransfer: true;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface AuthResponse {
  user: AuthUser;
}

export interface SessionResponse {
  user: AuthUser;
}

export interface MeResponse extends AuthUser {}
