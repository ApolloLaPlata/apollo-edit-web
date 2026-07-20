import { GoogleGenAI } from "@google/genai";
const ai = new GoogleGenAI({ apiKey: process.env.GEMINI_API_KEY });
async function run() {
  try {
    const response = await ai.models.generateContent({
        model: 'gemini-2.5-flash',
        contents: 'Hi'
    });
    console.log("2.5-flash success", response.text);
  } catch (e: any) {
    console.log("2.5-flash error", e.message);
  }
}
run();
