import { NextResponse } from 'next/server';
import db from '@/lib/db';

const MODULES = ['SWARM', 'DAEMON', 'SCRAPER', 'CRM', 'PAYWALL', 'SOCIAL'];
const SEVERITIES = ['INFO', 'INFO', 'INFO', 'INFO', 'WARN', 'ERROR', 'DEBUG'];

function generateMockLogs(count: number) {
  const logs = [];
  const now = Date.now();
  
  for (let i = 0; i < count; i++) {
    const mod = MODULES[Math.floor(Math.random() * MODULES.length)];
    const sev = SEVERITIES[Math.floor(Math.random() * SEVERITIES.length)];
    const timestamp = new Date(now - (i * Math.random() * 5000)).toISOString();
    
    let message = '';
    
    switch(mod) {
       case 'SWARM':
         message = sev === 'ERROR' ? 'Agent timeout during semantic search.' : 'Neural matrix updated context variables. Spawning Sub-agent.';
         break;
       case 'DAEMON':
         message = sev === 'WARN' ? 'High CPU load detected on text generation.' : 'Heartbeat OK. System normal.';
         break;
       case 'SCRAPER':
         message = 'Crawling target X for new YMYL gossip. 23 nodes found.';
         break;
       case 'CRM':
         message = 'Dispatched daily newsletter to 4,321 active leads.';
         break;
       case 'PAYWALL':
         message = 'Intercepted 3 unauthorized reading attempts. Conversion logic triggered.';
         break;
       case 'SOCIAL':
         message = 'Broadcasted new article to Telegram Mafia Channel.';
         break;
    }

    logs.push({
       id: `log-${now}-${i}`,
       timestamp,
       module: mod,
       severity: sev,
       message
    });
  }
  return logs.sort((a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime());
}

export async function GET(req: Request) {
  try {
    const { searchParams } = new URL(req.url);
    const lastId = searchParams.get('lastId');

    // MOCK: Generates 5-15 new logs every time if pooling
    // If it's the initial load (no lastId), generate 50 historical logs
    const logCount = lastId ? Math.floor(Math.random() * 5) + 1 : 50;
    const logs = generateMockLogs(logCount);

    // Let's also fetch the last 3 REAL posts to inject as [PUBLISHER] logs
    const recentPosts = db.prepare('SELECT title, createdAt FROM Post ORDER BY createdAt DESC LIMIT 3').all() as any[];
    
    if (!lastId && recentPosts.length > 0) {
        recentPosts.forEach((p, idx) => {
            logs.push({
               id: `real-log-${idx}`,
               timestamp: p.createdAt,
               module: 'PUBLISHER',
               severity: 'INFO',
               message: `Auto-published article: "${p.title}"`
            });
        });
        // Re-sort with real posts
        logs.sort((a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime());
    }

    return NextResponse.json({ success: true, logs });
  } catch (error: any) {
    return NextResponse.json({ success: false, error: error.message }, { status: 500 });
  }
}
