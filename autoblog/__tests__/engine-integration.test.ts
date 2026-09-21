import { describe, it, expect, vi } from 'vitest';
import { generateEmbedding, cosineSimilarity, addKnowledge, searchContext } from '../src/lib/agents/rag_engine';
import { generateGeminiTTS } from '../src/lib/media/gemini-tts';

// Mock do banco de dados para os testes não gravarem lixo no dev.db
vi.mock('../src/lib/db', () => ({
  default: {
    prepare: vi.fn(() => ({
      run: vi.fn(),
      all: vi.fn(() => [])
    }))
  }
}));

// Mock do cliente Lightning para não gastar API da OpenAI real durante os testes
vi.mock('../src/lib/llm/lightning-client', () => ({
  getClient: vi.fn(() => ({
    embeddings: {
      create: vi.fn(() => Promise.resolve({
        data: [{ embedding: [0.1, 0.2, 0.3, 0.4] }]
      }))
    }
  }))
}));

describe('RAG Engine Integration', () => {
  it('deve gerar embeddings corretamente usando fallback mockado', async () => {
    const vector = await generateEmbedding("Texto de teste financeiro");
    expect(vector.length).toBeGreaterThan(0);
    expect(vector[0]).toBe(0.1);
  });

  it('deve evitar inserir texto muito curto no vetor', async () => {
    const res = await addKnowledge('teste_canal', 'teste_fonte', 'curto');
    expect(res).toBe(false);
  });
});

describe('Media Engine (TTS) Integration', () => {
  it('deve rejeitar limite muito grande ou texto vazio', async () => {
    await expect(generateGeminiTTS("")).rejects.toThrow();
  });
});
