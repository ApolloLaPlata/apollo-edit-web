import { GenerationSettings } from '../types';
import { generateTextOpenRouter } from './openRouterService';
import { generateTextOpenAI, generateTextGrok } from './openaiService';
import { GoogleGenAI, HarmCategory, HarmBlockThreshold } from '@google/genai';

// Helper to execute generateContent with a timeout
const generateContentWithTimeout = async (ai: GoogleGenAI, params: any, timeoutMs: number = 120000) => {
    let timeoutId: NodeJS.Timeout;
    const timeoutPromise = new Promise<never>((_, reject) => {
        timeoutId = setTimeout(() => reject(new Error(`Request timed out after ${timeoutMs / 1000} seconds`)), timeoutMs);
    });

    try {
        const result = await Promise.race([
            ai.models.generateContent(params),
            timeoutPromise
        ]);
        return result;
    } finally {
        clearTimeout(timeoutId!);
    }
};

export const generateText = async (
    prompt: string,
    settings: GenerationSettings,
    systemInstruction?: string,
    geminiApiKey?: string // Optional, used if textProvider is gemini
): Promise<string> => {
    try {
        if (settings.textProvider === 'openrouter' && settings.openRouterKey) {
            return await generateTextOpenRouter(settings.openRouterKey, prompt, settings, systemInstruction);
        } else if (settings.textProvider === 'openai' && settings.openaiKey) {
            return await generateTextOpenAI(settings.openaiKey, prompt, settings, systemInstruction);
        } else if (settings.textProvider === 'xai' && settings.xaiKey) {
            return await generateTextGrok(settings.xaiKey, prompt, settings, systemInstruction);
        } else {
            // Fallback to Gemini
            if (!geminiApiKey) {
                throw new Error("Chave API do Gemini não fornecida para geração de texto.");
            }
            const ai = new GoogleGenAI({ apiKey: geminiApiKey });
            
            const modelName = settings.useThinking ? 'gemini-2.5-pro' : 'gemini-2.5-flash';
            const config: any = {};

            if (systemInstruction !== undefined && systemInstruction !== null && systemInstruction !== '') {
                config.systemInstruction = systemInstruction;
            }
            if (settings.temperature !== undefined && settings.temperature !== null && !isNaN(Number(settings.temperature))) {
                config.temperature = Number(settings.temperature);
            }
            if (settings.topP !== undefined && settings.topP !== null && !isNaN(Number(settings.topP))) {
                config.topP = Number(settings.topP);
            }

            if (settings.useThinking) {
                config.thinkingConfig = {
                    thinkingBudgetTokens: 8192 // Adjust as needed, or omit for default HIGH
                };
            }

            const response = await generateContentWithTimeout(ai, {
                model: modelName,
                contents: [{ role: "user", parts: [{ text: prompt }] }],
                config: config
            }, 60000); // 60s timeout for text
            return response.text || "";
        }
    } catch (error: any) {
        if (settings.textProvider !== 'gemini' && settings.textProvider !== undefined) {
            throw new Error(`TextProviderError: [${settings.textProvider}] ${error.message}`);
        }
        throw error;
    }
};
