import type { UserResponse } from "@/types";
import { put } from "./client";

export function updateUser(
  userId: number,
  body: { display_name?: string }
): Promise<UserResponse> {
  return put<UserResponse>(`/user/${userId}/`, body);
}
