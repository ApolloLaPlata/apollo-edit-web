const AgentJournalist = require('./agent_journalist');
const AgentSensationalist = require('./agent_sensationalist');
const AgentEditor = require('./agent_editor');

/**
 * 🔺 O TRIÂNGULO DOURADO (Swarm Engine V6)
 * O coração da Redação Neural. 
 * Conecta os 3 Agentes num Loop de Auto-Correção.
 */

async function runSwarmEngine(targetUrl) {
    console.log('=============================================');
    console.log('🧠 [SWARM ENGINE] REDAÇÃO NEURAL ONLINE...');
    console.log('=============================================');

    const jornalista = new AgentJournalist();
    const sensacionalista = new AgentSensationalist();
    const editor = new AgentEditor();

    try {
        // PASSO 1: Extração Fria
        const research = await jornalista.extractFacts(targetUrl);
        
        let finalApprovedPost = null;
        let iteration = 1;
        const MAX_RETRIES = 3;

        // O LOOP DE REDAÇÃO (As I.As brigam entre si até ficar perfeito)
        while (!finalApprovedPost && iteration <= MAX_RETRIES) {
            console.log(`\n🔄 [SWARM] Iniciando Draft (Rascunho) - Iteração ${iteration}...`);
            
            // PASSO 2: Escrita Venenosa
            const draft = await sensacionalista.spinStory(research.facts);
            
            // PASSO 3: Controle de Qualidade
            const review = await editor.reviewArticle(draft, research.facts);

            if (review.status === "APPROVED") {
                finalApprovedPost = review.finalPost;
                console.log(`\n🏆 [SWARM] SUCESSO! Artigo Aprovado pelo Editor na Tentativa ${iteration}.`);
            } else {
                console.log(`\n⚠️ [SWARM] FALHA. Editor reprovou: "${review.reason}". Sensacionalista vai reescrever...`);
                iteration++;
            }
        }

        if (finalApprovedPost) {
            console.log(`\n✅ [SWARM] RESULTADO FINAL PRONTO PARA POSTAR:`);
            console.log(`MANCHETE: ${finalApprovedPost.headline}`);
            // Aqui enviaria pro Banco de Dados SQLite (D1)
        } else {
            console.error(`\n❌ [SWARM] ABORTO. Os agentes não entraram em consenso após ${MAX_RETRIES} tentativas.`);
        }

    } catch (err) {
        console.error('[SWARM] ❌ Pânico no Enxame.', err);
    }
}

if (require.main === module) {
    runSwarmEngine("https://fofoca-exemplo.com/materia-vazada");
}

module.exports = { runSwarmEngine };
