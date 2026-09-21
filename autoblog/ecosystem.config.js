module.exports = {
  apps: [
    {
      name: 'apollo-cms-web',
      script: 'npm',
      args: 'start',
      cwd: './',
      env: {
        NODE_ENV: 'production',
        PORT: 3000,
      },
      instances: 1,
      exec_mode: 'fork',
      autorestart: true,
      watch: false,
      max_memory_restart: '1G',
    },
    {
      name: 'apollo-daemon-writer',
      script: './src/scripts/daemon.js',
      cwd: './',
      env: {
        NODE_ENV: 'production',
      },
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '500M',
    },
    {
      name: 'apollo-telemetry-exporter',
      script: './src/scripts/metrics_exporter.js',
      cwd: './',
      env: {
        NODE_ENV: 'production',
        PORT: 9090,
      },
      instances: 1,
      autorestart: true,
      watch: false,
    },
    {
      name: 'apollo-ai-war',
      script: './src/scripts/ai_war/competitive_agents.js',
      cwd: './',
      cron_restart: '0 * * * *', // Roda a cada hora para disparar a briga por trends
      autorestart: false,
      watch: false,
    }
  ],
};
