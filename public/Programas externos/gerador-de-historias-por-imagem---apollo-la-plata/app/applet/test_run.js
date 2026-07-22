import { GoogleGenAI } from '@google/genai';

async function testParams() {
    const ai = new GoogleGenAI({ apiKey: process.env.API_KEY || 'AIzaSyTestKey' });
    try {
        console.log("Testing with contents: text, config: systemInstruction");
        await ai.models.generateContent({
            model: "gemini-2.5-flash",
            contents: "say hi",
            config: {
                systemInstruction: "you are a bot"
            }
        });
        console.log("OK string content");
    } catch (e: any) {
        console.error("String content error:", e.message);
    }

    try {
        console.log("Testing with parts");
        await ai.models.generateContent({
            model: "gemini-2.5-flash",
            contents: { parts: [{ text: "say hi" }] },
            config: {
                systemInstruction: "you are a bot"
            }
        });
        console.log("OK parts content");
    } catch (e: any) {
        console.error("Parts content error:", e.message);
    }
}

testParams();
