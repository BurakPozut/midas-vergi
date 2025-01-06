import { writeFile } from "fs/promises";
import { NextResponse } from "next/server";
import { join } from "path";
import { auth } from "@/auth";
import { spawn } from "child_process";
import fs from "fs/promises";

export async function POST(req: Request) {
  try {
    const session = await auth();
    if (!session?.user?.id) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    const data = await req.formData();
    console.log("FormData received:", data);

    const file: File | null = data.get("file") as unknown as File;
    console.log("File object:", file?.name, file?.type);

    if (!file) {
      return NextResponse.json({ error: "No files provided" }, { status: 400 });
    }

    // Validate file type
    if (file.type !== "application/pdf") {
      return NextResponse.json(
        { error: "Only PDF files are allowed" },
        { status: 400 }
      );
    }

    const bytes = await file.arrayBuffer();
    const buffer = Buffer.from(bytes);

    // Create uploads directory if it doesn't exist
    const uploadDir = join(process.cwd(), "public", "uploads");
    try {
      await fs.mkdir(uploadDir, { recursive: true });
    } catch (err) {
      console.error("Error creating uploads directory:", err);
    }

    // Create path and write file
    const filePath = join("public", "uploads", file.name);
    console.log("Writing file to:", filePath);

    await writeFile(filePath, buffer);
    console.log("\n ---File written successfully");

    // Call Python script to extract tables with UTF-8 encoding
    const pythonProcess = spawn(
      "python",
      ["python/extract_tables.py", filePath, session.user.id],
      {
        env: {
          ...process.env,
          PYTHONIOENCODING: "utf-8",
          PYTHONLEGACYWINDOWSSTDIO: "1", // Add this for Windows
        },
      }
    );

    // Handle Python script output with UTF-8 encoding
    pythonProcess.stdout.setEncoding("utf-8");
    pythonProcess.stderr.setEncoding("utf-8");

    // Handle Python script output
    pythonProcess.stdout.on("data", (data) => {
      console.log(`Python script output: ${data}`);
    });

    pythonProcess.stderr.on("data", (data) => {
      console.error(`Python script error: ${data}`);
    });

    return NextResponse.json({
      success: true,
      message: "File uploaded and processing started",
    });
  } catch (error) {
    console.error("Error in upload:", error);
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
