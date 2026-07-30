import type { UploadSlim } from "@/types";
import { Platform } from "react-native";
import { postFile } from "./client";

export interface PickedImage {
  uri: string;
  fileName?: string | null;
  mimeType?: string | null;
}

/** Upload a picked image as multipart form data → Upload record. */
export async function uploadImage(asset: PickedImage): Promise<UploadSlim> {
  const name = asset.fileName ?? `photo-${Date.now()}.jpg`;
  const type = asset.mimeType ?? "image/jpeg";
  const form = new FormData();

  if (Platform.OS === "web") {
    // On web the picker returns a blob/data URI — materialize it into a File.
    const blob = await (await fetch(asset.uri)).blob();
    form.append("file", new File([blob], name, { type }));
  } else {
    // React Native FormData accepts a { uri, name, type } file descriptor.
    form.append("file", { uri: asset.uri, name, type } as unknown as Blob);
  }

  return postFile<UploadSlim>("/upload/", form);
}
