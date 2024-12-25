import { NextResponse } from "next/server";
import { writeFile } from "fs/promises";
import { join } from "path";

export async function POST(request: Request) {
  try {
    const formData = await request.formData();
    const files = formData.getAll("files");

    if (!files || files.length === 0) {
      return NextResponse.json(
        { error: "No files received." },
        { status: 400 }
      );
    }

    const uploadPromises = files.map(async (file: any) => {
      const bytes = await file.arrayBuffer();
      const buffer = Buffer.from(bytes);

      // Create uploads directory if it doesn't exist
      const uploadDir = join(process.cwd(), "public/uploads");

      // Save the file
      const filePath = join(uploadDir, file.name);
      await writeFile(filePath, buffer);

      return { fileName: file.name, path: `/uploads/${file.name}` };
    });

    const savedFiles = await Promise.all(uploadPromises);

    return NextResponse.json({
      message: "Files uploaded successfully",
      files: savedFiles,
    });
  } catch (error) {
    console.error("Error uploading file:", error);
    return NextResponse.json(
      { error: "Error uploading file" },
      { status: 500 }
    );
  }
}

export const config = {
  api: {
    bodyParser: false,
  },
};
