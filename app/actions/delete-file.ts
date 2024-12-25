"use server";

import { unlink } from "fs/promises";
import { join } from "path";

export async function deleteFile(fileName: string) {
  try {
    const filePath = join(process.cwd(), "public/uploads", fileName);
    await unlink(filePath);
    return { success: true };
  } catch (error) {
    console.error("Error deleting file:", error);
    return { success: false, error: "Failed to delete file" };
  }
}
