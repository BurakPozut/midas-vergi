'use client';

import { fileHandler } from "./actions/file-handler";


export default function Home() {

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      const formData = new FormData();
      formData.append('file', file);

      // const response = await fetch('/api/upload', {
      //   method: 'POST',
      //   body: formData,
      // });

      // const result = await response.json();
      const result = await fileHandler(formData);
      console.log(result); // Parsed PDF data
    }
  };

  return (
    <input type="file" onChange={handleFileUpload} />

  );
}
