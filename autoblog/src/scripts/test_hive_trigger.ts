import { executeAutonomousEditorialCycle } from './src/lib/agents/autonomous_engine';
async function runTest() {
  console.log('?? INICIANDO GATILHO DA COLMEIA...');
  try {
    const result = await executeAutonomousEditorialCycle();
    console.log('? CICLO COMPLETADO:', result);
  } catch(e) { console.error('? ERRO:', e); }
}
runTest();
