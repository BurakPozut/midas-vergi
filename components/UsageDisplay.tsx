'use client';

import { useEffect, useState } from 'react';
import { useSession } from "next-auth/react";

interface UsageDisplayProps {
  refreshTrigger?: number;
}

export default function UsageDisplay({ refreshTrigger = 0 }: UsageDisplayProps) {
  const { data: session } = useSession();
  const [usage, setUsage] = useState<number | null>(null);

  useEffect(() => {
    const fetchUsage = async () => {
      try {
        const response = await fetch('/api/user/usage');
        if (response.ok) {
          const data = await response.json();
          setUsage(data.usage);
        }
      } catch (error) {
        console.error('Failed to fetch usage:', error);
      }
    };

    if (session) {
      fetchUsage();
    }
  }, [session, refreshTrigger]);

  return (
    <div className="mb-4 text-center">
      <div className="inline-flex items-center px-4 py-2 rounded-lg bg-blue-50 text-blue-700">
        <span className="font-medium">Kalan Kullanım Hakkı:</span>
        <span className="ml-2 font-bold">{usage !== null ? usage : '...'}</span>
      </div>
    </div>
  );
} 