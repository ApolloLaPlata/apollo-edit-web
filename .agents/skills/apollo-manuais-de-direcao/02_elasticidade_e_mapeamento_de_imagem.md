# O MANUAL DO PILOTO - APOLLO STUDIO
## 02: A Lógica da Elasticidade de Mapeamento

### Como o Editor Junta Peças
O Apollo Studio funciona à base de "Elasticidade do Mapeamento". Isso significa que o texto da Locução (TTS) ou da Fala dita o tempo de duração da cena.

### O Gatilho do Corte de Imagem
Quando você desenha um roteiro, o fechamento de um bloco de palavra (um "Enter" ou o fim de uma sentença) é o **gatilho matemático** que o Editor usa para dar um corte na imagem e carregar o próximo Vídeo Base ou Template que você mapeou na lista.

**Exemplo Prático da Elasticidade:**
Se você forneceu uma lista com 3 Vídeos Base:
1. `01_carro.mp4`
2. `02_oficina.mp4`
3. `03_estrada.mp4`

Seu texto do roteiro precisa ser dividido rigidamente em 3 blocos/parágrafos correspondentes:

```text
[BLOCO DE FALA 1 - Mapeia com 01_carro.mp4]
O carro da família parou de funcionar de repente na rodovia.

[BLOCO DE FALA 2 - Mapeia com 02_oficina.mp4]
Tivemos que chamar o guincho e levar para a oficina mais cara da cidade.

[BLOCO DE FALA 3 - Mapeia com 03_estrada.mp4]
Mas, no fim, o problema era só um fusível de 5 reais.
```

**Seu dever como Codex:** Ao desenhar o Código-Roteiro, você deve garantir que a quantidade de blocos de fala bata perfeitamente com a quantidade de ativos mapeados (Templates e Vídeos Base). A "elasticidade" esticará a duração do vídeo `01_carro.mp4` exatamente pelo tempo que demorar para o áudio do "Bloco de fala 1" terminar de ser lido.
