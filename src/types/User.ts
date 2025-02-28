export interface UserResponse {
  id: number;
  username: string;
  email: string;
  display_name: string;
  admin: boolean;
  disabled: boolean;
  avatar_url?: string;
  last_login?: string;
}

export interface PublicUser {
  id: number;
  display_name: string;
  avatar_url?: string;
}
