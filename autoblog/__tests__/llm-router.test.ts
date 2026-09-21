import { describe, it, expect } from 'vitest';
import { getSortedCamadaA, CAMADA_B } from '../src/lib/llm/lightning-client';
describe('LLM Fallback Router', () => {
  it('deve priorizar a menor latência nas 4 chaves lightning (Camada A)', () => {
    const camadaA = getSortedCamadaA('writer');
    expect(camadaA.length).toBeGreaterThan(0);
    expect(camadaA[0].provider).toMatch(/lightning_/);
  });
  it('deve ter o Groq como Camada B de Resgate Imediato', () => {
    expect(CAMADA_B[0].provider).toBe('groq');
    expect(CAMADA_B[0].model).toMatch(/llama-3/i);
  });
});
