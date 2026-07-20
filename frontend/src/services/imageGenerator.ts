import { GenerationSettings, Character } from '../types';
import { generateImageFromPrompt as generateGeminiImage } from './geminiService';
import { checkComfyConnection, queuePrompt, waitForPromptCompletion, fetchMediaAsBase64, injectPromptIntoWorkflow, uploadImageToComfyUI, injectImageIntoWorkflow, randomizeSeedInWorkflow } from './comfyService';

export const generateImage = async (
    apiKey: string,
    prompt: string,
    characters: Character[],
    settings: GenerationSettings,
    referenceImage?: string
): Promise<string> => {
    if (settings.imageProvider === 'comfyui' && settings.comfyUrl && settings.comfyImageWorkflow) {
        // Use ComfyUI
        const isConnected = await checkComfyConnection(settings.comfyUrl, settings.comfyApiKey);
        if (!isConnected) {
            throw new Error("Não foi possível conectar ao ComfyUI. Verifique a URL nas configurações.");
        }

        let workflow = JSON.parse(settings.comfyImageWorkflow);

        // Upload reference image if provided
        if (referenceImage) {
            const uploadedFilename = await uploadImageToComfyUI(settings.comfyUrl, referenceImage, settings.comfyApiKey);
            workflow = injectImageIntoWorkflow(workflow, uploadedFilename);
        }

        // Inject prompt
        workflow = injectPromptIntoWorkflow(workflow, prompt, settings.negativePrompt);
        
        // Randomize seed
        workflow = randomizeSeedInWorkflow(workflow);

        // Queue prompt
        const promptId = await queuePrompt(settings.comfyUrl, workflow, settings.comfyApiKey);

        // Wait for completion
        const history = await waitForPromptCompletion(settings.comfyUrl, promptId, settings.comfyApiKey);

        // Extract image
        const outputs = history[promptId].outputs;
        let filename, subfolder, type, directUrl;

        for (const nodeId in outputs) {
            if (outputs[nodeId].images && outputs[nodeId].images.length > 0) {
                const img = outputs[nodeId].images[0];
                if (img.url) {
                    directUrl = img.url;
                } else {
                    filename = img.filename;
                    subfolder = img.subfolder;
                    type = img.type;
                }
                break;
            }
        }

        if (!filename && !directUrl) {
            throw new Error("Nenhuma imagem retornada pelo ComfyUI.");
        }

        if (directUrl) {
            // Fetch direct URL and convert to base64
            const response = await fetch('/api/proxy', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ url: directUrl })
            });
            if (!response.ok) throw new Error(`Failed to fetch image from URL: ${response.statusText}`);
            const blob = await response.blob();
            const base64Image = await new Promise<string>((resolve, reject) => {
                const reader = new FileReader();
                reader.onloadend = () => {
                    if (typeof reader.result === 'string') resolve(reader.result);
                    else reject(new Error("Failed to convert blob to base64"));
                };
                reader.onerror = reject;
                reader.readAsDataURL(blob);
            });
            return base64Image;
        }

        const base64Image = await fetchMediaAsBase64(settings.comfyUrl, filename, subfolder, type, settings.comfyApiKey);
        return base64Image;
    } else if (settings.imageProvider === 'flux_modal' || settings.imageProvider === 'flux_pulid') {
        // Use FLUX Modal Cloud Engine
        const payload: any = {
            prompt: prompt,
            model: settings.imageProvider === 'flux_pulid' ? "flux-pulid" : "flux-dev",
            preset: "pro", // Adjust based on settings
            format: settings.aspectRatio === '16:9' ? 'horizontal' : settings.aspectRatio === '9:16' ? 'vertical' : 'square',
            width: settings.aspectRatio === '16:9' ? 1280 : settings.aspectRatio === '9:16' ? 720 : 1024,
            height: settings.aspectRatio === '16:9' ? 720 : settings.aspectRatio === '9:16' ? 1280 : 1024,
            guidance_scale: 3.5,
            num_inference_steps: 28
        };
        
        if (referenceImage) {
            // Strip the data:image/png;base64, prefix if it exists
            const base64Data = referenceImage.includes(',') ? referenceImage.split(',')[1] : referenceImage;
            payload.reference_images_base64 = [base64Data];
        }

        const response = await fetch('https://apollolaplata--apollo-render-router-apollo-api.modal.run/generate/image', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const data = await response.json();
        
        if (data.status === 'success' && data.image_base64) {
            return `data:image/jpeg;base64,${data.image_base64}`;
        } else {
            throw new Error(`Erro na API Modal: ${data.message || 'Desconhecido'}`);
        }
    } else if (settings.imageProvider === 'apollo-cloud-multipass') {
        const { runModalMultiPass } = await import('./comfyService');
        
        if (!settings.comfyImageWorkflow) {
            throw new Error("Você precisa importar um Workflow JSON base (KLEIN ou PuLID) na seção ComfyUI primeiro!");
        }

        const etapas = characters.map(c => ({
            prompt: prompt,
            image_b64: c.images[0] ? (c.images[0].includes(',') ? c.images[0].split(',')[1] : c.images[0]) : null
        })).filter(e => e.image_b64 !== null);

        if (etapas.length === 0) {
            throw new Error("Nenhum personagem com imagem foi encontrado para o Multi-Pass.");
        }

        const script = {
            workflow_json_string: settings.comfyImageWorkflow,
            etapas: etapas
        };

        const data = await runModalMultiPass(script);
        
        if (data.status === 'success' && data.image_base64) {
            return `data:image/jpeg;base64,${data.image_base64}`;
        } else {
            throw new Error(`Erro na API Modal (Multi-Pass): ${data.message || 'Desconhecido'}`);
        }
    } else {
        // Use Gemini
        return await generateGeminiImage(apiKey, prompt, characters, settings, referenceImage);
    }
};
