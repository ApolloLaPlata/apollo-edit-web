import random

# Banco de dados de produtos "Achadinhos" simulado
# Em produção, isso pode vir de um banco de dados real ou API da Shopee/AliExpress
PRODUTOS_ACHADINHOS = [
    {
        "id": "ach_001",
        "nome": "Fone de Ouvido Bluetooth 5.3 com Cancelamento de Ruído",
        "preco": "R$ 49,90",
        "link": "https://s.click.aliexpress.com/e/_exemplo1",
        "imagem": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&w=300&q=80",
        "descricao": "O melhor custo-benefício para quem busca som de qualidade absurda. Sucesso de vendas!"
    },
    {
        "id": "ach_002",
        "nome": "Smartwatch Relógio Inteligente à Prova D'água",
        "preco": "R$ 89,00",
        "link": "https://s.click.aliexpress.com/e/_exemplo2",
        "imagem": "https://images.unsplash.com/photo-1579586337278-3befd40fd17a?auto=format&fit=crop&w=300&q=80",
        "descricao": "Monitore sua saúde e receba notificações direto no pulso. Bateria dura 7 dias."
    },
    {
        "id": "ach_003",
        "nome": "Mini Projetor Portátil Full HD 1080p Cinema em Casa",
        "preco": "R$ 199,99",
        "link": "https://s.click.aliexpress.com/e/_exemplo3",
        "imagem": "https://images.unsplash.com/photo-1620327318043-41dcaf12b185?auto=format&fit=crop&w=300&q=80",
        "descricao": "Transforme sua sala num verdadeiro cinema. Roda Netflix e YouTube nativo!"
    }
]

def gerar_banner_html(produto):
    """
    Gera o código HTML estilizado do banner do produto para ser injetado no Markdown.
    """
    html = f"""
    <div style="background: linear-gradient(135deg, #fdfbfb 0%, #ebedee 100%); border-left: 4px solid #ff4757; padding: 20px; margin: 30px 0; border-radius: 8px; display: flex; align-items: center; gap: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.05);">
        <img src="{produto['imagem']}" alt="{produto['nome']}" style="width: 120px; height: 120px; object-fit: cover; border-radius: 6px;" />
        <div style="flex: 1;">
            <div style="color: #ff4757; font-weight: bold; font-size: 12px; text-transform: uppercase; margin-bottom: 5px;">🔥 Achadinho Imperdível</div>
            <h4 style="margin: 0 0 10px 0; font-size: 18px; color: #2f3542;">{produto['nome']}</h4>
            <p style="margin: 0 0 15px 0; font-size: 14px; color: #57606f;">{produto['descricao']}</p>
            <div style="display: flex; align-items: center; gap: 15px;">
                <span style="font-weight: 900; font-size: 20px; color: #2ed573;">{produto['preco']}</span>
                <a href="{produto['link']}" target="_blank" style="background: #ff4757; color: white; padding: 8px 20px; border-radius: 20px; text-decoration: none; font-weight: bold; font-size: 14px; transition: background 0.3s;">Eu Quero! 🛒</a>
            </div>
        </div>
    </div>
    """
    return html

def injetar_banner_no_markdown(markdown_text):
    """
    Escolhe um produto aleatório e o injeta dinamicamente no meio do artigo.
    Por padrão, procura o primeiro subtítulo (##) ou quebra de parágrafo dupla.
    """
    if not PRODUTOS_ACHADINHOS:
        return markdown_text

    produto_escolhido = random.choice(PRODUTOS_ACHADINHOS)
    banner_html = gerar_banner_html(produto_escolhido)

    # Injeta o banner um pouco antes do [PAYWALL] se existir, 
    # caso contrário injeta no meio do texto baseando-se nas quebras de linha
    if "[PAYWALL]" in markdown_text:
        return markdown_text.replace("[PAYWALL]", banner_html + "\n\n[PAYWALL]")
    else:
        paragrafos = markdown_text.split("\n\n")
        meio = len(paragrafos) // 2
        if meio > 0:
            paragrafos.insert(meio, banner_html)
            return "\n\n".join(paragrafos)
        
    # Fallback: joga no final
    return markdown_text + "\n\n" + banner_html
