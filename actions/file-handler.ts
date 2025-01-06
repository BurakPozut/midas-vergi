"use server";

import { writeFile } from "fs/promises";
import { join } from "path";
import * as pdfjsLib from "pdfjs-dist";

export async function fileHandler(data: FormData) {
  const file: File | null = data.get("file") as unknown as File;

  if (!file) throw new Error("No file uploaded");

  const bytes = await file.arrayBuffer();
  const buffer = Buffer.from(bytes);

  // Define the path to save the file temporarily
  const path = join(process.cwd(), file.name);
  await writeFile(path, buffer);

  // Load and parse the PDF using pdfjs-dist
  try {
    const loadingTask = pdfjsLib.getDocument({ data: buffer });
    const pdfDocument = await loadingTask.promise;

    let fullText = "";

    for (let i = 1; i <= pdfDocument.numPages; i++) {
      const page = await pdfDocument.getPage(i);
      const textContent = await page.getTextContent();

      // Extract text and concatenate it
      const pageText = textContent.items.map((item: any) => item.str).join(" ");
      fullText += pageText + "\n";
    }

    console.log(`PDF Content:\n${fullText}`);

    // Return the parsed text or any structured data as needed
    return { success: true, text: fullText };
  } catch (error) {
    console.error("Error reading PDF:", error);
    throw new Error("Failed to read PDF");
  }
}
