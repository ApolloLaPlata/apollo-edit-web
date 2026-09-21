/**
 * 🧛‍♂️ AGENTE 2: O SENSACIONALISTA (O Veneno)
 * Função: Pegar os fatos chatos e crus do Agente Jornalista e transformá-los 
 * em uma bomba atômica de dopamina e clickbait psicológico.
 */

class AgentSensationalist {
    constructor() {
        this.role = "Clickbait & Psychological Manipulation";
        this.persona = "Venenoso, Urgente, Indignado, Estilo Tablóide.";
    }

    /**
     * Pega os fatos do jornalista e devolve o texto sujo.
     */
    async spinStory(factsArray) {
        console.log(`[SENSACIONALISTA] 🧛‍♂️ Recebendo fatos crus. Hora de injetar o veneno...`);
        
        // Simulação de delay (LLM Inference)
        await new Promise(resolve => setTimeout(resolve, 2000));
        
        const generatedHeadline = "TRAIÇÃO NO FASANO?! A prova que faltava do fim do casamento de ouro 🚨💔";
        
        const generatedBody = `
MÁSCARAS CAÍRAM! Vocês acharam mesmo que aquele casamento de comercial de margarina ia durar? 
Nossas fontes infiltradas flagraram a atriz e o bonitão num jantar pra lá de íntimo, Tarde da Noite, 
no restaurante mais caro de SP. O detalhe que chocou todo mundo? NENHUM DOS DOIS usava aliança! 
É o fim da linha. Eles até tentaram disfarçar saindo separados, mas a gente sabe muito bem 
onde os dois carros foram parar depois... 👀🔥
        `.trim();

        console.log(`[SENSACIONALISTA] ☠️ Manchete forjada: "${generatedHeadline}"`);
        
        return {
            headline: generatedHeadline,
            body: generatedBody,
            viralScore: 99.8 // Potencial de clique
        };
    }
}

module.exports = AgentSensationalist;
