import { Metadata } from 'next';
import Link from 'next/link';
import db from '@/lib/db';
import Footer from '@/components/blog/Footer';

export async function generateMetadata(props: { params: Promise<{ domain: string, slug: string }> }): Promise<Metadata> {
  const params = await props.params;
  const decodedDomain = decodeURIComponent(params.domain);
  const slug = decodeURIComponent(params.slug);

  let blogMeta = db.prepare('SELECT * FROM Blog WHERE domain = ?').get(decodedDomain) as any;
  if (!blogMeta && decodedDomain.includes('localhost')) {
    blogMeta = db.prepare('SELECT * FROM Blog LIMIT 1').get() as any;
  }
  
  const titleMap: any = {
    'sobre-nos': 'Sobre Nós',
    'politica-de-privacidade': 'Política de Privacidade',
    'termos-de-uso': 'Termos de Uso'
  };

  const pageTitle = titleMap[slug] || 'Página Institucional';

  return {
    title: `${pageTitle} | ${blogMeta?.name || 'Portal'}`,
    description: `Leia as informações sobre ${pageTitle} do ${blogMeta?.name || 'nosso portal'}.`,
    robots: { index: true, follow: true }
  };
}

export default async function InstitutionalPage(props: { params: Promise<{ domain: string, slug: string }> }) {
  const params = await props.params;
  const decodedDomain = decodeURIComponent(params.domain);
  const slug = decodeURIComponent(params.slug);
  
  let blogMeta = db.prepare('SELECT * FROM Blog WHERE domain = ?').get(decodedDomain) as any;
  if (!blogMeta && decodedDomain.includes('localhost')) {
    blogMeta = db.prepare('SELECT * FROM Blog LIMIT 1').get() as any;
  }
  const themeClass = blogMeta?.theme ? `theme-${blogMeta.theme}` : 'theme-dark';
  const blogName = blogMeta?.name || 'O Portal';
  const domainUrl = `https://${decodedDomain}`;

  let content = '';
  let title = '';

  if (slug === 'sobre-nos') {
    title = 'Sobre Nós';
    content = `
      <h2>Quem Somos</h2>
      <p>Bem-vindo ao <strong>${blogName}</strong>. Somos um portal dedicado a fornecer informações, análises e as últimas novidades sobre o nosso nicho de atuação.</p>
      <p>Nosso objetivo é democratizar o acesso à informação de qualidade, utilizando tecnologias de ponta e curadoria especializada para garantir que você receba o conteúdo mais relevante e atualizado.</p>
      
      <h2>Nossa Missão</h2>
      <p>Nossa missão é informar, educar e inspirar nossos leitores todos os dias. Acreditamos que a informação tem o poder de transformar vidas e moldar o futuro.</p>
      
      <h2>Contato</h2>
      <p>Se você deseja entrar em contato conosco para sugerir pautas, fechar parcerias comerciais ou tirar dúvidas, envie um e-mail para <strong>contato@${decodedDomain}</strong>.</p>
    `;
  } else if (slug === 'politica-de-privacidade') {
    title = 'Política de Privacidade';
    content = `
      <h2>1. Coleta de Informações</h2>
      <p>O <strong>${blogName}</strong> coleta informações pessoais que você nos fornece voluntariamente, como nome e e-mail ao se inscrever na nossa newsletter, além de dados de navegação automaticamente coletados através de cookies (como endereço IP, tipo de navegador e páginas visitadas).</p>
      
      <h2>2. Uso das Informações</h2>
      <p>As informações coletadas são utilizadas para:</p>
      <ul>
        <li>Personalizar sua experiência no site;</li>
        <li>Melhorar nosso conteúdo e interface;</li>
        <li>Enviar e-mails periódicos (caso você tenha se inscrito);</li>
        <li>Processar eventuais transações.</li>
      </ul>
      
      <h2>3. Proteção das Informações</h2>
      <p>Implementamos uma variedade de medidas de segurança para manter a segurança de suas informações pessoais. Utilizamos criptografia avançada para proteger informações sensíveis transmitidas online e offline.</p>
      
      <h2>4. Uso de Cookies (Google AdSense e outros)</h2>
      <p>Nós utilizamos cookies para melhorar o acesso ao nosso site. Além disso, fornecedores terceiros, incluindo o Google, usam cookies para veicular anúncios com base em visitas anteriores do usuário ao <strong>${blogName}</strong> ou a outros websites.</p>
      <p>O uso de cookies de publicidade permite que o Google e seus parceiros veiculem anúncios para os usuários com base nas visitas feitas aos seus sites e/ou a outros sites na Internet. Você pode desativar a publicidade personalizada acessando as <a href="https://www.google.com/settings/ads" target="_blank" rel="nofollow">Configurações de anúncios do Google</a>.</p>
      
      <h2>5. Consentimento</h2>
      <p>Ao utilizar nosso site, você concorda com nossa Política de Privacidade.</p>
    `;
  } else if (slug === 'termos-de-uso') {
    title = 'Termos de Uso';
    content = `
      <h2>1. Aceitação dos Termos</h2>
      <p>Ao acessar e usar o site <strong>${blogName}</strong> (${domainUrl}), você aceita e concorda em cumprir estes Termos de Uso. Se você não concorda com qualquer parte destes termos, não deve usar nosso site.</p>
      
      <h2>2. Uso de Conteúdo</h2>
      <p>O conteúdo presente no <strong>${blogName}</strong> é protegido por direitos autorais e outras leis de propriedade intelectual. Você pode visualizar, baixar para armazenamento temporário e imprimir páginas do site para uso pessoal, mas não comercial.</p>
      
      <h2>3. Isenção de Responsabilidade</h2>
      <p>Os materiais no site são fornecidos "como estão". O <strong>${blogName}</strong> não oferece garantias, expressas ou implícitas, e, por este meio, isenta e nega todas as outras garantias, incluindo, sem limitação, garantias implícitas ou condições de comercialização, adequação a um fim específico ou não violação de propriedade intelectual ou outra violação de direitos.</p>
      
      <h2>4. Limitações</h2>
      <p>Em nenhum caso o <strong>${blogName}</strong> ou seus fornecedores serão responsáveis por quaisquer danos (incluindo, sem limitação, danos por perda de dados ou lucro, ou devido à interrupção dos negócios) decorrentes do uso ou da incapacidade de usar os materiais no site.</p>
      
      <h2>5. Alterações nos Termos</h2>
      <p>O <strong>${blogName}</strong> pode revisar estes termos de uso para seu site a qualquer momento sem aviso prévio. Ao usar este site, você concorda em ficar vinculado à versão atual desses Termos de Uso.</p>
    `;
  } else {
    title = 'Página Não Encontrada';
    content = '<p>O documento que você está procurando não existe ou foi removido.</p>';
  }

  return (
    <main className={`flex min-h-screen flex-col bg-theme-bg theme-transition text-theme-text ${themeClass}`}>
      
      {/* HEADER NAVBAR PREMIUM */}
      <nav className="sticky top-0 w-full z-50 transition-all duration-300 bg-theme-bg/50 backdrop-blur-md border-b border-theme-border/50 py-4 shadow-xl">
        <div className="max-w-7xl mx-auto px-4 py-2 flex justify-between items-center">
          <Link href={`/`} className="flex items-center gap-2">
            <div className="w-8 h-8 bg-theme-accent rounded flex items-center justify-center">
              <span className="text-theme-text font-bold font-serif text-sm">{blogMeta?.name?.charAt(0) || "O"}</span>
            </div>
            <span className="font-bold text-xl tracking-tight text-theme-text uppercase">
              {blogMeta?.name}
            </span>
          </Link>
          <Link href={`/`} className="text-sm font-semibold text-theme-accent hover:text-theme-accent-hover transition-colors">
            Voltar ao Blog
          </Link>
        </div>
      </nav>

      {/* CONTENT */}
      <div className="w-full max-w-4xl mx-auto px-4 py-16">
        <div className="bg-theme-surface/80 backdrop-blur-md border border-theme-border/50 rounded-3xl p-8 md:p-12 shadow-2xl">
          <h1 className="text-4xl md:text-5xl font-black text-theme-text mb-8 border-b border-theme-border/50 pb-6">
            {title}
          </h1>
          <div 
            className="prose prose-invert prose-lg max-w-none 
                       prose-h2:text-theme-accent prose-h2:font-bold prose-h2:border-b prose-h2:border-theme-border/50 prose-h2:pb-2 prose-h2:mt-10
                       prose-p:text-theme-muted prose-p:leading-relaxed prose-p:font-medium
                       prose-a:text-theme-accent prose-a:no-underline hover:prose-a:underline
                       prose-ul:text-theme-muted prose-li:marker:text-theme-accent"
            dangerouslySetInnerHTML={{ __html: content }} 
          />
        </div>
      </div>

      <Footer domain={decodedDomain} name={blogMeta?.name} />
    </main>
  );
}
