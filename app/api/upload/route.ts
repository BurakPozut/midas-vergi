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
      return NextResponse.json({ error: "Yetkisiz erişim" }, { status: 401 });
    }

    const data = await req.formData();
    const files = data.getAll("files") as File[];

    if (!files || files.length === 0) {
      return NextResponse.json({ error: "Dosya seçilmedi" }, { status: 400 });
    }

    // Create a TransformStream for sending progress updates
    const stream = new TransformStream();
    const writer = stream.writable.getWriter();
    const encoder = new TextEncoder();

    // Start the response early
    const response = new Response(stream.readable, {
      headers: {
        "Content-Type": "text/event-stream",
        "Cache-Control": "no-cache",
        Connection: "keep-alive",
      },
    });

    // Process files in the background
    (async () => {
      try {
        // Create user-specific directory: uploads/[userId]
        const userUploadDir = join(process.cwd(), "uploads", userId);
        await fs.mkdir(userUploadDir, { recursive: true });

        for (let i = 0; i < files.length; i++) {
          const file = files[i];
          const isLastFile = i === files.length - 1;

          // Send upload start event
          await writer.write(
            encoder.encode(
              `data: ${JSON.stringify({
                type: "status",
                file: file.name,
                status: "processing_start",
              })}\n\n`
            )
          );

          // Validate file type
          if (file.type !== "application/pdf") {
            await writer.write(
              encoder.encode(
                `data: ${JSON.stringify({
                  type: "error",
                  file: file.name,
                  error: "PDF dosyası değil",
                })}\n\n`
              )
            );
            continue;
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

              pythonProcess.stdout.on("data", async (data: string) => {
                result += data;
                // Send processing progress event
                await writer.write(
                  encoder.encode(
                    `data: ${JSON.stringify({
                      type: "processing_progress",
                      file: file.name,
                      data: data.toString(),
                    })}\n\n`
                  )
                );
              });

              pythonProcess.stderr.on("data", async (data: string) => {
                error += data;
                console.error(`Python script error: ${data}`);
                await writer.write(
                  encoder.encode(
                    `data: ${JSON.stringify({
                      type: "error",
                      file: file.name,
                      error: "İşlem sırasında hata oluştu: " + data.toString(),
                    })}\n\n`
                  )
                );
              });

              pythonProcess.on("close", (code: number | null) => {
                if (code === 0) {
                  try {
                    const jsonResult = JSON.parse(result);
                    resolve(jsonResult as PythonResult);
                  } catch {
                    if (error) {
                      reject(new Error(error));
                    } else {
                      resolve({
                        success: true,
                        message: "İşlem başarıyla tamamlandı",
                        hasData: false,
                      });
                    }
                  }
                } else {
                  reject(new Error(error || "Python script çalıştırılamadı"));
                }
              });
            }
          );

          // Send completion event
          await writer.write(
            encoder.encode(
              `data: ${JSON.stringify({
                type: "status",
                file: file.name,
                status: "processing_complete",
                result: pythonResult,
              })}\n\n`
            )
          );

          // Clean up the file after processing
          try {
            await unlink(absoluteFilePath);
            if (isLastFile) {
              await fs.rm(userUploadDir, { recursive: true });
            }
          } catch (deleteError) {
            console.error(`Error during cleanup: ${deleteError}`);
          }
        }

        // Close the stream when all files are processed
        await writer.write(
          encoder.encode(`data: ${JSON.stringify({ type: "complete" })}\n\n`)
        );
        await writer.close();
      } catch (error) {
        await writer.write(
          encoder.encode(
            `data: ${JSON.stringify({
              type: "error",
              error:
                error instanceof Error ? error.message : "Dosya işleme hatası",
            })}\n\n`
          )
        );
        await writer.close();
      }
    })();

    return response;
  } catch (error) {
    console.error("Error in upload:", error);
    return NextResponse.json(
      { error: "Dosya yükleme hatası" },
      { status: 500 }
    );
  }
}

export const config = {
  api: {
    bodyParser: false,
  },
};
