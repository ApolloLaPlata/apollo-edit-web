import os
import sys
import asyncio
import chromadb
from chromadb.utils import embedding_functions

from mcp.server import Server, NotificationOptions
from mcp.server.stdio import stdio_server
import mcp.types as types
from mcp.server.models import InitializationOptions

# Inicializa ChromaDB
BASE_DIR = r'E:\MEUS PROGRAMAS\ANTIGRAVITY_OBSERVER'
DB_PATH = os.path.join(BASE_DIR, 'memory_rag/chroma_db')

def get_collection():
    client = chromadb.PersistentClient(path=DB_PATH)
    sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
    collection = client.get_or_create_collection(name="apollo_shadow_logs", embedding_function=sentence_transformer_ef)
    return collection

app = Server("apollo-memory")

async def handle_list_tools(ctx, params: types.PaginatedRequestParams | None = None) -> types.ListToolsResult:
    return types.ListToolsResult(
        tools=[
            types.Tool(
                name="query_apollo_memory",
                description="Pesquisa no historico nativo (RAG) do Antigravity usando ChromaDB. Util para lembrar regras matematicas, de voz ou de arquitetura do chat passado.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "O que voce esta procurando? Ex: 'formula XTTS', 'arquitetura do motor'."},
                        "limit": {"type": "integer", "description": "Numero maximo de resultados", "default": 10}
                    },
                    "required": ["query"]
                }
            ),
            types.Tool(
                name="get_recent_context",
                description="Recupera as ultimas mensagens cronologicas para se contextualizar sobre o que estava sendo feito antes no projeto.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "limit": {"type": "integer", "description": "Numero maximo de mensagens recentes", "default": 30}
                    },
                    "required": []
                }
            )
        ]
    )

async def handle_call_tool(ctx, params: types.CallToolRequestParams) -> types.CallToolResult:
    name = params.name
    arguments = params.arguments or {}
    
    try:
        collection = get_collection()
    except Exception as e:
        return types.CallToolResult(content=[types.TextContent(type="text", text=f"Erro ao conectar no banco ChromaDB: {e}")])

    if name == "query_apollo_memory":
        query = arguments.get("query")
        limit = arguments.get("limit", 10)
        
        results = collection.query(
            query_texts=[query],
            n_results=limit
        )
        
        if not results['documents'] or not results['documents'][0]:
            return types.CallToolResult(content=[types.TextContent(type="text", text="Nenhum resultado encontrado para essa pesquisa.")])
            
        docs = results['documents'][0]
        metadatas = results['metadatas'][0]
        
        response = "### 🧠 Memorias Encontradas:\n\n"
        for doc, meta in zip(docs, metadatas):
            timestamp = meta.get("timestamp", "Unknown")
            response += f"**Data:** {timestamp}\n**Log:** {doc}\n---\n"
            
        return types.CallToolResult(content=[types.TextContent(type="text", text=response)])
        
    elif name == "get_recent_context":
        limit = arguments.get("limit", 30)
        
        all_results = collection.get()
        if not all_results['documents']:
            return types.CallToolResult(content=[types.TextContent(type="text", text="A memoria esta vazia.")])
            
        combined = list(zip(all_results['documents'], all_results['metadatas']))
        # Sort by timestamp descending
        combined.sort(key=lambda x: x[1].get('timestamp', ''), reverse=True)
        
        # Take the most recent 'limit' items
        recent = combined[:limit]
        # Reverse to chronological order for readability
        recent.reverse()
        
        response = "### ⏳ Contexto Recente do Antigravity:\n\n"
        for doc, meta in recent:
            timestamp = meta.get("timestamp", "Unknown")
            response += f"[{timestamp}] {doc}\n"
            
        return types.CallToolResult(content=[types.TextContent(type="text", text=response)])
        
    return types.CallToolResult(
        content=[types.TextContent(type="text", text=f"Unknown tool: {name}")],
        isError=True
    )

app.add_request_handler("tools/list", types.PaginatedRequestParams, handle_list_tools)
app.add_request_handler("tools/call", types.CallToolRequestParams, handle_call_tool)

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, InitializationOptions(
            server_name="apollo-memory",
            server_version="1.0.0",
            capabilities=app.get_capabilities(
                notification_options=NotificationOptions(),
                experimental_capabilities={},
            )
        ))

if __name__ == "__main__":
    asyncio.run(main())
