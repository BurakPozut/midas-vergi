import { writeFile, unlink } from "fs/promises";
import { NextResponse } from "next/server";
import { join } from "path";
import { auth } from "@/auth";
import fs from "fs/promises";
import { db } from "@/lib/prisma";

interface PythonResult {
  success: boolean;
  message?: string;
  error?: string;
  hasData?: boolean;
}

// Configuration for the Python API
const PYTHON_API_URL = process.env.PYTHON_API_URL || "http://localhost:5000";

export async function POST(req: Request) {
  try {
    const session = await auth();
    const userId = session?.user?.id;
    if (!userId) {
      return NextResponse.json({ error: "Yetkisiz erişim" }, { status: 401 });
    }

    // Check if user has enough usage left
    const user = await db.user.findUnique({
      where: { id: userId },
      select: { usage: true },
    });

    if (!user || user.usage <= 0) {
      return NextResponse.json(
        { error: "Kullanım hakkınız kalmadı." },
        { status: 403 }
      );
    }

    // Decrease usage by 1
    await db.user.update({
      where: { id: userId },
      data: { usage: { decrement: 1 } },
    });

    const data = await req.formData();
    const files = data.getAll("files") as File[];

    if (!files || files.length === 0) {
      return NextResponse.json({ error: "Dosya seçilmedi" }, { status: 400 });
    }

    // Check file count limit
    if (files.length > 36) {
      return NextResponse.json(
        { error: "En fazla 36 dosya yükleyebilirsiniz" },
        { status: 400 }
      );
    }

    // Calculate total size
    const totalSize = files.reduce((acc, file) => acc + file.size, 0);
    const maxSize = 1200 * 1024; // 1,200 KB in bytes

    if (totalSize > maxSize) {
      return NextResponse.json(
        { error: "Toplam dosya boyutu 1,200 KB'ı geçemez" },
        { status: 400 }
      );
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

          // Save the file to the uploads directory
          const bytes = await file.arrayBuffer();
          const buffer = Buffer.from(bytes);
          const filePath = join("uploads", userId, file.name);
          const absoluteFilePath = join(process.cwd(), filePath);
          await writeFile(absoluteFilePath, buffer);

          // Process file with Python API
          try {
            // Call the Python API with the file path and user ID
            const apiResponse = await fetch(`${PYTHON_API_URL}/process-file`, {
              method: "POST",
              headers: {
                "Content-Type": "application/json",
              },
              body: JSON.stringify({
                file_path: absoluteFilePath,
                user_id: userId,
              }),
            });

            if (!apiResponse.ok) {
              throw new Error(`API error: ${apiResponse.statusText}`);
            }

            // Parse the response
            const pythonResult: PythonResult = await apiResponse.json();

            // Send processing progress event
            await writer.write(
              encoder.encode(
                `data: ${JSON.stringify({
                  type: "processing_progress",
                  file: file.name,
                  data: "Processing completed",
                })}\n\n`
              )
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
            } catch (deleteError) {
              console.error(`Error deleting file: ${deleteError}`);
            }
          } catch (error) {
            console.error(`Error processing file with API: ${error}`);
            await writer.write(
              encoder.encode(
                `data: ${JSON.stringify({
                  type: "error",
                  file: file.name,
                  error:
                    error instanceof Error
                      ? error.message
                      : "API işleme hatası",
                })}\n\n`
              )
            );

            // Try to clean up the file even if processing failed
            try {
              await unlink(absoluteFilePath);
            } catch (deleteError) {
              console.error(`Error deleting file: ${deleteError}`);
            }
          }
        }

        // Clean up the user directory after processing all files
        try {
          await fs.rm(userUploadDir, { recursive: true, force: true });
        } catch (deleteError) {
          console.error(`Error during cleanup: ${deleteError}`);
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
