import { NextResponse } from 'next/server';
import { uploadToGateway } from '@/lib/storage';

export async function POST(req: Request) {
  try {
    const formData = await req.formData();
    const file = formData.get('file') as File | null;
    const folder = formData.get('folder') as string || 'uploads';

    if (!file) {
      return NextResponse.json({ success: false, error: 'Nenhum arquivo enviado.' }, { status: 400 });
    }

    const buffer = Buffer.from(await file.arrayBuffer());
    const mimeType = file.type || 'application/octet-stream';
    const filename = file.name || 'uploaded_media';

    const url = await uploadToGateway(buffer, filename, mimeType, folder);

    return NextResponse.json({
      success: true,
      abstract_url: url
    });
  } catch (error: any) {
    console.error("[API/MEDIA] Erro ao enviar mídia:", error);
    return NextResponse.json({ success: false, error: error.message }, { status: 500 });
  }
}
