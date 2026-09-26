/**
 * 🧑‍⚖️ AGENTE 3: O EDITOR-CHEFE
 * Função: O controle de qualidade (QC) do Enxame.
 * Ele analisa a fofoca gerada pelo Agente Sensacionalista e a compara com os Fatos do Jornalista.
 * Se o Sensacionalista viajou demais (Mentira processável) ou se o texto tá muito chato, 
 * o Editor REJEITA o post e devolve pro Sensacionalista refazer.
 */

class AgentEditor {
    constructor() {
        this.role = "Quality Assurance & Legal Filter";
        this.persona = "Crítico, Medroso com Processos, Exigente com Retenção.";
    }

    /**
     * Avalia o texto gerado. Retorna PASS (Aprovado) ou FAIL (Refazer).
     */
    async reviewArticle(sensationalistText, originalFacts) {
        console.log(`[EDITOR-CHEFE] 🧑‍⚖️ Lendo o lixo que o Sensacionalista escreveu...`);
        
        // Simulação de inferência (LLM de Autocorreção)
        await new Promise(resolve => setTimeout(resolve, 2000));
        
        // Simula uma Análise Semântica
        const isClickbaitEnough = sensationalistText.viralScore > 80;
        const mentionsLegalRisk = sensationalistText.body.includes("processo") || sensationalistText.body.includes("crime");

        console.log(`[EDITOR-CHEFE] 📝 Relatório: Choque=${sensationalistText.viralScore}/100 | Risco Jurídico=${mentionsLegalRisk ? 'ALTO' : 'BAIXO'}`);

        if (!isClickbaitEnough) {
            console.log(`[EDITOR-CHEFE] ❌ REJEITADO. O texto tá muito chato, parece Wikipédia. Mande refazer.`);
            return { status: "REJECTED", reason: "Falta Emoção." };
        }

        if (mentionsLegalRisk) {
            console.log(`[EDITOR-CHEFE] ❌ REJEITADO. Risco de Tomar Processo Alto. Remova afirmações literais de crime.`);
            return { status: "REJECTED", reason: "Risco Jurídico (Calúnia)." };
        }

        console.log(`[EDITOR-CHEFE] ✅ APROVADO! O texto tá venenoso e nos limites da lei. Pode publicar!`);
        return { status: "APPROVED", finalPost: sensationalistText };
    }
}

module.exports = AgentEditor;
