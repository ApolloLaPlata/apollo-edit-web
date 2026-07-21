/**
 * Apollo La Plata - Motor de IA Vanilla JS
 * Tradução do geminiService.ts e imageGenerator.ts
 * Utiliza o SDK oficial do Google injetado via ESM (esm.sh) para manter 100% de compatibilidade
 */

window.laplataAI = {};

(function() {
    // Helper Base64
    function base64ToPart(base64Data, mimeType = 'image/png') {
        const match = base64Data.match(/^data:(image\/\w+);base64,/);
        let finalMimeType = mimeType;
        let data = base64Data;
        if (match) {
            finalMimeType = match[1];
            data = base64Data.replace(/^data:image\/\w+;base64,/, "");
        }
        return {
            inlineData: { data, mimeType: finalMimeType }
        };
    }

    // Limpeza de Output
    function cleanModelOutput(text) {
        if (!text) return "";
        let clean = text.trim();
        clean = clean.replace(/```\w*\n?/g, '').replace(/```/g, '');
        clean = clean.replace(/^(Prompt|Output|Response|Description):\s*/i, '');
        return clean.trim();
    }

    // Criador de Regex Inteligente para Personagens
    window.laplataAI.createCharacterMatchRegex = function(name) {
        const cleanName = name.replace(/^#/, '').trim();
        const parts = cleanName.split(/\s+/);
        const patterns = [];

        const normalizeAccents = (str) => str.normalize("NFD").replace(/[\u0300-\u036f]/g, "");

        const addVariations = (word) => {
            const norm = normalizeAccents(word);
            patterns.push(word);
            if (norm !== word) patterns.push(norm);

            const lowerNorm = norm.toLowerCase();
            if (lowerNorm.endsWith("ao")) {
                patterns.push(norm.slice(0, -1));
                patterns.push(norm.slice(0, -2));
                patterns.push(norm.slice(0, -2) + 'a');
                patterns.push(norm.slice(0, -2) + 'al');
            } else if (lowerNorm.endsWith("a") && norm.length > 4) {
                patterns.push(norm.slice(0, -1));
            } else if (lowerNorm.endsWith("es") && norm.length > 4) {
                patterns.push(norm.slice(0, -2));
                patterns.push(norm.slice(0, -1));
            }
        };

        addVariations(cleanName);
        if (parts.length > 1) addVariations(parts[0]);
        if (parts.length > 2) addVariations(`${parts[0]} ${parts[parts.length-1]}`);

        const uniquePatterns = Array.from(new Set(patterns))
            .filter(p => p.length >= 3 || p === cleanName || p === normalizeAccents(cleanName))
            .sort((a, b) => b.length - a.length);

        const regexStrParts = uniquePatterns.map(p => {
            const escaped = p.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
            return escaped.replace(/\s+/g, '\\s+');
        });

        const makeVowelsFlexible = (str) => {
            return str
                .replace(/[aáàãâä]/gi, '[aáàãâäAÁÀÃÂÄaA]')
                .replace(/[eéèêë]/gi, '[eéèêëEÉÈÊËeE]')
                .replace(/[iíìîï]/gi, '[iíìîïIÍÌÎÏiI]')
                .replace(/[oóòõôö]/gi, '[oóòõôöOÓÒÕÔÖoO]')
                .replace(/[uúùûü]/gi, '[uúùûüUÚÙÛÜuU]')
                .replace(/[cç]/gi, '[cçCÇ]');
        };

        const finalRegexParts = regexStrParts.map(p => makeVowelsFlexible(p));
        return new RegExp(`(^|[\\s.,!?;:"'({\\[\\-])(#?(?:${finalRegexParts.join('|')}))(?=[\\s.,!?;:"')}\\]]|$)`, 'gi');
    };

    // --- GERAÇÃO DE IMAGEM ---
    window.laplataAI.generateImage = async function(apiKey, prompt, characters, settings, referenceImage = null) {
        // Carrega o SDK dinamicamente via ESM para rodar no Vanilla JS sem bundler
        const { GoogleGenAI, HarmCategory, HarmBlockThreshold } = await import('https://esm.sh/@google/genai@0.1.2');
        const ai = new GoogleGenAI({ apiKey });

        const combinedText = [prompt, settings.globalContext || "", settings.sceneContext || "", settings.negativePrompt || ""].join(" ");
        
        const usedCharacters = characters.filter((char) => {
            const regex = window.laplataAI.createCharacterMatchRegex(char.name);
            return regex.test(combinedText);
        });

        let enhancedPrompt = prompt;
        const parts = [];

        let promptText = `Generate a high-quality image based on the following prompt:\n\nPROMPT: ${enhancedPrompt}\n\n`;

        if (settings.globalContext) promptText += `VISUAL STYLE / ART DIRECTION: ${settings.globalContext}\n\n`;
        if (settings.sceneContext) promptText += `SCENE CONTEXT (Narrative Environment): ${settings.sceneContext}\n\n`;
        if (settings.negativePrompt) promptText += `NEGATIVE PROMPT (Do NOT include these elements): ${settings.negativePrompt}\n\n`;

        promptText += `LANGUAGE/TEXT RENDERING: If the image requires any text, signs, labels, or documents, they MUST be written in PORTUGUESE (PT-BR) unless otherwise specified.\n\n`;

        if (usedCharacters.length > 0) {
            promptText += `CRITICAL CHARACTER CONSISTENCY INSTRUCTIONS:\n`;
            promptText += `1. The attached images are reference photos of specific characters in the scene.\n`;
            promptText += `2. You MUST generate an image of THESE EXACT CHARACTERS.\n`;
            promptText += `3. The generated characters MUST look IDENTICAL to the people in the reference photos.\n`;
            promptText += `4. Use the provided reference images as the absolute source of truth.\n\n`;
            
            usedCharacters.forEach((char, idx) => {
                const alias = `[Subject ${idx + 1}]`;
                const regex = window.laplataAI.createCharacterMatchRegex(char.name);
                let safeDescription = char.description || "";
                
                const nameWithoutHash = char.name.replace('#', '');
                if (safeDescription && nameWithoutHash.length > 2) {
                    const descRegex = new RegExp(`\\b${nameWithoutHash.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}\\b`, 'gi');
                    safeDescription = safeDescription.replace(descRegex, alias);
                }

                if (safeDescription) {
                    enhancedPrompt = enhancedPrompt.replace(regex, `$1${alias} (Visual Description: ${safeDescription})`);
                } else {
                    enhancedPrompt = enhancedPrompt.replace(regex, `$1${alias}`);
                }
                promptText = promptText.replace(regex, `$1${alias}`);
            });

            promptText = promptText.replace(`PROMPT: ${prompt}`, `PROMPT: ${enhancedPrompt}`);
        }

        const randomSeed = Math.floor(Math.random() * 1000000000);
        promptText += `[System Note: Internal Seed ${randomSeed}]\n`;

        parts.push({ text: promptText });

        if (settings.styleReferenceImage) {
            parts.push({ text: "CRITICAL STYLE REFERENCE: Apply the exact visual style of the following image:" });
            parts.push(base64ToPart(settings.styleReferenceImage));
        }

        if (usedCharacters.length > 0) {
            usedCharacters.forEach((char, idx) => {
                const alias = `[Subject ${idx + 1}]`;
                let charText = `--- Reference image(s) for ${alias} ---`;
                
                let safeDescription = char.description || "";
                const nameWithoutHash = char.name.replace('#', '');
                if (safeDescription && nameWithoutHash.length > 2) {
                    const descRegex = new RegExp(`\\b${nameWithoutHash.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}\\b`, 'gi');
                    safeDescription = safeDescription.replace(descRegex, alias);
                }

                if (safeDescription) charText += `\nCharacter Description: ${safeDescription}`;
                parts.push({ text: charText });
                
                if (char.images && char.images.length > 0) {
                    const imagesToUse = char.images.slice(0, 4);
                    parts.push({ text: `The following ${imagesToUse.length} image(s) are all of the EXACT SAME PERSON referred to as "${alias}". You MUST generate this specific person.` });
                    imagesToUse.forEach(img => parts.push(base64ToPart(img)));
                } else if (char.previewUrl) {
                    parts.push({ text: `The following image is of the person referred to as "${alias}". You MUST generate this specific person.` });
                    parts.push(base64ToPart(char.previewUrl));
                }
            });
        }

        if (referenceImage) {
            parts.push({ text: "PREVIOUS SCENE CONTEXT / REFERENCE IMAGE:" });
            parts.push(base64ToPart(referenceImage));
        }

        const isGemini2_5 = settings.modelId.includes('gemini-2.5');
        const imageConfig = { aspectRatio: settings.aspectRatio || '16:9' };
        if (!isGemini2_5) imageConfig.imageSize = settings.imageSize || '1K';

        const config = {
            imageConfig,
            safetySettings: [
                { category: HarmCategory.HARM_CATEGORY_HARASSMENT, threshold: HarmBlockThreshold.BLOCK_NONE },
                { category: HarmCategory.HARM_CATEGORY_HATE_SPEECH, threshold: HarmBlockThreshold.BLOCK_NONE },
                { category: HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT, threshold: HarmBlockThreshold.BLOCK_NONE },
                { category: HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT, threshold: HarmBlockThreshold.BLOCK_NONE },
            ]
        };

        try {
            console.log("Iniciando geração com Gemini SDK...", { model: settings.modelId });
            const response = await ai.models.generateContent({
                model: settings.modelId,
                contents: [{ role: "user", parts }],
                config: config,
            });

            if (response.promptFeedback?.blockReason) {
                throw new Error(`BLOQUEADO: ${response.promptFeedback.blockReason}`);
            }

            if (response.candidates?.[0]?.content?.parts) {
                for (const part of response.candidates[0].content.parts) {
                    if (part.inlineData && part.inlineData.data) {
                        return `data:${part.inlineData.mimeType || 'image/png'};base64,${part.inlineData.data}`;
                    }
                }
            }
            throw new Error("Nenhuma imagem retornada (possível bloqueio de segurança silencioso).");
        } catch (e) {
            throw e;
        }
    };

    // --- EXPANSÃO E DESCRIÇÃO DE TEXTO ---
    window.laplataAI.generateText = async function(apiKey, prompt, settings, systemInstruction = "") {
        const { GoogleGenAI } = await import('https://esm.sh/@google/genai@0.1.2');
        const ai = new GoogleGenAI({ apiKey });
        
        try {
            const response = await ai.models.generateContent({
                model: 'gemini-2.5-flash',
                contents: [{ role: "user", parts: [{ text: prompt }] }],
                config: {
                    systemInstruction: systemInstruction ? { parts: [{ text: systemInstruction }] } : undefined,
                    temperature: 0.7
                }
            });
            return cleanModelOutput(response.text);
        } catch (e) {
            throw e;
        }
    };

    window.laplataAI.expandDescription = async function(apiKey, shortDescription, mode, settings) {
        let systemInstruction = "";
        if (mode === 't-pose') {
            systemInstruction = "You are a Technical Character Artist for 3D Modeling. Expand the user's short description into a detailed, technical T-Pose reference prompt. Focus on exact physical proportions, clothing details, and symmetry. No flowery language.";
        } else if (mode === 'expression') {
            systemInstruction = "You are a Character Concept Artist. Expand the user's short description into a prompt for a Character Expression Sheet. Focus on personality traits, distinct facial features, and dynamic action poses.";
        } else {
            systemInstruction = "You are a Lead Character Designer. Expand the user's short description into a rich Character Sheet prompt. Focus on visual storytelling, materials, anatomy, and style covering Front, Side, and Back views.";
        }
        return await window.laplataAI.generateText(apiKey, `Short Description: ${shortDescription}\n\nExpand this into a detailed visual prompt:`, settings, systemInstruction);
    };

    // --- EDIÇÃO DE IMAGEM ---
    window.laplataAI.editImage = async function(apiKey, base64Image, instruction) {
        const { GoogleGenAI } = await import('https://esm.sh/@google/genai@0.1.2');
        const ai = new GoogleGenAI({ apiKey });
        
        try {
            const parts = [
                { text: `Apply the following edit instruction to the provided image: ${instruction}. Return the new edited image.` },
                base64ToPart(base64Image)
            ];
            
            const response = await ai.models.generateContent({
                model: 'gemini-2.5-flash',
                contents: [{ role: "user", parts }],
            });

            if (response.candidates?.[0]?.content?.parts) {
                for (const part of response.candidates[0].content.parts) {
                    if (part.inlineData && part.inlineData.data) {
                        return `data:${part.inlineData.mimeType || 'image/png'};base64,${part.inlineData.data}`;
                    }
                }
            }
            throw new Error("Falha na edição da imagem.");
        } catch (e) {
            throw e;
        }
    };

})();
