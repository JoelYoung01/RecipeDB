export interface UserResponse {
  id: number;
  username: string;
  email: string;
  display_name: string;
  admin: boolean;
  disabled: boolean;
  avatar_url?: string;
}
