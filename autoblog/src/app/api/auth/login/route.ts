import { NextResponse } from 'next/server';
import { cookies } from 'next/headers';

// Em produção, isso viria de variáveis de ambiente.
// O mesmo N8N_MASTER_KEY pode atuar como senha padrão da rede para o SSO Inicial.
const MASTER_KEY = process.env.N8N_MASTER_KEY || 'N8N_APOLLO_ROOT';

export async function POST(req: Request) {
  try {
    const { token } = await req.json();

    if (!token || token !== MASTER_KEY) {
       return NextResponse.json({ error: 'Credenciais Inválidas ou Token Expirado' }, { status: 401 });
    }

    // SSO Aprovado. Seta o Cookie Global Administrativo
    const cookieStore = await cookies();
    cookieStore.set('apollo_sso_token', token, {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'lax',
      maxAge: 60 * 60 * 24 * 7, // 7 dias
      path: '/'
    });

    return NextResponse.json({ success: true });
  } catch (err: any) {
    return NextResponse.json({ error: 'Erro Interno do Servidor' }, { status: 500 });
  }
}
