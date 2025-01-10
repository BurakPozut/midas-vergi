'use client';

import FileUploader from '@/components/FileUploader';
import FlickeringGrid from '@/components/ui/flickering-grid';
import { useSession } from "next-auth/react";

export default function TaxPage() {
  const { status } = useSession();

  if (status === "loading") {
    return (
      <div className="relative min-h-screen bg-gradient-to-b from-gray-900 to-navy-900 flex items-center justify-center">
        <FlickeringGrid
          className="z-0 absolute inset-0 [mask-image:radial-gradient(450px_circle_at_center,white,transparent)]"
          squareSize={4}
          gridGap={6}
          color="#60A5FA"
          maxOpacity={0.5}
          flickerChance={0.1}
        />
        <div className="animate-pulse flex space-x-4 items-center">
          <div className="h-3 w-3 bg-blue-400 rounded-full"></div>
          <div className="text-lg text-gray-400">Yükleniyor...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="relative min-h-screen bg-gradient-to-b from-gray-900 to-navy-900">
      <FlickeringGrid
        className="z-0 absolute inset-0 [mask-image:radial-gradient(450px_circle_at_center,white,transparent)]"
        squareSize={4}
        gridGap={6}
        color="#60A5FA"
        maxOpacity={0.5}
        flickerChance={0.1}
      />
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-28">
        <div className="text-center space-y-8 mb-16">
          <h1 className="animate-fade-in text-5xl md:text-6xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-emerald-400">
            Vergi Hesaplama
          </h1>
          <p className="animate-fade-in animation-delay-200 text-gray-400 text-lg md:text-xl max-w-2xl mx-auto">
            Dökümanlarınızı yükleyin ve vergi hesaplamanızı otomatik olarak yapalım.
          </p>
        </div>

        <div className="animate-fade-in animation-delay-400 bg-gray-800 rounded-lg p-8 shadow-xl">
          <FileUploader />
        </div>
      </div>
    </div>
  );
} 