---
name: observador-economico-checagem-atual
description: Verifica atualidade e confiabilidade de dados economicos, fiscais e contabeis para conteudos do Observador Economico. Use quando a tarefa envolver IPCA, Selic, Focus, inflacao, precos, tarifas, cambio, cesta basica, NF-e, DANFE, CFOP, normas contabeis, leis, dados de 2026 ou qualquer informacao que possa mudar.
---

# Observador Economico - Checagem Atual

## Quando usar

Use antes de roteirizar ou publicar conteudo com dados instaveis.

## Entradas esperadas

- Dado, afirmacao ou pauta a verificar.
- Tipo de dado: economico, fiscal, contabil ou plataforma.
- Data pretendida de publicacao.
- Nivel de detalhe desejado.

## Fontes prioritarias

- IBGE/SIDRA para IPCA e pesos.
- Banco Central/Focus para expectativas de mercado.
- Banco Central/SGS para series historicas.
- Portal Nacional da NF-e para NF-e, DANFE e chave de acesso.
- Conselho Federal de Contabilidade para normas contabeis.
- Receita/SEFAZ/gov.br quando houver assunto fiscal especifico.

## Processo

1. Separar conceito estavel de dado atual.
2. Buscar fonte primaria ou oficial.
3. Registrar data da consulta.
4. Comparar se o dado local antigo ainda faz sentido.
5. Transformar numero em linguagem de cenario, nao certeza.
6. Incluir cautela quando houver estimativa.

## Linguagem recomendada

Use:

- "Segundo [fonte], consultado em [data]..."
- "A mediana/projecao indica..."
- "Esse dado pode mudar em novos boletins..."
- "Este conteudo tem finalidade educacional..."

Evite:

- "vai acontecer";
- "com certeza";
- "garantido";
- "o preco sera";
- "a Selic vai";
- previsao sem fonte.

## Saida padrao

- Veredito: confirmado, precisa atualizar, ou usar como hipotese.
- Fonte primaria recomendada.
- Data da consulta.
- Formula de linguagem segura.
- Alertas de risco.

## Checklist de qualidade

- Usou fonte oficial quando possivel.
- Separou conceito de numero atual.
- Citou data.
- Nao tratou projecao como fato.
- Marcou incertezas.
