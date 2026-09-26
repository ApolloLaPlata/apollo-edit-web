import { test, expect } from '@playwright/test';

// Fase 92: Testes E2E Playwright
// Este teste garante que a Máfia de Blogs nunca caia devido a deploys quebrados.

test('Verifica se o Painel Admin carrega corretamente', async ({ page }) => {
  // Vamos para a rota de admin
  await page.goto('http://localhost:3000/admin');
  
  // Como estamos testando o CMS, verificamos o título da página principal
  await expect(page).toHaveTitle(/Apollo/);

  // Verifica se o texto do Dashboard Global do CMS está renderizando
  const dashboardHeading = page.locator('h1', { hasText: 'Apollo CMS' });
  await expect(dashboardHeading).toBeVisible({ timeout: 10000 });
});

test('Escudo Anti-Bot no Middleware (Fase 84)', async ({ request }) => {
  // Envia um User-Agent proibido (scrapy) e espera 403 Forbidden
  const response = await request.get('http://localhost:3000', {
    headers: {
      'User-Agent': 'scrapy bot'
    }
  });
  
  expect(response.status()).toBe(403);
});
