import { GoogleGenAI, HarmCategory, HarmBlockThreshold } from '@google/genai';

async function test() {
    const ai = new GoogleGenAI({ apiKey: process.env.API_KEY || 'fake' });
    try {
        const response = await ai.models.generateContent({
            model: 'gemini-2.5-flash',
            contents: 'test',
            config: {
                systemInstruction: "test instruction",
                temperature: undefined, // this might throw
            }
        });
        console.log("Success with undefined temp", response.text);
    } catch (e: any) {
        console.error("Failed defined:", e.message, JSON.stringify(e));
    }
}
test();
