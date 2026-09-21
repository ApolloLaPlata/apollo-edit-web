import { NextResponse } from 'next/server';
import os from 'os';
import db from '@/lib/db';

export async function GET() {
  try {
    const totalMem = os.totalmem();
    const freeMem = os.freemem();
    const usedMem = totalMem - freeMem;
    const memPerc = Math.min(100, Math.round((usedMem / totalMem) * 100));
    
    const usedMemMb = Math.round(usedMem / 1024 / 1024);
    
    const uptimeSeconds = process.uptime();
    const hours = Math.floor(uptimeSeconds / 3600);
    const minutes = Math.floor((uptimeSeconds % 3600) / 60);
    
    let uptimeStr = '';
    if (hours > 0) uptimeStr = `${hours}h ${minutes}m`;
    else if (minutes > 0) uptimeStr = `${minutes}m`;
    else uptimeStr = `${Math.floor(uptimeSeconds)}s`;

    const processMem = process.memoryUsage().rss;
    const processMemMb = Math.round(processMem / 1024 / 1024);
    const processMemPerc = Math.min(100, Math.round((processMem / totalMem) * 100));

    const startDb = performance.now();
    const totalPosts = (db.prepare('SELECT COUNT(*) as c FROM Post').get() as any)?.c || 0;
    const pendingQueue = (db.prepare('SELECT COUNT(*) as c FROM ContentQueue WHERE status = ?').get('pending') as any)?.c || 0;
    const activeLeads = (db.prepare('SELECT COUNT(*) as c FROM Subscriber').get() as any)?.c || 0;
    const dbLatency = Math.round((performance.now() - startDb) * 100) / 100;

    return NextResponse.json({
      success: true,
      stats: {
        memoryPercent: processMemPerc > 5 ? processMemPerc : memPerc,
        memoryLabel: `${processMemMb}MB`,
        uptime: uptimeStr,
        status: 'ONLINE',
        dbStatus: `ONLINE (<${Math.max(1, Math.ceil(dbLatency))}ms)`,
        totalPosts,
        pendingQueue,
        activeLeads
      }
    });
  } catch (error: any) {
    return NextResponse.json({ success: false, error: error.message }, { status: 500 });
  }
}
