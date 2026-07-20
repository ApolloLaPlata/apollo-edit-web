import { GenerationSettings } from '../types';

const OPENROUTER_API_URL = 'https://openrouter.ai/api/v1';

export const generateTextOpenRouter = async (
    apiKey: string,
    prompt: string,
    settings: GenerationSettings,
    systemInstruction?: string
): Promise<string> => {
    if (!apiKey) throw new Error("Chave API do OpenRouter não configurada.");

    const messages = [];
    if (systemInstruction) {
        messages.push({ role: 'system', content: systemInstruction });
    }
    messages.push({ role: 'user', content: prompt });

    const response = await fetch(`${OPENROUTER_API_URL}/chat/completions`, {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${apiKey}`,
            'Content-Type': 'application/json',
            'HTTP-Referer': window.location.origin, // Required by OpenRouter
            'X-Title': 'GeminiStudio'
        },
        body: JSON.stringify({
            model: settings.openRouterTextModel,
            messages: messages,
            temperature: settings.temperature,
            max_tokens: settings.maxOutputTokens,
            top_p: settings.topP,
        })
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(`OpenRouter Error: ${error.error?.message || response.statusText}`);
    }

    const data = await response.json();
    return data.choices[0]?.message?.content || "";
};

export const fetchOpenRouterModels = async (apiKey: string) => {
    if (!apiKey) return null;

    try {
        const response = await fetch(`${OPENROUTER_API_URL}/models`, {
            headers: {
                'Authorization': `Bearer ${apiKey}`,
                'HTTP-Referer': window.location.origin,
                'X-Title': 'GeminiStudio'
            }
        });

        if (!response.ok) throw new Error("Falha ao buscar modelos");

        const data = await response.json();
        const allModels = data.data;

        // Categorize and Format
        const textModels = allModels
            .filter((m: any) => !m.id.includes('flux') && !m.id.includes('sdxl') && !m.id.includes('stable-diffusion') && !m.id.includes('midjourney'))
            .map((m: any) => ({
                id: m.id,
                name: `${m.name} (${parseFloat(m.pricing.prompt) === 0 ? 'Grátis' : 'Pago'})`,
                isFree: parseFloat(m.pricing.prompt) === 0
            }))
            .sort((a: any, b: any) => (b.isFree === a.isFree ? 0 : b.isFree ? 1 : -1)); // Free first

        return { textModels, imageModels: [] };
    } catch (error) {
        console.error("Erro ao buscar modelos OpenRouter:", error);
        return null;
    }
};
