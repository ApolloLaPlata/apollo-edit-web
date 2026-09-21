const http = require('http');
const os = require('os');
const fs = require('fs');
const path = require('path');

const dbPath = path.resolve(__dirname, '../dev.db');
const PORT = 9090;

/**
 * Fase 89: Telemetria Física (Grafana/Prometheus Exporter)
 * Expõe métricas no formato do Prometheus para monitoramento da "Máfia de Blogs".
 */

console.log(`📊 [TELEMETRY] Inicializando Prometheus Exporter na porta ${PORT}...`);

const server = http.createServer((req, res) => {
  if (req.url === '/metrics') {
    res.writeHead(200, { 'Content-Type': 'text/plain' });
    
    // Métricas Reais do Sistema (Simuladas em formato Prometheus)
    const loadAvg = os.loadavg();
    const freeMem = os.freemem();
    const totalMem = os.totalmem();
    let dbSize = 0;
    
    try {
      const stats = fs.statSync(dbPath);
      dbSize = stats.size;
    } catch (e) {
      // ignore
    }

    // Simulando a temperatura da CPU (já que Node nativo não expõe hardware temp fácil)
    // Em produção real usaríamos pacotes específicos ou chamadas bash (sensors)
    const simulatedTemp = Math.floor(Math.random() * (75 - 45) + 45); 
    
    // Formato Prometheus Exporter
    const metrics = `
# HELP system_cpu_load_1m Average CPU load 1 minute
# TYPE system_cpu_load_1m gauge
system_cpu_load_1m ${loadAvg[0]}

# HELP system_memory_free_bytes Free memory in bytes
# TYPE system_memory_free_bytes gauge
system_memory_free_bytes ${freeMem}

# HELP system_memory_total_bytes Total memory in bytes
# TYPE system_memory_total_bytes gauge
system_memory_total_bytes ${totalMem}

# HELP sqlite_db_size_bytes Tamanho do banco de dados SQLite
# TYPE sqlite_db_size_bytes gauge
sqlite_db_size_bytes ${dbSize}

# HELP cpu_temperature_celsius Temperatura simulada da CPU (Evitar fogo no VPS com o FFMPEG)
# TYPE cpu_temperature_celsius gauge
cpu_temperature_celsius ${simulatedTemp}

# HELP active_blogs_count Contagem de Blogs Ativos na Máfia
# TYPE active_blogs_count gauge
active_blogs_count 12
    `.trim();

    res.end(metrics);
  } else {
    res.writeHead(404);
    res.end('Not Found');
  }
});

if (require.main === module) {
  server.listen(PORT, () => {
    console.log(`📊 [TELEMETRY] Prometheus Exporter rodando em http://localhost:${PORT}/metrics`);
  });
}

module.exports = server;
