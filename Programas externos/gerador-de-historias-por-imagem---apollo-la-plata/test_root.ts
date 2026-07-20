import { GoogleGenAI } from '@google/genai';

async function testParams() {
    const ai = new GoogleGenAI({ apiKey: 'invalid_key' }); 
    try {
        await ai.models.generateContent({
            model: "non-existent-model-123",
            contents: "hi",
        });
        console.log("OK");
    } catch (e: any) {
        console.error("Error full:", e.message);
    }
}

testParams();
