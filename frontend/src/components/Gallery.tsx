import React, { useState, useEffect, useRef } from 'react';
import { GeneratedImage, ApiKey, GenerationSettings, Character } from '../types';
import { Download, ExternalLink, Image as ImageIcon, Archive, Trash2, Clapperboard, Copy, Check, FileText, RefreshCw, Wand2, Loader2, X, AlertTriangle, ChevronLeft, ChevronRight, Table } from 'lucide-react';
import { editGeneratedImage } from '../services/geminiService';
import { generateImage } from '../services/imageGenerator';
import { checkComfyConnection, queuePrompt, waitForPromptCompletion, fetchMediaAsBase64, injectPromptIntoWorkflow, uploadImageToComfyUI, injectImageIntoWorkflow } from '../services/comfyService';
import toast from 'react-hot-toast';
import { executeWithKeyRotation } from '../utils/apiKeyRotation';
import JSZip from 'jszip';
import SafeImage from './SafeImage';
import { extractLastFrame } from '../utils/videoUtils';

interface GalleryProps {
  images: GeneratedImage[];
  onClearGallery?: () => void;
  // Props required for Regeneration/Editing
  apiKeys: ApiKey[];
  setApiKeys: React.Dispatch<React.SetStateAction<ApiKey[]>>;
  settings: GenerationSettings;
  characters: Character[];
  addGeneratedImage: (img: GeneratedImage) => void;
  updateGeneratedImage?: (id: string, updates: Partial<GeneratedImage>) => void;
  onRemoveImage?: (id: string) => void;
  onImageClick?: (image: GeneratedImage) => void;
}

