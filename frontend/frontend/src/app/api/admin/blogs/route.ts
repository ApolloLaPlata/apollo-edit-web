import { NextResponse } from 'next/server';
import db from '@/lib/db';
import crypto from 'crypto';

export async function GET() {
  try {
    const blogsRaw = db.prepare(`
      SELECT 
        Blog.*, 
        AgentConfig.id as agentConfig_id, 
        AgentConfig.isActive as agentConfig_isActive, 
        AgentConfig.postFrequency as agentConfig_postFrequency,
        (SELECT COUNT(*) FROM Post WHERE Post.blogId = Blog.id) as posts_count
      FROM Blog
      LEFT JOIN AgentConfig ON AgentConfig.blogId = Blog.id
      ORDER BY Blog.createdAt DESC
    `).all();

    const blogs = blogsRaw.map((b: any) => ({
      ...b,
      agentConfig: b.agentConfig_id ? {
        id: b.agentConfig_id,
        isActive: b.agentConfig_isActive,
        postFrequency: b.agentConfig_postFrequency
      } : null,
      _count: { posts: b.posts_count }
    }));

    return NextResponse.json({ success: true, blogs });
  } catch (error) {
    console.error("Erro ao buscar blogs no admin:", error);
    return NextResponse.json({ success: false, error: "Falha ao carregar a frota" }, { status: 500 });
  }
}

export async function POST(req: Request) {
  try {
    const { name, domain, niche, postFrequency } = await req.json();
    if (!name || !domain || !niche) {
      return NextResponse.json({ success: false, error: "Nome, domínio e nicho são obrigatórios." }, { status: 400 });
    }

    const blogId = "cl" + crypto.randomUUID().replace(/-/g, "").substring(0, 23);
    const now = new Date().toISOString();
    
    // Inserção da Franquia no Banco SQLite
    db.prepare(`
      INSERT INTO Blog (id, domain, name, niche, description, theme, primaryColor, secondaryColor, layoutStyle, createdAt, updatedAt)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    `).run(
      blogId, 
      domain.toLowerCase().trim(), 
      name.trim(), 
      niche.trim(), 
      `Portal inteligente de notícias e análises sobre ${niche}.`, 
      "dark", 
      "#06b6d4", 
      "#3b82f6", 
      "modern", 
      now, 
      now
    );

    // Criação Automática do Agente Neural (Cortex) da Franquia
    const configId = "cl" + crypto.randomUUID().replace(/-/g, "").substring(0, 23);
    const defaultPrompt = `Você é o Diretor Editorial de Inteligência Artificial do portal ${name}. Seu objetivo é escrever artigos profundos, virais e otimizados em SEO no nicho de ${niche}.`;
    const defaultImagePrompt = "photorealistic, cinematic lighting, 8k resolution, highly detailed, editorial style";
    
    db.prepare(`
      INSERT INTO AgentConfig (id, blogId, personaPrompt, imageStylePrompt, isActive, postFrequency, createdAt, updatedAt)
      VALUES (?, ?, ?, ?, 1, ?, ?, ?)
    `).run(configId, blogId, defaultPrompt, defaultImagePrompt, Number(postFrequency || 3), now, now);

    return NextResponse.json({ success: true, blogId });
  } catch (error: any) {
    console.error("Erro ao criar nova franquia:", error);
    return NextResponse.json({ success: false, error: error.message || "Falha técnica ao provisionar o portal." }, { status: 500 });
  }
}
