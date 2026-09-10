# O MANUAL DO PILOTO - APOLLO STUDIO
## 04: Regras e Formatação da Aba Podcast

### A Mecânica da Aba Podcast
Diferente da Aba Diretor (focada em cortes bruscos de vídeo e avatares), a "Aba Podcast" é projetada para áudios longos, debates, trocas de locutores e layouts que reagem à voz (Visualizers, ondas sonoras, avatares estáticos piscando).

### Formatação de Roteiro para Podcast
Ao projetar a matriz de um Podcast, o Codex deve organizar o código-roteiro demarcando as "Trocas de Microfone". Isso diz à Elasticidade do Editor que um novo locutor assumiu o áudio e, portanto, a tela deve mudar (ex: dar destaque para a foto do locutor atual).

**Exemplo de Saída Estruturada para Podcast:**

```text
==== [INÍCIO DO CÓDIGO-ROTEIRO: ABA PODCAST] ====

[MICROFONE: APRESENTADOR A]
[TEXTO]: E hoje recebemos aqui o especialista em IA para debatermos o futuro da tecnologia. Seja bem vindo!
[TEMPLATE VISUAL]: layout_duplo_foco_esq.json

[MICROFONE: CONVIDADO B]
[TEXTO]: Muito obrigado! É uma honra. Olha, a verdade é que estamos apenas no começo de uma revolução monumental.
[TEMPLATE VISUAL]: layout_duplo_foco_dir.json

[MICROFONE: APRESENTADOR A]
[TEXTO]: Concordo plenamente. Inclusive, quero mostrar aos espectadores aquele gráfico que você trouxe.
[TEMPLATE VISUAL]: layout_grafico_convidado.json
[EFEITO SONORO]: sfx_papel_deslizando.wav

==== [FIM DO CÓDIGO-ROTEIRO] ====
```

Ao seguir este modelo limpo, sem textos soltos no meio, você permite que o usuário Humano direcione os parâmetros exatos para os inputs de locutor A, locutor B e templates na interface do Apollo Podcast.