const Gallery: React.FC<GalleryProps> = ({ 
    images = [], 
    onClearGallery, 
    apiKeys, 
    setApiKeys,
    settings, 
    characters, 
    addGeneratedImage,
    updateGeneratedImage,
    onRemoveImage,
    onImageClick
}) => {
  // Defensive check: ensure images is always an array and filter out invalid items
  const safeImages = Array.isArray(images) 
    ? images.filter(img => img && typeof img === 'object' && img.id && img.imageUrl) 
    : [];

  const [showScriptModal, setShowScriptModal] = useState(false);
  const [scriptedBatchText, setScriptedBatchText] = useState("");
  const [isZipping, setIsZipping] = useState(false);
  const [copiedPromptId, setCopiedPromptId] = useState<string | null>(null);
  const [expandedPromptId, setExpandedPromptId] = useState<string | null>(null);
  const [scriptCopied, setScriptCopied] = useState(false);
  const [animPromptsCopied, setAnimPromptsCopied] = useState(false);
  
  // Confirmation States
  const [showClearConfirm, setShowClearConfirm] = useState(false);
  const [deletingId, setDeletingId] = useState<string | null>(null);

  // State for Editing
  const [editModeId, setEditModeId] = useState<string | null>(null);
  const [editInstruction, setEditInstruction] = useState('');
  const [processingImageId, setProcessingImageId] = useState<string | null>(null);
  
  // Edit Confirmation State
  const [pendingEdit, setPendingEdit] = useState<{ img: GeneratedImage, instruction: string } | null>(null);

  // Pagination State
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 20;

  const totalPages = Math.ceil(safeImages.length / itemsPerPage);
  
  // Reset to page 1 if images change significantly (e.g. cleared)
  useEffect(() => {
    if (currentPage > totalPages && totalPages > 0) {
      setCurrentPage(totalPages);
    } else if (totalPages === 0) {
      setCurrentPage(1);
    }
  }, [safeImages.length, totalPages, currentPage]);

  const reversedImages = [...safeImages].reverse();
  const currentImages = reversedImages.slice(
    (currentPage - 1) * itemsPerPage,
    currentPage * itemsPerPage
  );

  const apiKeysRef = useRef(apiKeys);
  useEffect(() => { apiKeysRef.current = apiKeys; }, [apiKeys]);

  // Helper to ensure 01, 02, 03... formatting
  const padNumber = (num: number) => num.toString().padStart(3, '0');

  const handleRegenerate = async (img: GeneratedImage) => {
      setProcessingImageId(img.id);
      try {
          const newImageUrl = await executeWithKeyRotation(
              apiKeysRef,
              setApiKeys,
              async (apiKey) => {
                  return await generateImage(
                      apiKey,
                      img.prompt,
                      characters, // Pass all chars so references work if prompt has tags
                      settings
                  );
              }
          );

          if (updateGeneratedImage) {
              updateGeneratedImage(img.id, {
                  imageUrl: newImageUrl,
                  // We don't update the timestamp so it stays in the exact same position
                  // if any sorting relies on it, though currently it relies on array order.
              });
              toast.success("Imagem regenerada com sucesso!");
          } else {
              const newImage: GeneratedImage = {
                  ...img,
                  id: crypto.randomUUID(),
                  imageUrl: newImageUrl,
                  timestamp: Date.now(),
              };
              addGeneratedImage(newImage);
              toast.success("Nova imagem gerada!");
          }

      } catch (e: any) {
          toast.error("Falha ao regenerar: " + e.message);
      } finally {
          setProcessingImageId(null);
      }
  };

  const handleEditRequest = (img: GeneratedImage) => {
      if (!editInstruction.trim()) return;
      setPendingEdit({ img, instruction: editInstruction });
      setEditModeId(null); // Close the inline edit input
  };

  const executeEdit = async (replaceOriginal: boolean) => {
      if (!pendingEdit) return;
      const { img, instruction } = pendingEdit;
      setPendingEdit(null); // Close confirmation dialog

      setProcessingImageId(img.id);
      try {
          const newImageUrl = await executeWithKeyRotation(
              apiKeysRef,
              setApiKeys,
              async (apiKey) => {
                  return await editGeneratedImage(
                      apiKey,
                      img.imageUrl,
                      instruction,
                      settings
                  );
              }
          );

          if (replaceOriginal && updateGeneratedImage) {
              // Replace logic
              updateGeneratedImage(img.id, {
                  imageUrl: newImageUrl,
                  prompt: `[Editado: ${instruction}] ${img.prompt}`,
                  timestamp: Date.now()
              });
          } else {
              // Save as new logic (Default)
              const newImage: GeneratedImage = {
                  id: crypto.randomUUID(),
                  prompt: `[Editado: ${instruction}] ${img.prompt}`,
                  imageUrl: newImageUrl,
                  timestamp: Date.now(),
                  characterIds: img.characterIds,
                  aspectRatio: img.aspectRatio,
                  videoPrompt: img.videoPrompt
              };
              addGeneratedImage(newImage);
          }
          
          setEditInstruction('');

      } catch (e: any) {
          toast.error("Falha na edição: " + e.message);
      } finally {
          setProcessingImageId(null);
      }
  };

  const downloadImage = (dataUrl: string, filename: string) => {
    const link = document.createElement('a');
    link.href = dataUrl;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  // Helper to determine aspect ratio class based on image metadata
  const getAspectRatioClass = (ratio: string) => {
      switch (ratio) {
          case '1:1': return 'aspect-square';
          case '9:16': 
          case '3:4': return 'aspect-[9/16]';
          case '16:9':
          case '4:3': return 'aspect-video';
          default: return 'aspect-video';
      }
  };

  // Logic to build the consolidated script string
  const generateMasterScript = (sortedImages: GeneratedImage[]) => {
      let scriptContent = "PROJETO: GEMINI STUDIO STORY BATCH\n";
      scriptContent += "===================================\n\n";

      sortedImages.forEach((img, index) => {
          const sceneNum = padNumber(index + 1);
          scriptContent += `CENA ${sceneNum}\n`;
          scriptContent += `-----------------------------------\n`;
          // UPDATED: Filename now matches the cleaner format
          scriptContent += `Arquivo Img  : Cena_${sceneNum}.png\n`;
          scriptContent += `Prompt (Img) : ${img.prompt}\n`;
          
          if (img.videoPrompt) {
            scriptContent += `Prompt (Vid) : ${img.videoPrompt}\n`;
          } else {
            scriptContent += `Prompt (Vid) : [Nenhum prompt de vídeo gerado]\n`;
          }
          scriptContent += `\n`;
      });

      return scriptContent;
  };

  const copyMasterScript = () => {
      // Sort by timestamp ascending (Oldest = Scene 1)
      const sortedImages = [...safeImages].sort((a, b) => a.timestamp - b.timestamp);
      const script = generateMasterScript(sortedImages);
      navigator.clipboard.writeText(script);
      setScriptCopied(true);
      setTimeout(() => setScriptCopied(false), 2000);
  };

  const copyAnimationPromptsOnly = () => {
      const sortedImages = [...safeImages].sort((a, b) => a.timestamp - b.timestamp);
      
      const script = sortedImages.map((img) => {
          // Priority: Video Prompt > Image Prompt
          let content = img.videoPrompt || img.prompt;
          
          // FORMATTING FIX: 
          // 1. Remove internal newlines to ensure prompt is a single block
          // 2. Trim whitespace
          // 3. Remove accidental prefixes like "Prompt:"
          content = content.replace(/[\r\n]+/g, ' ').trim();
          content = content.replace(/^(Prompt|Motion Prompt):\s*/i, '');
          
          return content;
      }).join('\n\n'); // Strictly separated by double newline for easy batch pasting

      navigator.clipboard.writeText(script);
      setAnimPromptsCopied(true);
      setTimeout(() => setAnimPromptsCopied(false), 2000);
  };

  const [isBatchAnimating, setIsBatchAnimating] = useState(false);
  const [batchAnimationProgress, setBatchAnimationProgress] = useState({ current: 0, total: 0 });

  const startScriptedBatchAnimation = async () => {
    if (settings.videoProvider !== 'comfyui' || !settings.comfyUrl || !settings.comfyVideoWorkflow) {
      toast.error("Configure o ComfyUI para vídeos nas configurações primeiro.");
      return;
    }

    const lines = scriptedBatchText.split('\n').filter(l => l.trim().length > 0);
    const scenes = lines.map(l => {
        let type = 'CORTA';
        let prompt = l.trim();
        if (l.toUpperCase().includes('[CONTINUA]')) {
            type = 'CONTINUA';
            prompt = prompt.replace(/\[\s*CONTINUA\s*\]/gi, '').trim();
        } else if (l.toUpperCase().includes('[CORTA]')) {
             prompt = prompt.replace(/\[\s*CORTA\s*\]/gi, '').trim();
        }
        return { type, prompt };
    });

    const cortaCount = scenes.filter(s => s.type === 'CORTA').length;
    // Images available for CORTA (ordered oldest first)
    const sortedImagesForCorta = [...safeImages].sort((a,b) => a.timestamp - b.timestamp);
    
    if (sortedImagesForCorta.length < cortaCount) {
        toast.error(`Você tem ${cortaCount} cenas [CORTA] mas apenas ${sortedImagesForCorta.length} imagens na galeria.`);
        return;
    }

    setIsBatchAnimating(true);
    setShowScriptModal(false);
    
    let cortaIndex = 0;
    let lastGeneratedLastFrameBase64: string | null = null;
    
    setBatchAnimationProgress({ current: 0, total: scenes.length });

    try {
      const isConnected = await checkComfyConnection(settings.comfyUrl, settings.comfyApiKey);
      if (!isConnected) throw new Error("Não foi possível conectar ao ComfyUI.");

      for (let i = 0; i < scenes.length; i++) {
          const scene = scenes[i];
          setBatchAnimationProgress({ current: i + 1, total: scenes.length });
          toast.loading(`Gerando Cena ${i + 1}/${scenes.length} (${scene.type})...`, { id: 'batch-anim' });
          
          let baseImageToUse = '';
          let referenceImgObj = null;

          if (scene.type === 'CORTA') {
              referenceImgObj = sortedImagesForCorta[cortaIndex];
              baseImageToUse = sortedImagesForCorta[cortaIndex].imageUrl;
              cortaIndex++;
          } else {
             if (!lastGeneratedLastFrameBase64) {
                 throw new Error(`Cena ${i+1} é [CONTINUA], mas ocorreu um erro ao extrair ou gerar o frame do vídeo anterior.`);
             }
             baseImageToUse = lastGeneratedLastFrameBase64;
          }

          const uploadedFilename = await uploadImageToComfyUI(settings.comfyUrl, baseImageToUse, settings.comfyApiKey);

          let workflow = JSON.parse(settings.comfyVideoWorkflow);
          workflow = injectImageIntoWorkflow(workflow, uploadedFilename);
          workflow = injectPromptIntoWorkflow(workflow, scene.prompt, settings.negativePrompt);

          const promptId = await queuePrompt(settings.comfyUrl, workflow, settings.comfyApiKey);
          const history = await waitForPromptCompletion(settings.comfyUrl, promptId, settings.comfyApiKey);
          
          const outputs = history[promptId].outputs;
          let filename, subfolder, type, directUrl;

          for (const nodeId in outputs) {
            if (outputs[nodeId].gifs && outputs[nodeId].gifs.length > 0) {
              const media = outputs[nodeId].gifs[0];
              if (media.url) { directUrl = media.url; } else {
                  filename = media.filename; subfolder = media.subfolder; type = media.type;
              }
              break;
            } else if (outputs[nodeId].images && outputs[nodeId].images.length > 0) {
              const media = outputs[nodeId].images[0];
              if (media.url) { directUrl = media.url; break; } 
              else if (media.filename.endsWith('.mp4') || media.filename.endsWith('.webm') || media.filename.endsWith('.gif')) {
                filename = media.filename; subfolder = media.subfolder; type = media.type;
                break;
              }
            }
          }

          if (!filename && !directUrl) throw new Error("Vídeo falhou no ComfyUI.");

          let videoBase64: string;
          if (directUrl) {
              const response = await fetch('/api/proxy', {
                  method: 'POST',
                  headers: { 'Content-Type': 'application/json' },
                  body: JSON.stringify({ url: directUrl })
              });
              if (!response.ok) throw new Error(`Falha ao baixar vídeo.`);
              const blob = await response.blob();
              videoBase64 = await new Promise<string>((resolve, reject) => {
                  const reader = new FileReader();
                  reader.onloadend = () => {
                      if (typeof reader.result === 'string') resolve(reader.result);
                      else reject(new Error("Erro de blob"));
                  };
                  reader.onerror = reject;
                  reader.readAsDataURL(blob);
              });
          } else {
              videoBase64 = await fetchMediaAsBase64(settings.comfyUrl, filename, subfolder, type, settings.comfyApiKey);
          }

          if (scene.type === 'CORTA' && referenceImgObj && updateGeneratedImage) {
              // Edit the existing CORTA gallery item
              updateGeneratedImage(referenceImgObj.id, { 
                  videoUrl: videoBase64, 
                  videoPrompt: scene.prompt 
              });
          } else {
             // It's a CONTINUA, we must add a new gallery item dynamically
             const newGalleryItem: GeneratedImage = {
                  id: crypto.randomUUID(),
                  prompt: `[CONTINUA] ` + scene.prompt,
                  imageUrl: baseImageToUse, // We save the extracted frame as its gallery representation thumbnail
                  videoUrl: videoBase64,
                  timestamp: Date.now() + i, // Keeps them sorted after
                  videoPrompt: scene.prompt
             }
             addGeneratedImage(newGalleryItem);
          }

          toast.loading(`Extraindo frame da Cena ${i + 1}...`, { id: 'batch-anim' });
          try {
             lastGeneratedLastFrameBase64 = await extractLastFrame(videoBase64);
          } catch(err) {
             console.error("Frame extraction error: ", err);
             throw new Error(`Falha ao extrair frame do vídeo na cena ${i+1}`);
          }
      }
      
      toast.success("Roteiro de Animação Concluído!", { id: 'batch-anim' });
      setScriptedBatchText('');
    } catch(e: any) {
      toast.error(e.message || "Erro fatal no roteiro.", { id: 'batch-anim' });
    } finally {
      setIsBatchAnimating(false);
      setBatchAnimationProgress({ current: 0, total: 0 });
    }
  };

  const startBatchAnimation = async () => {
    if (settings.videoProvider !== 'comfyui' || !settings.comfyUrl || !settings.comfyVideoWorkflow) {
      toast.error("Configure o ComfyUI para vídeos nas configurações primeiro.");
      return;
    }

    // Filter images that don't have a videoUrl yet
    const imagesToAnimate = safeImages.filter(img => !img.videoUrl);
    
    if (imagesToAnimate.length === 0) {
      toast.success("Todas as imagens já possuem vídeo!");
      return;
    }

    setIsBatchAnimating(true);
    setBatchAnimationProgress({ current: 0, total: imagesToAnimate.length });

    try {
      // Check connection first
      const isConnected = await checkComfyConnection(settings.comfyUrl, settings.comfyApiKey);
      if (!isConnected) {
        throw new Error("Não foi possível conectar ao ComfyUI. Verifique a URL.");
      }

      for (let i = 0; i < imagesToAnimate.length; i++) {
        const img = imagesToAnimate[i];
        setBatchAnimationProgress({ current: i + 1, total: imagesToAnimate.length });
        
        try {
          // 1. Upload image to ComfyUI
          toast.loading(`Enviando imagem ${i + 1}/${imagesToAnimate.length}...`, { id: 'batch-anim' });
          const uploadedFilename = await uploadImageToComfyUI(settings.comfyUrl, img.imageUrl, settings.comfyApiKey);

          // 2. Prepare workflow
          let workflow = JSON.parse(settings.comfyVideoWorkflow);
          workflow = injectImageIntoWorkflow(workflow, uploadedFilename);
          
          // Inject prompt if available (use videoPrompt if exists, else image prompt)
          const promptToInject = img.videoPrompt || img.prompt;
          workflow = injectPromptIntoWorkflow(workflow, promptToInject, settings.negativePrompt);

          // 3. Queue prompt
          toast.loading(`Processando vídeo ${i + 1}/${imagesToAnimate.length}...`, { id: 'batch-anim' });
          const promptId = await queuePrompt(settings.comfyUrl, workflow, settings.comfyApiKey);

          // 4. Wait for completion
          const history = await waitForPromptCompletion(settings.comfyUrl, promptId, settings.comfyApiKey);

          // 5. Extract video
          const outputs = history[promptId].outputs;
          let filename, subfolder, type, directUrl;

          for (const nodeId in outputs) {
            // ComfyUI usually outputs videos as gifs or in a specific format
            if (outputs[nodeId].gifs && outputs[nodeId].gifs.length > 0) {
              const media = outputs[nodeId].gifs[0];
              if (media.url) {
                  directUrl = media.url;
              } else {
                  filename = media.filename;
                  subfolder = media.subfolder;
                  type = media.type;
              }
              break;
            } else if (outputs[nodeId].images && outputs[nodeId].images.length > 0) {
              // Sometimes videos are under 'images' depending on the node
              const media = outputs[nodeId].images[0];
              if (media.url) {
                  directUrl = media.url;
                  break;
              } else if (media.filename.endsWith('.mp4') || media.filename.endsWith('.webm') || media.filename.endsWith('.gif')) {
                filename = media.filename;
                subfolder = media.subfolder;
                type = media.type;
                break;
              }
            }
          }

          if (!filename && !directUrl) {
            throw new Error("Nenhum vídeo retornado pelo ComfyUI para esta imagem.");
          }

          toast.loading(`Baixando vídeo ${i + 1}/${imagesToAnimate.length}...`, { id: 'batch-anim' });
          let videoBase64;
          if (directUrl) {
              const response = await fetch('/api/proxy', {
                  method: 'POST',
                  headers: { 'Content-Type': 'application/json' },
                  body: JSON.stringify({ url: directUrl })
              });
              if (!response.ok) throw new Error(`Failed to fetch video from URL: ${response.statusText}`);
              const blob = await response.blob();
              videoBase64 = await new Promise<string>((resolve, reject) => {
                  const reader = new FileReader();
                  reader.onloadend = () => {
                      if (typeof reader.result === 'string') resolve(reader.result);
                      else reject(new Error("Failed to convert blob to base64"));
                  };
                  reader.onerror = reject;
                  reader.readAsDataURL(blob);
              });
          } else {
              videoBase64 = await fetchMediaAsBase64(settings.comfyUrl, filename, subfolder, type, settings.comfyApiKey);
          }

          // 6. Update image with videoUrl
          if (updateGeneratedImage) {
            updateGeneratedImage(img.id, { videoUrl: videoBase64 });
          }

        } catch (err: any) {
          console.error(`Erro ao animar imagem ${img.id}:`, err);
          toast.error(`Falha ao animar imagem ${i + 1}: ${err.message}`);
          // Continue to next image even if one fails
        }
      }
      
      toast.success("Animação em lote concluída!", { id: 'batch-anim' });
    } catch (error: any) {
      toast.error(error.message || "Erro na animação em lote.", { id: 'batch-anim' });
    } finally {
      setIsBatchAnimating(false);
      setBatchAnimationProgress({ current: 0, total: 0 });
    }
  };

  const downloadAllAsZip = async (includeTextFiles: boolean = true) => {
    if (safeImages.length === 0) return;
    
    setIsZipping(true);
    const dateStr = new Date().toISOString().replace(/[:.]/g, '-').replace('T', '_').slice(0, 19);
    const folderName = `gemini_story_batch_${dateStr}`;
    const zip = new JSZip();
    const folder = zip.folder(folderName);

    // Important: Sort chronological (Oldest First = Scene 1, Scene 2...)
    const sortedImages = [...safeImages].sort((a, b) => a.timestamp - b.timestamp);

    if (includeTextFiles) {
        // Generate the Master Script
        const masterScript = generateMasterScript(sortedImages);
        folder?.file("_ROTEIRO_MESTRE.txt", masterScript);
    }

    // Process images and videos
    sortedImages.forEach((img, index) => {
        if (!img.imageUrl || !img.imageUrl.includes(',')) {
            return; // Skip invalid images to prevent crash
        }
        try {
            const base64Data = img.imageUrl.split(',')[1];
            if (base64Data) {
                // Strict numbering: Cena_001.png
                // Removed ID suffix to ensure perfect OS sorting
                const sceneNum = padNumber(index + 1);
                const fileName = `Cena_${sceneNum}.png`;
                
                folder?.file(fileName, base64Data, { base64: true });
            }

            if (img.videoUrl && img.videoUrl.includes(',')) {
                const videoBase64Data = img.videoUrl.split(',')[1];
                if (videoBase64Data) {
                    const sceneNum = padNumber(index + 1);
                    // Determine extension based on mime type if possible, default to mp4
                    let ext = 'mp4';
                    if (img.videoUrl.startsWith('data:image/gif')) ext = 'gif';
                    else if (img.videoUrl.startsWith('data:video/webm')) ext = 'webm';
                    
                    const videoFileName = `Cena_${sceneNum}.${ext}`;
                    folder?.file(videoFileName, videoBase64Data, { base64: true });
                }
            }
        } catch (e) {
            console.error("Skipping bad image/video data", e);
        }
    });

    try {
        const content = await zip.generateAsync({ type: "blob" });
        const url = window.URL.createObjectURL(content);
        const link = document.createElement('a');
        link.href = url;
        link.download = `${folderName}.zip`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
    } catch (error) {
        console.error("Falha ao compactar imagens", error);
        toast.error("Falha ao criar arquivo ZIP. Tente baixar individualmente.");
    } finally {
        setIsZipping(false);
    }
  };

  const downloadCSV = () => {
    if (safeImages.length === 0) return;
    
    const sortedImages = [...safeImages].sort((a, b) => a.timestamp - b.timestamp);
    
    // Create CSV header
    let csvContent = "Cena,Arquivo,Prompt de Imagem,Prompt de Vídeo,Proporção,Data\n";
    
    sortedImages.forEach((img, index) => {
        const sceneNum = padNumber(index + 1);
        const fileName = `Cena_${sceneNum}.png`;
        const imgPrompt = `"${(img.prompt || '').replace(/"/g, '""')}"`;
        const vidPrompt = `"${(img.videoPrompt || '').replace(/"/g, '""')}"`;
        const date = new Date(img.timestamp).toLocaleString();
        
        csvContent += `${sceneNum},${fileName},${imgPrompt},${vidPrompt},${img.aspectRatio},"${date}"\n`;
    });
    
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.setAttribute("href", url);
    link.setAttribute("download", `Story_Batch_${new Date().toISOString().slice(0,10)}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const copyVideoPrompt = (prompt: string, id: string) => {
      navigator.clipboard.writeText(prompt);
      setCopiedPromptId(id);
      setTimeout(() => setCopiedPromptId(null), 2000);
  };

  const handleClearGallery = () => {
      if (onClearGallery) {
          onClearGallery();
          setShowClearConfirm(false);
      }
  };

  const handleRemoveImage = (id: string) => {
      if (onRemoveImage) {
          onRemoveImage(id);
          setDeletingId(null);
      }
  };

  return (
    <div className="bg-slate-900 rounded-xl border border-slate-700 h-full flex flex-col">
      <div className="p-6 border-b border-slate-700 flex flex-col xl:flex-row justify-between items-start xl:items-center gap-4">
        <h2 className="text-xl font-bold text-white flex items-center gap-2">
          <ImageIcon className="w-5 h-5 text-purple-400" />
          Galeria <span className="text-slate-500 text-sm font-normal">({safeImages.length} itens)</span>
        </h2>
        
        <div className="flex flex-wrap gap-2 w-full xl:w-auto justify-end items-center">
            {/* DELETE ALL BUTTON - Highlighted for visibility */}
            {onClearGallery && safeImages.length > 0 && (
                showClearConfirm ? (
                    <div className="flex items-center gap-2 animate-in fade-in slide-in-from-right-4 duration-200">
                        <span className="text-sm font-bold text-red-400">Tem certeza?</span>
                        <button 
                            onClick={handleClearGallery}
                            className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg text-sm font-bold border border-red-500 transition-all flex items-center gap-2 shadow-lg"
                        >
                            Sim, Esvaziar
                        </button>
                        <button 
                            onClick={() => setShowClearConfirm(false)}
                            className="px-3 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg text-sm border border-slate-600"
                        >
                            Cancelar
                        </button>
                    </div>
                ) : (
                    <button 
                        onClick={() => setShowClearConfirm(true)}
                        className="px-4 py-2 bg-slate-800 hover:bg-red-900/40 text-slate-300 hover:text-red-400 border border-slate-600 hover:border-red-500 rounded-lg text-sm font-bold transition-all flex items-center gap-2"
                    >
                        <Trash2 className="w-4 h-4" /> Esvaziar Galeria
                    </button>
                )
            )}

            {/* Copy Animation Prompts Only */}
             <button 
                onClick={copyAnimationPromptsOnly}
                disabled={safeImages.length === 0}
                className="px-3 py-2 bg-slate-800 hover:bg-slate-700 text-purple-300 border border-slate-600 rounded-lg text-sm font-bold flex items-center gap-2 transition-colors"
                title="Copiar APENAS prompts de animação (Lista Limpa para Batch)"
            >
                {animPromptsCopied ? <Check className="w-4 h-4" /> : <Clapperboard className="w-4 h-4" />}
                <span className="hidden lg:inline">{animPromptsCopied ? "Copiado!" : "Exp. Prompts Anim"}</span>
            </button>

            {/* Copy Script Button */}
             <button 
                onClick={copyMasterScript}
                disabled={safeImages.length === 0}
                className="px-3 py-2 bg-slate-800 hover:bg-slate-700 text-blue-300 border border-slate-600 rounded-lg text-sm font-bold flex items-center gap-2 transition-colors"
                title="Copiar a lista completa de prompts (Imagem & Vídeo) para a área de transferência"
            >
                {scriptCopied ? <Check className="w-4 h-4" /> : <FileText className="w-4 h-4" />}
                <span className="hidden lg:inline">{scriptCopied ? "Copiado!" : "Copiar Roteiro"}</span>
            </button>

            <button 
                onClick={startBatchAnimation}
                disabled={safeImages.length === 0 || isBatchAnimating}
                className={`px-3 py-2 rounded-lg text-sm font-bold flex items-center gap-2 transition-colors ${
                    safeImages.length === 0 || isBatchAnimating
                    ? 'bg-slate-800 text-slate-500 cursor-not-allowed border border-slate-700'
                    : 'bg-orange-600 hover:bg-orange-500 text-white shadow-lg shadow-orange-900/50'
                }`}
                title="Animar todas as imagens que ainda não possuem vídeo usando ComfyUI"
            >
                {isBatchAnimating ? (
                    <><Loader2 className="w-4 h-4 animate-spin" /> Animando {batchAnimationProgress.current}/{batchAnimationProgress.total}...</>
                ) : (
                    <><Clapperboard className="w-4 h-4" /> Animar Faltantes</>
                )}
            </button>

            <button 
                onClick={() => setShowScriptModal(true)}
                disabled={safeImages.length === 0 || isBatchAnimating}
                className={`flex-1 md:flex-none px-4 py-2 rounded-lg font-bold text-sm flex items-center justify-center gap-2 transition-all ${
                    safeImages.length === 0 || isBatchAnimating
                    ? 'bg-slate-800 text-slate-500 cursor-not-allowed border border-slate-700'
                    : 'bg-blue-600 hover:bg-blue-500 text-white shadow-lg shadow-blue-900/50'
                }`}
                title="Animar seguindo um roteiro com CORTA e CONTINUA"
            >
                <FileText className="w-4 h-4" /> Animação por Roteiro
            </button>

            <button 
                onClick={downloadCSV}
                disabled={safeImages.length === 0}
                className="px-3 py-2 bg-slate-800 hover:bg-slate-700 text-green-300 border border-slate-600 rounded-lg text-sm font-bold flex items-center gap-2 transition-colors"
                title="Exportar dados como CSV"
            >
                <Table className="w-4 h-4" /> CSV
            </button>

            <button 
                onClick={() => downloadAllAsZip(false)}
                disabled={safeImages.length === 0 || isZipping}
                className={`flex-1 md:flex-none px-4 py-2 rounded-lg font-bold text-sm flex items-center justify-center gap-2 transition-all ${
                    safeImages.length === 0 
                    ? 'bg-slate-800 text-slate-500 cursor-not-allowed' 
                    : 'bg-indigo-600 hover:bg-indigo-700 text-white shadow-lg shadow-indigo-900/50'
                }`}
                title="Baixar apenas as imagens, sem o arquivo de texto"
            >
                {isZipping ? (
                    <>Processando...</>
                ) : (
                    <>
                        <ImageIcon className="w-4 h-4" /> ZIP (Só Imagens)
                    </>
                )}
            </button>

            <button 
                onClick={() => downloadAllAsZip(true)}
                disabled={safeImages.length === 0 || isZipping}
                className={`flex-1 md:flex-none px-4 py-2 rounded-lg font-bold text-sm flex items-center justify-center gap-2 transition-all ${
                    safeImages.length === 0 
                    ? 'bg-slate-800 text-slate-500 cursor-not-allowed' 
                    : 'bg-purple-600 hover:bg-purple-700 text-white shadow-lg shadow-purple-900/50'
                }`}
                title="Baixar imagens e o roteiro em texto"
            >
                {isZipping ? (
                    <>Processando...</>
                ) : (
                    <>
                        <Archive className="w-4 h-4" /> ZIP (Completo)
                    </>
                )}
            </button>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-6">
        {safeImages.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-slate-500">
            <ImageIcon className="w-16 h-16 mb-4 opacity-20" />
            <p>Nenhuma imagem gerada ainda.</p>
            <p className="text-xs mt-2 opacity-50">As imagens são armazenadas temporariamente. Baixe-as antes de sair.</p>
          </div>
        ) : (
          <div className="flex flex-col gap-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
              {/* We map REVERSED for display (newest first), but download is chronological */}
              {currentImages.map((img) => (
                <div key={img.id} className="group bg-slate-800 rounded-lg overflow-hidden border border-slate-700 shadow-lg flex flex-col transition-transform hover:scale-[1.01] relative">
                
                {/* Processing Overlay */}
                {processingImageId === img.id && (
                    <div className="absolute inset-0 bg-black/80 z-50 flex flex-col items-center justify-center gap-2 text-blue-400">
                        <Loader2 className="w-8 h-8 animate-spin" />
                        <span className="text-xs font-bold animate-pulse">Processando...</span>
                    </div>
                )}

                {/* Confirm Delete Overlay (Individual) */}
                {deletingId === img.id && (
                     <div className="absolute inset-0 bg-red-900/90 z-50 flex flex-col items-center justify-center gap-3 p-4 text-center animate-in fade-in duration-200">
                        <AlertTriangle className="w-8 h-8 text-white mb-1" />
                        <p className="text-white font-bold text-sm">Excluir esta imagem?</p>
                        <div className="flex gap-2 w-full">
                            <button 
                                onClick={() => handleRemoveImage(img.id)}
                                className="flex-1 bg-white text-red-900 font-bold py-2 rounded text-xs hover:bg-slate-200"
                            >
                                Sim
                            </button>
                            <button 
                                onClick={() => setDeletingId(null)}
                                className="flex-1 bg-black/50 text-white font-bold py-2 rounded text-xs hover:bg-black/70"
                            >
                                Não
                            </button>
                        </div>
                     </div>
                )}

                {/* Edit Mode Overlay */}
                {editModeId === img.id && (
                    <div className="absolute inset-0 bg-slate-900/95 z-40 flex flex-col p-4 gap-2">
                        <div className="flex justify-between items-center text-white mb-1">
                            <span className="font-bold text-sm flex items-center gap-2"><Wand2 className="w-4 h-4 text-purple-400" /> Editar Imagem</span>
                            <button onClick={() => setEditModeId(null)} className="text-slate-500 hover:text-white"><X className="w-4 h-4" /></button>
                        </div>
                        <textarea 
                            value={editInstruction}
                            onChange={(e) => setEditInstruction(e.target.value)}
                            placeholder="Ex: Remova o braço extra, Mude o cabelo para azul..."
                            className="w-full flex-1 bg-black border border-slate-700 rounded p-2 text-sm text-white resize-none outline-none focus:border-purple-500"
                        />
                        <button 
                            onClick={() => handleEditRequest(img)}
                            className="w-full bg-purple-600 hover:bg-purple-700 text-white py-2 rounded text-sm font-bold transition-colors"
                        >
                            Gerar Correção
                        </button>
                    </div>
                )}

                {/* Edit Confirmation Overlay */}
                {pendingEdit && (
                    <div className="fixed inset-0 z-[110] bg-black/80 backdrop-blur-sm flex items-center justify-center p-4 animate-in fade-in duration-200">
                        <div className="bg-slate-900 border border-slate-700 rounded-xl p-6 max-w-md w-full shadow-2xl flex flex-col gap-4">
                            <div className="flex items-center gap-3 text-purple-400">
                                <Wand2 className="w-6 h-6" />
                                <h3 className="text-lg font-bold text-white">Confirmar Edição</h3>
                            </div>
                            
                            <p className="text-slate-300 text-sm">
                                Você está prestes a aplicar a edição: <br/>
                                <span className="italic text-purple-300">"{pendingEdit.instruction}"</span>
                            </p>

                            <div className="bg-slate-800 p-3 rounded border border-slate-700 flex gap-3 items-center">
                                <img src={pendingEdit.img.imageUrl} className="w-16 h-16 object-cover rounded bg-black" alt="Original" />
                                <div className="text-xs text-slate-400">
                                    <p>Imagem Original</p>
                                    <p className="font-mono text-[10px]">{pendingEdit.img.id.slice(0,8)}</p>
                                </div>
                            </div>

                            <p className="text-slate-400 text-xs">
                                Como deseja salvar o resultado?
                            </p>

                            <div className="flex flex-col gap-2">
                                <button 
                                    onClick={() => executeEdit(false)}
                                    className="w-full bg-purple-600 hover:bg-purple-700 text-white py-3 rounded-lg font-bold text-sm flex items-center justify-center gap-2 transition-colors"
                                >
                                    <Copy className="w-4 h-4" />
                                    Salvar como Nova Cópia (Recomendado)
                                </button>
                                
                                {updateGeneratedImage && (
                                    <button 
                                        onClick={() => executeEdit(true)}
                                        className="w-full bg-slate-800 hover:bg-red-900/50 text-slate-300 hover:text-red-300 border border-slate-700 hover:border-red-500/50 py-3 rounded-lg font-bold text-sm flex items-center justify-center gap-2 transition-all"
                                    >
                                        <RefreshCw className="w-4 h-4" />
                                        Substituir Imagem Original
                                    </button>
                                )}
                            </div>

                            <button 
                                onClick={() => setPendingEdit(null)}
                                className="mt-2 text-slate-500 hover:text-white text-sm underline decoration-slate-700 underline-offset-4"
                            >
                                Cancelar
                            </button>
                        </div>
                    </div>
                )}

                {/* Dynamic Aspect Ratio Container */}
                <div 
                    className={`relative ${getAspectRatioClass(img.aspectRatio)} bg-black overflow-hidden cursor-pointer group/image`}
                    onClick={() => onImageClick?.(img)}
                >
                  {img.videoUrl ? (
                    <video 
                      src={img.videoUrl} 
                      autoPlay 
                      loop 
                      muted 
                      playsInline
                      className="w-full h-full object-contain"
                    />
                  ) : (
                    <SafeImage 
                      src={img.imageUrl} 
                      alt={img.prompt} 
                      className="w-full h-full object-contain"
                    />
                  )}
                  
                  {/* Hover Controls */}
                  <div className="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-2" onClick={(e) => e.stopPropagation()}>
                     <button 
                        onClick={() => onImageClick?.(img)}
                        className="p-2 bg-slate-800 text-white rounded-full hover:bg-slate-700 transition-colors transform hover:scale-110 border border-slate-600"
                        title="Expandir (Tela Cheia)"
                     >
                        <ExternalLink className="w-4 h-4" />
                     </button>

                     <button 
                        onClick={() => downloadImage(img.videoUrl || img.imageUrl, `gemini-char-${img.id}.${img.videoUrl ? 'mp4' : 'png'}`)}
                        className="p-2 bg-white text-slate-900 rounded-full hover:bg-slate-200 transition-colors transform hover:scale-110"
                        title="Baixar"
                     >
                        <Download className="w-4 h-4" />
                     </button>

                     <button 
                        onClick={() => handleRegenerate(img)}
                        className="p-2 bg-blue-500 text-white rounded-full hover:bg-blue-400 transition-colors transform hover:scale-110"
                        title="Regenerar (Re-rolar)"
                     >
                        <RefreshCw className="w-4 h-4" />
                     </button>

                     <button 
                        onClick={() => {
                            setEditModeId(img.id);
                            setEditInstruction('');
                        }}
                        className="p-2 bg-purple-500 text-white rounded-full hover:bg-purple-400 transition-colors transform hover:scale-110"
                        title="Editar / Corrigir (Inpainting)"
                     >
                        <Wand2 className="w-4 h-4" />
                     </button>

                     {img.videoPrompt && (
                        <button 
                            onClick={() => setExpandedPromptId(expandedPromptId === img.id ? null : img.id)}
                            className="p-2 bg-pink-500 text-white rounded-full hover:bg-pink-400 transition-colors transform hover:scale-110"
                            title="Ver Prompt de Vídeo"
                        >
                            <Clapperboard className="w-4 h-4" />
                        </button>
                     )}
                  </div>
                  {/* Badge for Type */}
                  <div className="absolute top-2 left-2 bg-black/50 backdrop-blur-sm px-2 py-0.5 rounded text-[10px] text-white font-mono opacity-60 pointer-events-none">
                      {img.aspectRatio === '1:1' ? 'QUADRADO' : 'WIDE'}
                  </div>
                </div>
                
                {/* Video Prompt Overlay / Expansion */}
                {expandedPromptId === img.id && img.videoPrompt && (
                    <div className="bg-slate-950 p-3 border-b border-slate-700 flex flex-col gap-2">
                        <div className="flex justify-between items-center text-xs text-purple-400 font-bold uppercase">
                            <span>Prompt de Movimento</span>
                            <button onClick={() => copyVideoPrompt(img.videoPrompt!, img.id)} className="hover:text-white flex items-center gap-1">
                                {copiedPromptId === img.id ? <Check className="w-3 h-3" /> : <Copy className="w-3 h-3" />}
                                {copiedPromptId === img.id ? "Copiado" : "Copiar"}
                            </button>
                        </div>
                        <p className="text-xs text-slate-300 italic p-2 bg-slate-900 rounded border border-slate-800">
                            {img.videoPrompt}
                        </p>
                    </div>
                )}

                <div className="p-4 flex-1 flex flex-col justify-between">
                  <p className="text-slate-300 text-sm line-clamp-3 mb-2 font-light">
                    {img.prompt}
                  </p>
                  <div className="flex justify-between items-center text-xs text-slate-500 mt-2 border-t border-slate-700 pt-2">
                    <span>{new Date(img.timestamp).toLocaleTimeString()}</span>
                    <div className="flex items-center gap-2">
                         {/* DELETE BUTTON ALWAYS VISIBLE IN FOOTER */}
                        {onRemoveImage && (
                            <button 
                                onClick={(e) => {
                                    e.stopPropagation();
                                    setDeletingId(img.id);
                                }}
                                className="text-slate-600 hover:text-red-500 transition-colors p-1"
                                title="Excluir Imagem"
                            >
                                <Trash2 className="w-4 h-4" />
                            </button>
                        )}
                        {img.videoPrompt && <Clapperboard className="w-3 h-3 text-purple-500" />}
                        <span className="font-mono bg-slate-700 px-1.5 py-0.5 rounded text-slate-300">{img.aspectRatio}</span>
                    </div>
                  </div>
                </div>
              </div>
            ))}
            </div>
            
            {/* Pagination Controls */}
            {totalPages > 1 && (
              <div className="flex justify-center items-center gap-4 mt-4 pt-4 border-t border-slate-700">
                <button
                  onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                  disabled={currentPage === 1}
                  className="p-2 bg-slate-800 hover:bg-slate-700 text-white rounded-lg disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  <ChevronLeft className="w-5 h-5" />
                </button>
                <span className="text-slate-300 text-sm font-medium">
                  Página {currentPage} de {totalPages}
                </span>
                <button
                  onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                  disabled={currentPage === totalPages}
                  className="p-2 bg-slate-800 hover:bg-slate-700 text-white rounded-lg disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  <ChevronRight className="w-5 h-5" />
                </button>
              </div>
            )}
          </div>
        )}
      </div>

      {showScriptModal && (
          <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
            <div className="bg-slate-900 border border-slate-700 p-6 rounded-xl shadow-2xl w-full max-w-3xl flex flex-col gap-4">
              <div className="flex justify-between items-center">
                <h3 className="text-xl font-bold text-white flex items-center gap-2">
                  <Clapperboard className="text-blue-400" />
                  Geração de Vídeo Roteirizado em Lote
                </h3>
                <button onClick={() => setShowScriptModal(false)} className="text-slate-400 hover:text-white">
                  <X className="w-5 h-5" />
                </button>
              </div>

              <p className="text-sm text-slate-300">
                Digite ou cole o texto no campo abaixo.
              </p>

              <textarea 
                  value={scriptedBatchText}
                  onChange={(e) => setScriptedBatchText(e.target.value)}
                  placeholder="[CORTA] o macaco abre um sorriso...&#10;[CONTINUA] o macaco pega uma banana..."
                  className="w-full h-64 bg-slate-800 border border-slate-600 rounded-lg p-4 font-mono text-sm text-slate-300 outline-none focus:border-blue-500 resize-none leading-relaxed"
              ></textarea>

              <div className="flex justify-end gap-3 mt-2">
                  <button onClick={() => setShowScriptModal(false)} className="px-4 py-2 text-slate-400 hover:text-white">Cancelar</button>
                  <button 
                      onClick={startScriptedBatchAnimation}
                      disabled={isBatchAnimating || scriptedBatchText.trim() === ""}
                      className="px-6 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg font-bold flex items-center gap-2"
                  >
                      {isBatchAnimating ? <Loader2 className="w-4 h-4 animate-spin" /> : <Clapperboard className="w-4 h-4" />} 
                      Iniciar Sequência
                  </button>
              </div>
            </div>
          </div>
      )}

    </div>
  );
};

export default Gallery;