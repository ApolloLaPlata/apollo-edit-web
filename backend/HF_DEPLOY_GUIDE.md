# 🚀 Guia de Deploy (Pilar 3: Hugging Face Spaces)

Este guia acompanha o `Dockerfile` que acabamos de forjar. Ele vai colocar todo o cérebro pesado do Apollo Edit Web (FastAPI) rodando no hardware de 16GB de RAM gratuito do Hugging Face.

## Passo a Passo para Subir:

1. Acesse sua conta no [Hugging Face](https://huggingface.co/spaces) e clique em **Create New Space**.
2. De um nome ao seu Space (ex: `apollo-edit-backend`).
3. Em **Select the Space SDK**, escolha a opção **Docker** e clique em **Blank**.
4. Em **Space hardware**, mantenha o *Free (2 vCPU - 16GB)*.
5. Crie o Space.

## Fazendo o Upload do Código (Via Terminal / Git):

Abra o terminal do seu computador na pasta `E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\backend` e digite os seguintes comandos (substituindo pelo link do seu Space):

```bash
git init
git add .
git commit -m "Deploy Inicial do Backend Apollo Edit - Pilar 3"
git remote add origin https://huggingface.co/spaces/SEU_USUARIO/apollo-edit-backend
git push -u origin main
```

*(Se o Git pedir senha, lembre-se que no Hugging Face você deve gerar um "Access Token" com permissão de "Write" nas configurações da sua conta e usá-lo como senha).*

## Variáveis de Ambiente (Segurança)
Nunca suba o arquivo `.env`! O `.dockerignore` que criei já proíbe isso.
Lá no painel do seu Space no Hugging Face, clique em **Settings > Variables and secrets**, e adicione manualmente as chaves do Modal, OpenAI, etc.

---
*Assim que o Build do Docker finalizar lá na nuvem, o backend responderá perfeitamente pela porta 7860 e será o cérebro inviolável que o Vercel irá consultar.*
