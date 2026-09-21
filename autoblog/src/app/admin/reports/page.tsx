import React from 'react';
import ReportsClient from './ReportsClient';

export const dynamic = 'force-dynamic';

export default function ReportsPage() {
  return (
    <div className="max-w-[1440px] mx-auto space-y-8 pb-16 animate-in fade-in duration-500">
      <ReportsClient />
    </div>
  );
}
