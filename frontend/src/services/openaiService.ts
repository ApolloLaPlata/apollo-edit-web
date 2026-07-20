import { GenerationSettings } from '../types';

const OPENAI_API_URL = 'https://api.openai.com/v1';
const XAI_API_URL = 'https://api.x.ai/v1';

export const generateTextOpenAI = async (
    apiKey: string,
    prompt: string,
    settings: GenerationSettings,
    systemInstruction?: string
): Promise<string> => {
    if (!apiKey) throw new Error("Chave API da OpenAI não configurada.");

    const messages = [];
    if (systemInstruction) {
        messages.push({ role: 'system', content: systemInstruction });
    }
    messages.push({ role: 'user', content: prompt });

    const response = await fetch(`${OPENAI_API_URL}/chat/completions`, {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${apiKey}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            model: settings.openaiModel || 'gpt-4o',
            messages: messages,
            temperature: settings.temperature || 0.7,
            max_tokens: settings.maxOutputTokens || 2048,
            top_p: settings.topP || 1,
        })
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(`OpenAI Error: ${error.error?.message || response.statusText}`);
    }

    const data = await response.json();
    return data.choices[0]?.message?.content || "";
};

export const generateTextGrok = async (
    apiKey: string,
    prompt: string,
    settings: GenerationSettings,
    systemInstruction?: string
): Promise<string> => {
    if (!apiKey) throw new Error("Chave API do Grok (xAI) não configurada.");

    const messages = [];
    if (systemInstruction) {
        messages.push({ role: 'system', content: systemInstruction });
    }
    messages.push({ role: 'user', content: prompt });

    const response = await fetch(`${XAI_API_URL}/chat/completions`, {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${apiKey}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            model: settings.xaiModel || 'grok-2-latest',
            messages: messages,
            temperature: settings.temperature || 0.7,
            max_tokens: settings.maxOutputTokens || 2048,
            stream: false
        })
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(`Grok Error: ${error.error?.message || response.statusText}`);
    }

    const data = await response.json();
    return data.choices[0]?.message?.content || "";
};
