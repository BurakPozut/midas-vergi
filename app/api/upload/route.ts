import { writeFile, unlink } from "fs/promises";
import { NextResponse } from "next/server";
import { join } from "path";
import { auth } from "@/auth";
import { spawn } from "child_process";
import type { ChildProcessWithoutNullStreams } from "child_process";
import fs from "fs/promises";

interface PythonResult {
  success: boolean;
  message?: string;
  error?: string;
  hasData?: boolean;
}

export async function POST(req: Request) {
  try {
    const session = await auth();
    const userId = session?.user?.id;
    if (!userId) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    const data = await req.formData();
    const files = data.getAll("files") as File[];

    if (!files || files.length === 0) {
      return NextResponse.json({ error: "No files provided" }, { status: 400 });
    }

    // Create user-specific directory: uploads/[userId]
    const userUploadDir = join(process.cwd(), "uploads", userId);
    try {
      await fs.mkdir(userUploadDir, { recursive: true });
    } catch (err) {
      console.error("Error creating user upload directory:", err);
      return NextResponse.json(
        { error: "Failed to create upload directory" },
        { status: 500 }
      );
    }

    const results = [];
    for (let i = 0; i < files.length; i++) {
      const file = files[i];
      const isLastFile = i === files.length - 1;

      // Validate file type
      if (file.type !== "application/pdf") {
        return NextResponse.json(
          { error: `File ${file.name} is not a PDF` },
          { status: 400 }
        );
      }

      const bytes = await file.arrayBuffer();
      const buffer = Buffer.from(bytes);

      // Create path and write file in user's directory
      const filePath = join("uploads", userId, file.name);
      const absoluteFilePath = join(process.cwd(), filePath);
      await writeFile(absoluteFilePath, buffer);

      // Process file with Python script
      const pythonResult = await new Promise<PythonResult>(
        (resolve, reject) => {
          let result = "";
          let error = "";

          const pythonProcess = spawn("python", [
            "python/extract_tables.py",
            absoluteFilePath,
            userId,
          ]) as ChildProcessWithoutNullStreams;

          pythonProcess.stdout.setEncoding("utf-8");
          pythonProcess.stderr.setEncoding("utf-8");

          pythonProcess.stdout.on("data", (data: string) => {
            result += data;
          });

          pythonProcess.stderr.on("data", (data: string) => {
            error += data;
            console.error(`Python script error: ${data}`);
          });

          pythonProcess.on("close", (code: number | null) => {
            if (code === 0) {
              try {
                // Try to parse the result as JSON
                const jsonResult = JSON.parse(result);
                resolve(jsonResult as PythonResult);
              } catch {
                // If parsing fails, check if there were any errors
                if (error) {
                  reject(new Error(error));
                } else {
                  resolve({
                    success: true,
                    message: "Processing completed successfully",
                    hasData: false,
                  });
                }
              }
            } else {
              reject(new Error(error || "Python script failed"));
            }
          });
        }
      );

      if (!pythonResult.success) {
        return NextResponse.json(
          {
            error: pythonResult.error || `Failed to process file ${file.name}`,
          },
          { status: 500 }
        );
      }

      // Clean up the file after processing
      try {
        await unlink(absoluteFilePath);
        console.log(`Deleted file: ${absoluteFilePath}`);

        // Delete directory after processing last file
        if (isLastFile) {
          await fs.rm(userUploadDir, { recursive: true });
          console.log(`Deleted directory: ${userUploadDir}`);
        }
      } catch (deleteError) {
        console.error(`Error during cleanup: ${deleteError}`);
      }

      results.push({
        fileName: file.name,
        message: pythonResult.message || "File processed successfully",
        hasData: pythonResult.hasData,
      });
    }

    return NextResponse.json({
      success: true,
      results,
    });
  } catch (error) {
    console.error("Error in upload:", error);
    return NextResponse.json(
      { error: "Error uploading files" },
      { status: 500 }
    );
  }
}

export const config = {
  api: {
    bodyParser: false,
  },
};
