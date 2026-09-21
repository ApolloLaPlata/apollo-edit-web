import React from 'react';
import TasksClient from './TasksClient';

export const dynamic = 'force-dynamic';

export default function AdminKanbanPage() {
  return (
    <div className="max-w-[1440px] mx-auto space-y-8 pb-16 animate-in fade-in duration-500">
      <TasksClient />
    </div>
  );
}
