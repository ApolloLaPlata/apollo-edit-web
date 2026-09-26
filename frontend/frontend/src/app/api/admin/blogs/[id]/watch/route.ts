import { NextResponse } from 'next/server';

export async function POST(req: Request, props: { params: Promise<{ id: string }> }) {
  try {
    const params = await props.params;
    const blogId = params.id;
    const { videoUrl } = await req.json();

    if (!videoUrl || !videoUrl.includes('youtu')) {
      return NextResponse.json({ success: false, error: 'Link do YouTube inválido.' }, { status: 400 });
    }

    // Disparo assíncrono para não dar timeout
    import('@/lib/agents/social-watcher').then((watcher) => {
      watcher.executeWatcherPipeline(videoUrl, blogId).catch(console.error);
    });

    return NextResponse.json({ 
      success: true, 
      message: 'O Watcher iniciou a extração de comentários e a redação!' 
    });
  } catch (error: any) {
    console.error("Erro na rota do Watcher:", error);
    return NextResponse.json({ success: false, error: error.message }, { status: 500 });
  }
}
