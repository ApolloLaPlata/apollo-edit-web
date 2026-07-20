import React, { useState, useEffect, useRef } from 'react';
import { ApiKey, Character, GenerationSettings, JobItem, GeneratedImage } from '../types';
import { generateVideoPromptText, rewritePromptForSafety } from '../services/geminiService';
import { generateImage } from '../services/imageGenerator';
import { executeWithKeyRotation } from '../utils/apiKeyRotation';
import toast from 'react-hot-toast';
import { Play, Loader2, StopCircle, AlertTriangle, ArrowRight, Settings2, Clock, Zap, Save, Clapperboard, ShieldAlert, PauseCircle, Download, CheckSquare, Square, Activity, Pencil, X, RefreshCw, Image as ImageIcon, GripVertical, Trash2 } from 'lucide-react';
import JSZip from 'jszip';
import { ASPECT_RATIOS, MODELS } from '../constants';

interface JobRunnerProps {
  apiKeys: ApiKey[];
  setApiKeys: React.Dispatch<React.SetStateAction<ApiKey[]>>;
  characters: Character[];
  settings: GenerationSettings;
  onUpdateSetting: (field: keyof GenerationSettings, value: any) => void;
  addGeneratedImage: (img: GeneratedImage) => void;
  updateGeneratedImage?: (id: string, updates: Partial<GeneratedImage>) => void;
  onNavigateToSettings: () => void;
  generatedImages: GeneratedImage[];
  onImageClick?: (image: GeneratedImage) => void;
}

const JobRunner: React.FC<JobRunnerProps> = ({
  apiKeys,
  setApiKeys,
  characters,
  settings,
  onUpdateSetting,
  addGeneratedImage,
  updateGeneratedImage,
  onNavigateToSettings,
  generatedImages,
  onImageClick
}) => {
  const [promptInput, setPromptInput] = useState('');
  const [jobs, setJobs] = useState<JobItem[]>([]);
  const jobsRef = useRef<JobItem[]>([]);

  // Keep ref in sync
  useEffect(() => {
      jobsRef.current = jobs;
  }, [jobs]);
  const [isProcessing, setIsProcessing] = useState(false);
  const isProcessingRef = useRef(false);
  useEffect(() => {
      isProcessingRef.current = isProcessing;
  }, [isProcessing]);
  const [currentKeyIndex, setCurrentKeyIndex] = useState(0);
  const abortControllerRef = useRef<AbortController | null>(null);
  const jobAbortControllerRef = useRef<AbortController | null>(null);
  const [isQueueLoaded, setIsQueueLoaded] = useState(false);
  
  // Safety Feature: Defaults to true to protect large batches
  const [pauseOnError, setPauseOnError] = useState(true);
  
  // Shared IP Warning State
  // Removed showIpWarning state
  
  // Editing State
  const [editingJobId, setEditingJobId] = useState<string | null>(null);
  const [editPromptText, setEditPromptText] = useState('');

  const [draggedJobIndex, setDraggedJobIndex] = useState<number | null>(null);

  // Auto-scroll ref
  const jobListRef = useRef<HTMLDivElement>(null);

  // Ref to access latest keys inside async loop
  const apiKeysRef = useRef(apiKeys);
  useEffect(() => { apiKeysRef.current = apiKeys; }, [apiKeys]);

  // Filter only active keys for processing
  const activeKeys = apiKeys.filter(k => k.isActive);
  const hasActiveKeys = activeKeys.length > 0;
  
  // Key Health Stats
  const healthyKeysCount = activeKeys.filter(k => k.errorCount === 0).length;
  const errorKeysCount = activeKeys.filter(k => k.errorCount > 0).length;

  // Restore queue from localStorage on mount
  useEffect(() => {
    const savedQueue = localStorage.getItem('gemini_job_queue');
    if (savedQueue) {
        try {
            const parsedJobs: JobItem[] = JSON.parse(savedQueue);
            
            // Re-hydrate images from the full gallery (IndexedDB source via App prop)
            // Since we strip image data when saving to LS to save space, we need to find it again via ID
            const hydratedJobs = parsedJobs.map(job => {
                if (job.status === 'completed' && job.result) {
                    // Try to find the image in the current loaded gallery
                    const foundImage = generatedImages.find(img => img.id === job.result!.id);
                    if (foundImage) {
                        return { ...job, result: foundImage };
                    }
                }
                return job;
            });
            setJobs(hydratedJobs);
        } catch (e) {
            console.error("Failed to restore queue", e);
        }
    }
    setIsQueueLoaded(true);
  }, []); 

  // Save queue to localStorage whenever it changes
  // This covers "every minute" implicitly by saving on every significant change (add, update, finish)
  useEffect(() => {
    if (!isQueueLoaded) return;

    const saveQueue = () => {
        const queueToSave = jobs.map(job => {
            const jobCopy = { ...job };
            // Optimization: Do NOT save the full base64 image string to localStorage
            // It will hit the 5MB quota instantly. We just save the metadata.
            if (jobCopy.result) {
                jobCopy.result = {
                    ...jobCopy.result,
                    imageUrl: '' // Clear data to prevent LocalStorage quota exceeded
                };
            }
            return jobCopy;
        });
        
        try {
            localStorage.setItem('gemini_job_queue', JSON.stringify(queueToSave));
        } catch (e) {
            console.warn("Failed to save queue to localStorage", e);
        }
    };

    saveQueue();
  }, [jobs, isQueueLoaded]);

  // Generate job objects from text input
  const generateJobsFromInput = () => {
    const lines = promptInput.split('\n').filter((line) => line.trim().length > 0);
    return lines.map((line) => ({
      id: crypto.randomUUID(),
      prompt: line.trim(),
      status: 'pending' as const,
    }));
  };

  const handleLoadQueue = () => {
    const newJobs = generateJobsFromInput();
    if (newJobs.length > 0) {
        jobsRef.current = [...jobsRef.current, ...newJobs];
        setJobs(jobsRef.current);
        setPromptInput('');
    }
  };

  const handleExportForAutoVeo = async () => {
    const activeJobs = jobs.length > 0 ? jobs : generateJobsFromInput();
    if (activeJobs.length === 0) {
        toast.error("A fila está vazia. Insira ou carregue os prompts primeiro.");
        return;
    }

    const toastId = toast.loading("Preparando exportação para Auto VEO/FLOW...");
    try {
        const zip = new JSZip();

        // 1. Text file with prompts
        const promptsText = activeJobs.map(j => j.prompt).join('\n\n');
        zip.file('prompts.txt', promptsText);

        // 2. Identify characters and extract primary images
        const usedCharactersFound = new Set<string>();
        
        characters.forEach(char => {
            const hasChar = activeJobs.some(j => j.prompt.toLowerCase().includes(char.name.toLowerCase()));
            if (hasChar && char.previewUrl) {
                // Determine format
                const isPng = char.previewUrl.startsWith("data:image/png");
                const isWebp = char.previewUrl.startsWith("data:image/webp");
                const extension = isPng ? 'png' : (isWebp ? 'webp' : 'jpg');
                
                const base64Data = char.previewUrl.replace(/^data:image\/\w+;base64,/, "");
                const safeFileName = `${char.name.replace(/[^a-zA-Z0-9#@_-]/g, '')}.${extension}`;
                zip.file(`imagens_referencia/${safeFileName}`, base64Data, {base64: true});
                usedCharactersFound.add(char.name);
            }
        });

        // Generate Zip
        const content = await zip.generateAsync({ type: 'blob' });
        const a = document.createElement('a');
        a.href = URL.createObjectURL(content);
        a.download = `AutoVEO_Export_${new Date().toISOString().split('T')[0]}.zip`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);

        toast.success(`Exportação concluída! ${usedCharactersFound.size} personagens detectados.`, { id: toastId });
    } catch (e) {
        console.error(e);
        toast.error("Erro ao gerar exportação.", { id: toastId });
    }
  };

  const stopProcessing = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    if (jobAbortControllerRef.current) {
      jobAbortControllerRef.current.abort();
    }
    isProcessingRef.current = false;
    setIsProcessing(false);
  };

  const handleRewriteCensored = async () => {
    if (!promptInput.trim()) {
        toast.error("Cole alguns prompts na caixa de texto primeiro.");
        return;
    }
    const lines = promptInput.split('\n').filter(l => l.trim().length > 0);
    const toastId = toast.loading(`Reescrevendo ${lines.length} prompt(s) com IA...`);
    setIsProcessing(true);
    
    try {
        const newLines = [];
        for (const line of lines) {
            // 1. Alias characters
            let aliasedPrompt = line;
            const characterMap: { alias: string, originalName: string }[] = [];
            
            const extractedHashtags = (line.match(/#[\p{L}\p{N}_-]+/gu) || []);
            const uniqueTags = [...new Set(extractedHashtags)];
            
            uniqueTags.forEach((tag, idx) => {
                const alias = `#Personagem${idx + 1}`;
                characterMap.push({ alias, originalName: tag });
                const escapedTag = tag.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
                const regex = new RegExp(`(${escapedTag})`, 'gi');
                aliasedPrompt = aliasedPrompt.replace(regex, alias);
            });
            
            const usedChars = characters.filter(char => line.toLowerCase().includes(char.name.toLowerCase()));
            const sortedUsedChars = [...usedChars].sort((a, b) => b.name.length - a.name.length);
            let nextIdx = uniqueTags.length + 1;
            
            sortedUsedChars.forEach((char) => {
                const charClean = char.name.toLowerCase().replace('#', '');
                const alreadyMapped = uniqueTags.some(t => t.toLowerCase().replace('#', '') === charClean);
                
                if (!alreadyMapped) {
                    const alias = `#Personagem${nextIdx++}`;
                    characterMap.push({ alias, originalName: char.name });
                    const regex = new RegExp(`(\\b${char.name.replace('#','')}\\b)`, 'gi');
                    aliasedPrompt = aliasedPrompt.replace(regex, alias);
                }
            });

            // 2. Rewrite
            let rewritten = await executeWithKeyRotation(
                apiKeysRef,
                setApiKeys,
                async (apiKey) => await rewritePromptForSafety(aliasedPrompt, settings, apiKey)
            );

            // 3. Un-alias characters back to original names so it works normally in the system later
            if (rewritten && characterMap.length > 0) {
                // Sort by alias length descending so higher numbers (like #Personagem10) are replaced before #Personagem1
                const sortedMap = [...characterMap].sort((a, b) => b.alias.length - a.alias.length);
                sortedMap.forEach(mapping => {
                   // Ensure it's not followed by another digit (so #Personagem1 doesn't match #Personagem10)
                   const regex = new RegExp(`(${mapping.alias})(?!\\d)`, 'gi');
                   rewritten = rewritten!.replace(regex, mapping.originalName);
                });
            }

            newLines.push(rewritten || line);
        }
        setPromptInput(newLines.join('\n\n'));
        toast.success("Prompts reescritos com sucesso!", { id: toastId });
    } catch (e: any) {
        console.error(e);
        toast.error(`Erro ao reescrever: ${e.message}`, { id: toastId });
    } finally {
        setIsProcessing(false);
    }
  };

  const pauseJobAndBatch = (jobId: string) => {
      const job = jobsRef.current.find(j => j.id === jobId);
      if (job?.status === 'processing') {
          // Abort the whole batch so it stops
          if (abortControllerRef.current) {
              abortControllerRef.current.abort();
          }
          // Abort the current job
          if (jobAbortControllerRef.current) {
              jobAbortControllerRef.current.abort();
          }
      }
  };

  const sleep = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

  // Helper to update a single job status safely without overwriting the whole list
  const updateJobStatus = (id: string, updates: Partial<JobItem>) => {
      // Update ref immediately for synchronous access in loops
      jobsRef.current = jobsRef.current.map(job => 
          job.id === id ? { ...job, ...updates } : job
      );
      
      // Update state for UI
      setJobs(jobsRef.current);
  };

  const startEditing = (job: JobItem) => {
      setEditingJobId(job.id);
      setEditPromptText(job.prompt);
  };

  const saveEdit = () => {
      if (editingJobId) {
          updateJobStatus(editingJobId, { 
              prompt: editPromptText, 
              error: undefined,
              status: 'pending'
          });
          setEditingJobId(null);
          setEditPromptText('');
      }
  };

  const cancelEdit = () => {
      setEditingJobId(null);
      setEditPromptText('');
  };

  const regenerateJob = (jobId: string) => {
      updateJobStatus(jobId, { status: 'pending', error: undefined });
  };

  const removeJob = (jobId: string) => {
      const job = jobsRef.current.find(j => j.id === jobId);
      if (job?.status === 'processing') {
          // If we remove the currently processing job, we should abort the request
          // to save quota. This will stop the batch, but the user can restart it.
          if (abortControllerRef.current) {
              abortControllerRef.current.abort();
          }
          if (jobAbortControllerRef.current) {
              jobAbortControllerRef.current.abort();
          }
          isProcessingRef.current = false;
          setIsProcessing(false);
      }
      
      const newJobs = jobsRef.current.filter(j => j.id !== jobId);
      jobsRef.current = newJobs;
      setJobs(newJobs);
  };

  const downloadJobImage = (job: JobItem) => {
      if (job.result && job.result.imageUrl) {
          const link = document.createElement('a');
          link.href = job.result.imageUrl;
          link.download = `job_${job.id.slice(0,8)}.png`;
          document.body.appendChild(link);
          link.click();
          document.body.removeChild(link);
      }
  };

  // Unified Model Selection Logic
  const currentModelValue = settings.imageProvider === 'comfyui' ? 'comfyui' : settings.imageProvider === 'flux_modal' ? 'flux_modal' : settings.imageProvider === 'flux_pulid' ? 'flux_pulid' : settings.modelId;

  const handleModelChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
      const newModelId = e.target.value;
      if (newModelId === 'comfyui') {
          onUpdateSetting('imageProvider', 'comfyui');
      } else if (newModelId === 'flux_modal') {
          onUpdateSetting('imageProvider', 'flux_modal');
      } else if (newModelId === 'flux_pulid') {
          onUpdateSetting('imageProvider', 'flux_pulid');
      } else {
          onUpdateSetting('imageProvider', 'gemini');
          onUpdateSetting('modelId', newModelId);
      }
  };

  const handleDragStart = (e: React.DragEvent, index: number) => {
      setDraggedJobIndex(index);
      e.dataTransfer.effectAllowed = 'move';
      // Make it slightly transparent while dragging
      (e.target as HTMLElement).style.opacity = '0.5';
  };

  const handleDragEnd = (e: React.DragEvent) => {
      setDraggedJobIndex(null);
      (e.target as HTMLElement).style.opacity = '1';
  };

  const handleDragOver = (e: React.DragEvent) => {
      e.preventDefault();
      e.dataTransfer.dropEffect = 'move';
  };

  const handleDrop = (e: React.DragEvent, targetIndex: number) => {
      e.preventDefault();
      if (draggedJobIndex === null || draggedJobIndex === targetIndex) return;

      const newJobs = [...jobsRef.current];
      const draggedJob = newJobs[draggedJobIndex];
      
      // Remove from old position
      newJobs.splice(draggedJobIndex, 1);
      // Insert at new position
      newJobs.splice(targetIndex, 0, draggedJob);
      
      jobsRef.current = newJobs;
      setJobs(newJobs);
  };

  const startBatchProcessing = async () => {
    if (isProcessingRef.current) return;
    
    // 1. Validate Keys based on Provider
    if (activeKeys.length === 0) {
        toast.error("Nenhuma chave Gemini ativa encontrada. Por favor adicione nas Configurações.");
        return;
    }

    // Auto-load capability if queue is empty but input has text
    if (jobsRef.current.filter(j => j.status === 'pending').length === 0 && promptInput.trim().length > 0) {
        const newJobs = generateJobsFromInput();
        jobsRef.current = [...jobsRef.current, ...newJobs];
        setJobs(jobsRef.current);
        setPromptInput('');
    }

    if (jobsRef.current.filter(j => j.status === 'pending').length === 0) return;

    isProcessingRef.current = true;
    setIsProcessing(true);
    const controller = new AbortController();
    abortControllerRef.current = controller;

    const keyIdx = currentKeyIndex;

    // Loop continuously until there are no more pending jobs
    while (true) {
        if (controller.signal.aborted) break;

        // Find the FIRST pending job in the current queue (maintaining original order)
        const currentJobs = jobsRef.current;
        const pendingJobIndex = currentJobs.findIndex(j => j.status === 'pending');
        
        if (pendingJobIndex === -1) {
            // No more pending jobs
            break;
        }

        const currentJob = currentJobs[pendingJobIndex];
        const jobId = currentJob.id;

        // Determine previousResultImage based on the job immediately preceding this one
        let previousResultImage: string | undefined = undefined;
        for (let k = pendingJobIndex - 1; k >= 0; k--) {
            if (currentJobs[k].status === 'completed' && currentJobs[k].result?.imageUrl) {
                previousResultImage = currentJobs[k].result!.imageUrl;
                break;
            }
        }

        // Apply Delay
        if (settings.delayBetweenRequests > 0) {
            await sleep(settings.delayBetweenRequests);
        }
        
        if (controller.signal.aborted) break;

        updateJobStatus(jobId, { status: 'processing', error: undefined });

        let success = false;
        let lastErrorMsg = "";

        if (controller.signal.aborted) break;

        const jobController = new AbortController();
        jobAbortControllerRef.current = jobController;

        const onBatchAbort = () => jobController.abort();
        controller.signal.addEventListener('abort', onBatchAbort);

        let charactersToUse = [...characters];

        try {
            const [imageUrl, videoPrompt] = await executeWithKeyRotation(
                apiKeysRef,
                setApiKeys,
                async (apiKey) => {
                    // Unified Image Generation
                    const imagePromise = generateImage(
                        apiKey,
                        currentJob.prompt,
                        charactersToUse,
                        settings,
                        previousResultImage // Use previous image for continuity
                    );

                    let videoPromptPromise = Promise.resolve<string | undefined>(undefined);
                    
                    if (settings.generateVideoPrompt) {
                         const prevPrompt = pendingJobIndex > 0 ? currentJobs[pendingJobIndex - 1]?.prompt : undefined;
                         const nextPrompt = pendingJobIndex < currentJobs.length - 1 ? currentJobs[pendingJobIndex + 1]?.prompt : undefined;

                             // Video Prompt (handled by textGenerator internally)
                             videoPromptPromise = generateVideoPromptText(
                                 currentJob.prompt, 
                                 settings,
                                 characters,
                                 prevPrompt,
                                 nextPrompt,
                                 apiKey
                             ).catch(err => {
                                 console.error("Failed to generate video prompt:", err);
                                 return undefined; // Don't fail the image generation if video prompt fails
                             });
                    }

                    return await Promise.all([imagePromise, videoPromptPromise]);
                },
                undefined, // Allow default maxRetries (Math.max(3, keys.length))
                jobController.signal
            );

            const result: GeneratedImage = {
                id: currentJob.result?.id || crypto.randomUUID(),
                prompt: currentJob.prompt,
                imageUrl: imageUrl,
                timestamp: currentJob.result?.timestamp || Date.now(),
                characterIds: characters
                    .filter(c => currentJob.prompt.toLowerCase().includes(c.name.toLowerCase()))
                    .map(c => c.id),
                aspectRatio: settings.aspectRatio,
                videoPrompt: videoPrompt || currentJob.result?.videoPrompt
            };

            updateJobStatus(jobId, { status: 'completed', result: result, error: undefined });
            previousResultImage = imageUrl;

            if (currentJob.result?.id && updateGeneratedImage) {
                await updateGeneratedImage(result.id, result);
            } else {
                await addGeneratedImage(result); 
            }
            success = true;

        } catch (error: any) {
            console.warn(`Attempt failed with provider ${settings.imageProvider}`, error);
            
            lastErrorMsg = error.message || "Erro desconhecido";
            
            if (lastErrorMsg.includes('AbortError')) {
                lastErrorMsg = "Operação cancelada pelo usuário.";
            } else if (lastErrorMsg.includes('timed out')) {
                lastErrorMsg = "Tempo limite excedido (120s). A API não respondeu.";
            } else if (lastErrorMsg.includes('quota') || lastErrorMsg.includes('429') || lastErrorMsg.includes('tentativas de rotação falharam')) {
                if (lastErrorMsg.includes('tentativas de rotação falharam')) {
                    lastErrorMsg = `Cota de API Excedida em TODAS as chaves. ${lastErrorMsg}`;
                } else {
                    lastErrorMsg = "Cota de API Excedida (Erro 429).";
                }
            } else if (lastErrorMsg.includes('400')) {
                lastErrorMsg = `Erro 400 (Bad Request). Verifique os parâmetros ou a imagem de contexto. Detalhes: ${lastErrorMsg}`;
            } else if (lastErrorMsg.toLowerCase().match(/safety|policy|blocked|censor|harm|violation|restricted|not allowed|unauthorized/i) || lastErrorMsg.includes('500')) {
                console.warn("Censorship detected, attempting to rewrite prompt...", currentJob.prompt);
                
                const retryCount = currentJob.retryCount || 0;
                if (retryCount >= 1) {
                    lastErrorMsg = "Censura detectada. Falha ao reescrever o prompt de forma segura após tentativa.";
                } else if (!jobController.signal.aborted) {
                    try {
                        updateJobStatus(jobId, { status: 'processing', error: "Censura detectada. Reescrevendo prompt..." });
                        
                        // Alias ALL hashtags and known characters before rewriting
                        let aliasedPrompt = currentJob.prompt;
                        const characterMap: { alias: string, originalName: string }[] = [];
                        
                        const extractedHashtags = (currentJob.prompt.match(/#[\p{L}\p{N}_-]+/gu) || []);
                        const uniqueTags = [...new Set(extractedHashtags)];
                        
                        uniqueTags.forEach((tag, idx) => {
                            const alias = `#Personagem${idx + 1}`;
                            characterMap.push({ alias, originalName: tag });
                            const escapedTag = tag.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
                            const regex = new RegExp(`(${escapedTag})`, 'gi');
                            aliasedPrompt = aliasedPrompt.replace(regex, alias);
                        });
                        
                        const usedChars = characters.filter(char => currentJob.prompt.toLowerCase().includes(char.name.toLowerCase()));
                        const sortedUsedChars = [...usedChars].sort((a, b) => b.name.length - a.name.length);
                        let nextIdx = uniqueTags.length + 1;
                        
                        sortedUsedChars.forEach((char) => {
                            const charClean = char.name.toLowerCase().replace('#', '');
                            const alreadyMapped = uniqueTags.some(t => t.toLowerCase().replace('#', '') === charClean);
                            
                            if (!alreadyMapped) {
                                const alias = `#Personagem${nextIdx++}`;
                                characterMap.push({ alias, originalName: char.name });
                                const regex = new RegExp(`(\\b${char.name.replace('#','')}\\b)`, 'gi');
                                aliasedPrompt = aliasedPrompt.replace(regex, alias);
                            }
                        });

                        const rewrittenPrompt = await executeWithKeyRotation(
                            apiKeysRef,
                            setApiKeys,
                            async (apiKey) => await rewritePromptForSafety(aliasedPrompt, settings, apiKey),
                            undefined, // use default retries
                            jobController.signal
                        );
                        
                        let unaliasedPrompt = rewrittenPrompt;
                        if (unaliasedPrompt) {
                            const sortedMap = [...characterMap].sort((a, b) => b.alias.length - a.alias.length);
                            sortedMap.forEach(mapping => {
                                const regex = new RegExp(`(${mapping.alias})(?!\\d)`, 'gi');
                                unaliasedPrompt = unaliasedPrompt!.replace(regex, mapping.originalName);
                            });
                        }
                        
                        if (unaliasedPrompt && !jobController.signal.aborted) {
                            console.log("Prompt rewritten successfully:", unaliasedPrompt);
                            updateJobStatus(jobId, { 
                                prompt: unaliasedPrompt, 
                                status: 'pending', 
                                error: undefined, 
                                retryCount: retryCount + 1
                            });
                            
                            // Don't advance the index, let the loop pick up the pending job again
                            controller.signal.removeEventListener('abort', onBatchAbort);
                            continue; 
                        } else {
                            lastErrorMsg = "Censura detectada. Falha ao reescrever o prompt de forma segura.";
                        }
                    } catch (rewriteError: any) {
                        console.error("Failed to rewrite prompt:", rewriteError);
                        lastErrorMsg = "Censura detectada. Erro na tentativa de reescrita: " + (rewriteError.message || "Erro desconhecido");
                    }
                } else {
                    lastErrorMsg = "Censura detectada, mas a operação foi cancelada antes da reescrita.";
                }
            }
        } finally {
            controller.signal.removeEventListener('abort', onBatchAbort);
            jobAbortControllerRef.current = null;
        }
        
        if (!success) {
            if (jobController.signal.aborted && !controller.signal.aborted) {
                // Individual job was skipped
                updateJobStatus(jobId, { status: 'failed', error: "Pulado pelo usuário." });
            } else if (controller.signal.aborted) {
                // Whole batch was stopped
                updateJobStatus(jobId, { status: 'pending', error: "Pausado pelo usuário." });
                break; // Ensure we break out of the loop when aborted
            } else if (pauseOnError) {
                updateJobStatus(jobId, { status: 'pending', error: `PAUSA: ${lastErrorMsg}` });
                isProcessingRef.current = false;
                setIsProcessing(false);
                abortControllerRef.current = null;
                toast.error(`⚠️ Lote PAUSADO Automaticamente.\n\nMotivo: ${lastErrorMsg}`, { duration: 5000 });
                return; 
            } else {
                updateJobStatus(jobId, { status: 'failed', error: lastErrorMsg || "Falha." });
            }
        }

        setCurrentKeyIndex(keyIdx % Math.max(1, activeKeys.length));
    }

    isProcessingRef.current = false;
    setIsProcessing(false);
    abortControllerRef.current = null;
  };

  const pendingCount = jobs.filter(j => j.status === 'pending').length;
  const hasInput = promptInput.trim().length > 0;
  const canStart = hasActiveKeys && (pendingCount > 0 || hasInput) && !isProcessing;

  // Progress Metrics
  const totalJobs = jobs.length;
  const completedJobs = jobs.filter(j => j.status === 'completed').length;
  const failedJobs = jobs.filter(j => j.status === 'failed').length;
  const processingJobs = jobs.filter(j => j.status === 'processing').length;
  const progressPercent = totalJobs > 0 ? Math.round(((completedJobs + failedJobs) / totalJobs) * 100) : 0;

  return (
    <div className="h-full flex flex-col gap-4 overflow-y-auto pr-2 pb-2">
      {/* Warning if no keys */}
      {!hasActiveKeys && (
        <div className="bg-orange-950/20 border border-orange-500/50 p-4 rounded-xl flex items-center justify-between shrink-0">
            <div className="flex items-center gap-3">
                <AlertTriangle className="text-orange-500 w-5 h-5" />
                <div>
                    <h3 className="font-bold text-orange-200">Sem Chaves API Ativas</h3>
                    <p className="text-sm text-orange-200/70">Habilite chaves nas configurações para continuar.</p>
                </div>
            </div>
            <button onClick={onNavigateToSettings} className="bg-orange-500 hover:bg-orange-600 text-white px-4 py-2 rounded-lg text-sm font-bold">Ir para Configurações</button>
        </div>
      )}

      {/* Input Section */}
      <div className="bg-slate-900 rounded-xl border border-slate-700 p-6 flex flex-col gap-4 shrink-0">
        <div className="flex flex-col gap-4">
             {/* Header Controls */}
            <div className="flex flex-col xl:flex-row justify-between items-start xl:items-center gap-4">
                <div className="flex items-center gap-4">
                    <h2 className="text-xl font-bold text-white flex items-center gap-2">
                        <Play className="w-5 h-5 text-orange-400" />
                        Automação de Tarefas
                    </h2>
                    {/* Key Health Monitor */}
                    {hasActiveKeys && (
                        <div className="flex items-center gap-2 text-[10px] font-mono bg-slate-950 px-2 py-1 rounded border border-slate-800" title="Monitor de Saúde das Chaves API">
                            <Activity className={`w-3 h-3 ${errorKeysCount > 0 ? 'text-orange-400' : 'text-green-500'}`} />
                            <span className={healthyKeysCount > 0 ? "text-green-400 font-bold" : "text-slate-500"}>{healthyKeysCount} OK</span>
                            <span className="text-slate-600">|</span>
                            <span className={errorKeysCount > 0 ? "text-orange-400 font-bold" : "text-slate-500"}>{errorKeysCount} Erros</span>
                        </div>
                    )}
                </div>
                
                <div className="flex flex-wrap gap-2 items-center">
                    {/* Pause On Error Toggle */}
                    <button 
                        onClick={() => setPauseOnError(!pauseOnError)}
                        className={`flex items-center gap-2 px-3 py-1.5 rounded-lg border transition-all ${
                            pauseOnError
                            ? 'bg-orange-900/30 border-orange-500 text-orange-300' 
                            : 'bg-slate-800 border-slate-600 text-slate-500'
                        }`}
                        title="Se ativado, o lote pausa se ocorrer um erro na API, evitando que você perca seus prompts com falhas em sequência."
                        disabled={isProcessing}
                    >
                        <ShieldAlert className="w-4 h-4" />
                        <span className="text-xs font-bold">Pausar no Erro: {pauseOnError ? 'ON' : 'OFF'}</span>
                    </button>

                    {/* Story Continuity Checkbox (Renamed from Button) */}
                    <div 
                        onClick={() => !isProcessing && onUpdateSetting('useStoryContinuity', !settings.useStoryContinuity)}
                        className={`flex items-center gap-2 px-3 py-1.5 rounded-lg border transition-all cursor-pointer select-none ${
                            settings.useStoryContinuity 
                            ? 'bg-purple-600/20 border-purple-500 text-purple-300' 
                            : 'bg-slate-800 border-slate-600 text-slate-400'
                        } ${isProcessing ? 'opacity-50 cursor-not-allowed' : 'hover:border-purple-400'}`}
                        title="Usa a imagem gerada anteriormente como referência para a próxima (Mantém estilo/cena)"
                    >
                        {settings.useStoryContinuity ? <CheckSquare className="w-4 h-4 text-purple-400" /> : <Square className="w-4 h-4" />}
                        <span className="text-xs font-bold">Usar Continuidade da História</span>
                    </div>

                    {/* Video Prompt Toggle */}
                    <button 
                        onClick={() => {
                            if (!settings.openaiKey && !settings.generateVideoPrompt) {
                                toast.error("Para reescrever prompts com o ChatGPT, insira a chave da OpenAI na aba de Configurações.");
                            }
                            onUpdateSetting('generateVideoPrompt', !settings.generateVideoPrompt);
                        }}
                        className={`flex items-center gap-2 px-3 py-1.5 rounded-lg border transition-all ${
                            settings.generateVideoPrompt 
                            ? 'bg-yellow-600/20 border-yellow-500 text-yellow-300' 
                            : 'bg-slate-800 border-slate-600 text-slate-400 opacity-80 hover:opacity-100'
                        }`}
                        title="Ativa o sistema Anti-Censura. Os prompts serão reescritos usando o ChatGPT (requer chave OpenAI nas Configurações) antes do envio se encontrados problemas."
                        disabled={isProcessing}
                    >
                        <Clapperboard className="w-4 h-4" />
                        <span className="text-xs font-bold">Anti-Censura/Vídeo: {settings.generateVideoPrompt ? 'ON' : 'OFF'}</span>
                    </button>

                    {/* Model */}
                    <div className="flex items-center gap-2 bg-slate-800 p-1.5 rounded-lg border border-slate-600">
                        <Zap className="w-4 h-4 text-orange-400 ml-2" />
                        <select 
                            value={currentModelValue}
                            onChange={handleModelChange}
                            className="bg-slate-700 text-white text-sm rounded px-2 py-1 outline-none focus:ring-1 focus:ring-purple-500 border border-slate-600 max-w-[200px] truncate"
                            disabled={isProcessing}
                        >
                            <optgroup label="Modal (Cloud GPU)">
                                <option value="flux_pulid">FLUX Dev 8-bit (PuLID - Face ID)</option>
                                <option value="flux_modal">FLUX Dev 8-bit (Redux - Estilo)</option>
                            </optgroup>
                            <optgroup label="Google Gemini">
                                {MODELS.map((m) => <option key={m.id} value={m.id}>{m.name}</option>)}
                            </optgroup>
                            <optgroup label="ComfyUI">
                                <option value="comfyui">ComfyUI (Local/API)</option>
                            </optgroup>
                        </select>
                    </div>

                    {/* Image Size */}
                    <div className="flex items-center gap-2 bg-slate-800 p-1.5 rounded-lg border border-slate-600">
                        <ImageIcon className="w-4 h-4 text-blue-400 ml-2" />
                        <select 
                            value={settings.imageSize || '1K'}
                            onChange={(e) => onUpdateSetting('imageSize', e.target.value)}
                            className="bg-slate-700 text-white text-sm rounded px-2 py-1 outline-none focus:ring-1 focus:ring-purple-500 border border-slate-600"
                            disabled={isProcessing}
                            title="Resolução da Imagem"
                        >
                            <option value="1K">1K</option>
                            <option value="2K">2K</option>
                            <option value="4K">4K</option>
                        </select>
                    </div>

                    {/* Delay */}
                    <div className="flex items-center gap-2 bg-slate-800 p-1.5 rounded-lg border border-slate-600">
                        <Clock className="w-4 h-4 text-slate-400 ml-2" />
                        <select 
                            value={settings.delayBetweenRequests}
                            onChange={(e) => onUpdateSetting('delayBetweenRequests', parseInt(e.target.value))}
                            className="bg-slate-700 text-white text-sm rounded px-2 py-1 outline-none focus:ring-1 focus:ring-purple-500 border border-slate-600"
                            disabled={isProcessing}
                        >
                            <option value={0}>Sem Delay (Risco)</option>
                            <option value={2000}>2s (Recomendado)</option>
                            <option value={5000}>5s (Seguro)</option>
                            <option value={10000}>10s (Muito Seguro)</option>
                            <option value={15000}>15s (Para Contas Gratuitas)</option>
                            <option value={30000}>30s (Extremo)</option>
                        </select>
                    </div>

                    {/* Aspect Ratio */}
                    <div className="flex items-center gap-2 bg-slate-800 p-1.5 rounded-lg border border-slate-600">
                        <Settings2 className="w-4 h-4 text-slate-400 ml-2" />
                        <select 
                            value={settings.aspectRatio}
                            onChange={(e) => onUpdateSetting('aspectRatio', e.target.value)}
                            className="bg-slate-700 text-white text-sm rounded px-2 py-1 outline-none focus:ring-1 focus:ring-purple-500 border border-slate-600"
                            disabled={isProcessing}
                        >
                            {ASPECT_RATIOS.map((ratio) => <option key={ratio.value} value={ratio.value}>{ratio.label}</option>)}
                        </select>
                    </div>
                </div>
            </div>
        </div>

        <div className="flex justify-between items-center mb-1 mt-4">
            <h3 className="text-sm font-bold text-slate-300">Prompts Brutos</h3>
            <button 
                onClick={handleRewriteCensored} 
                disabled={!hasInput || isProcessing}
                className="bg-purple-600/20 hover:bg-purple-600/40 text-purple-300 border border-purple-500/30 px-3 py-1 rounded text-xs font-bold transition-all flex items-center gap-2 disabled:opacity-50"
                title="Usa o Gemini para refinar seus prompts de texto, tornando-os seguros para o filtro de censura do Google Flow/Veo, mantendo a direção de arte e trocando personagens reais por descrições indiretas."
            >
                <Pencil className="w-3 h-3" /> Refinar & Anti-Censura (Gemini)
            </button>
        </div>
        <textarea
          value={promptInput}
          onChange={(e) => setPromptInput(e.target.value)}
          placeholder={`Insira prompts de sequência aqui (um por linha).\nExemplo:\n#Heroi desembainhando a espada\n#Heroi correndo em direção ao inimigo`}
          className="w-full h-32 bg-slate-800 border border-slate-600 rounded p-3 text-white focus:ring-2 focus:ring-purple-500 outline-none font-mono text-sm resize-none"
          disabled={isProcessing}
        />

        <div className="flex gap-3 mt-2 flex-wrap">
          <button onClick={handleLoadQueue} disabled={!hasInput || isProcessing} className="bg-slate-700 hover:bg-slate-600 text-white px-4 py-2 rounded flex-1 min-w-[140px] disabled:opacity-50 transition-colors">
            Carregar na Fila
          </button>

          <button onClick={handleExportForAutoVeo} disabled={(!hasInput && jobs.length === 0) || isProcessing} className="bg-indigo-600/50 hover:bg-indigo-600 text-white px-4 py-2 rounded flex-none flex items-center justify-center gap-2 border border-indigo-500/50 disabled:opacity-50 transition-colors" title="Baixa um ZIP com os textos e imagens de personagens prontos para a Extensão Chrome Auto VEO/FLOW">
            <Download className="w-4 h-4" /> Exportar (Extensão VEO)
          </button>
          
          {!isProcessing ? (
            <button onClick={startBatchProcessing} disabled={!canStart} className={`flex-1 px-6 py-2 rounded flex items-center justify-center gap-2 font-bold transition-all ${canStart ? 'bg-purple-600 hover:bg-purple-700 text-white shadow-lg shadow-purple-900/50' : 'bg-slate-800 text-slate-500 cursor-not-allowed'}`}>
                {pendingCount === 0 && hasInput ? <><Play className="w-4 h-4" /> Carregar & Iniciar Lote</> : <><Play className="w-4 h-4" /> Iniciar Lote ({pendingCount > 0 ? pendingCount : ''})</>}
            </button>
          ) : (
             <button onClick={stopProcessing} className="bg-red-600 hover:bg-red-700 text-white px-6 py-2 rounded flex items-center justify-center gap-2 font-bold transition-colors flex-1">
                <StopCircle className="w-4 h-4" /> Parar
            </button>
          )}
        </div>
      </div>

      {/* Progress Bar */}
      {totalJobs > 0 && (
        <div className="bg-slate-900 rounded-xl border border-slate-700 p-4 shrink-0">
            <div className="flex justify-between items-center mb-2">
                <h3 className="text-sm font-bold text-slate-300">Progresso do Lote</h3>
                <span className="text-xs font-mono text-slate-400">{completedJobs + failedJobs} / {totalJobs} ({progressPercent}%)</span>
            </div>
            
            <div className="w-full h-3 bg-slate-800 rounded-full overflow-hidden flex">
                {/* Completed */}
                <div 
                    className="bg-green-500 h-full transition-all duration-500" 
                    style={{ width: `${(completedJobs / totalJobs) * 100}%` }} 
                    title={`${completedJobs} Concluídos`}
                />
                {/* Failed */}
                <div 
                    className="bg-red-500 h-full transition-all duration-500" 
                    style={{ width: `${(failedJobs / totalJobs) * 100}%` }} 
                    title={`${failedJobs} Falhas`}
                />
                {/* Processing */}
                <div 
                    className="bg-purple-500 h-full transition-all duration-500 animate-pulse" 
                    style={{ width: `${(processingJobs / totalJobs) * 100}%` }} 
                    title={`${processingJobs} Processando`}
                />
            </div>

            <div className="flex justify-between text-[10px] text-slate-500 mt-2 font-mono">
                 <div className="flex items-center gap-1"><div className="w-2 h-2 rounded-full bg-green-500"></div> Concluído ({completedJobs})</div>
                 <div className="flex items-center gap-1"><div className="w-2 h-2 rounded-full bg-purple-500 animate-pulse"></div> Processando ({processingJobs})</div>
                 <div className="flex items-center gap-1"><div className="w-2 h-2 rounded-full bg-red-500"></div> Falha ({failedJobs})</div>
                 <div className="flex items-center gap-1"><div className="w-2 h-2 rounded-full bg-slate-700 border border-slate-600"></div> Pendente ({pendingCount})</div>
            </div>
        </div>
      )}

      {/* Queue Display */}
      <div className="flex-1 bg-slate-900 rounded-xl border border-slate-700 p-6 overflow-hidden flex flex-col min-h-[400px] shrink-0">
        <div className="flex justify-between items-end mb-4">
             <div className="flex items-center gap-2">
                 <h3 className="font-bold text-slate-300">Fila de Processamento ({jobs.length})</h3>
                 {isQueueLoaded && <span className="text-[10px] text-green-400 bg-green-900/20 border border-green-900 px-2 py-0.5 rounded flex items-center gap-1 animate-pulse"><Save className="w-3 h-3" /> Salvo Automático</span>}
             </div>
             {jobs.length > 0 && !isProcessing && <button onClick={() => { setJobs([]); jobsRef.current = []; }} className="text-xs text-red-400 hover:text-red-300">Limpar Fila</button>}
        </div>
       
        <div className="flex-1 overflow-y-auto space-y-2 pr-2" ref={jobListRef}>
            {jobs.length === 0 && (
                <div className="flex flex-col items-center justify-center h-full text-slate-500 opacity-50">
                    <ArrowRight className="w-8 h-8 mb-2" />
                    <p className="italic">A fila está vazia. Adicione prompts acima.</p>
                </div>
            )}
            {jobs.map((job, idx) => (
                <div 
                    key={job.id} 
                    className={`p-3 rounded border flex items-center justify-between gap-4 transition-colors ${
                        job.status === 'processing' ? 'bg-purple-900/20 border-purple-500/50' :
                        job.status === 'completed' ? 'bg-green-900/20 border-green-500/50' :
                        job.status === 'failed' ? 'bg-red-900/20 border-red-500/50' :
                        'bg-slate-800 border-slate-700'
                    }`}
                    draggable={!isProcessing}
                    onDragStart={(e) => handleDragStart(e, idx)}
                    onDragEnd={handleDragEnd}
                    onDragOver={(e) => handleDragOver(e, idx)}
                    onDrop={(e) => handleDrop(e, idx)}
                >
                    <div className="flex items-center gap-3 overflow-hidden flex-1 mr-2">
                        {!isProcessing && (
                            <div className="cursor-grab active:cursor-grabbing text-slate-500 hover:text-slate-300 shrink-0">
                                <GripVertical className="w-4 h-4" />
                            </div>
                        )}
                        <span className="text-slate-500 font-mono text-xs w-6 shrink-0">#{idx + 1}</span>
                        
                        {editingJobId === job.id ? (
                            <div className="flex items-center gap-2 w-full">
                                <input 
                                    value={editPromptText}
                                    onChange={(e) => setEditPromptText(e.target.value)}
                                    className="flex-1 bg-slate-950 border border-purple-500 rounded px-2 py-1 text-sm text-white outline-none"
                                    autoFocus
                                    onKeyDown={(e) => e.key === 'Enter' && saveEdit()}
                                />
                                <button onClick={saveEdit} className="text-green-400 hover:text-green-300 p-1"><CheckSquare className="w-4 h-4"/></button>
                                <button onClick={cancelEdit} className="text-red-400 hover:text-red-300 p-1"><X className="w-4 h-4"/></button>
                            </div>
                        ) : (
                            <div className="flex flex-col min-w-0">
                                <div 
                                    className={`group flex items-center gap-2 cursor-pointer`} 
                                    onClick={() => startEditing(job)}
                                    title={"Clique para editar o prompt e tentar novamente"}
                                >
                                    <span className="text-sm text-slate-200 truncate max-w-[200px] md:max-w-[400px] group-hover:text-purple-300 transition-colors">
                                        {job.prompt}
                                    </span>
                                    <Pencil className="w-3 h-3 text-slate-600 group-hover:text-purple-400 opacity-0 group-hover:opacity-100 transition-opacity" />
                                </div>
                                {job.error && !editingJobId && <div className="flex items-center gap-1 text-xs text-orange-400 mt-1"><AlertTriangle className="w-3 h-3" /> {job.error}</div>}
                            </div>
                        )}
                    </div>
                    
                    <div className="flex items-center gap-3">
                        {job.status === 'processing' && <Loader2 className="w-4 h-4 text-purple-400 animate-spin" />}
                        {job.status === 'pending' && job.error && <PauseCircle className="w-4 h-4 text-orange-400" />}
                        
                        {/* Regenerate Button for failed or completed jobs */}
                        {(job.status === 'failed' || job.status === 'completed') && !isProcessing && (
                            <button 
                                onClick={() => regenerateJob(job.id)}
                                className="p-1.5 bg-slate-800 hover:bg-purple-600 text-slate-400 hover:text-white rounded transition-colors"
                                title="Regerar Imagem (Volta para a fila)"
                            >
                                <RefreshCw className="w-3 h-3" />
                            </button>
                        )}

                        {/* Result with Download */}
                        {job.status === 'completed' && job.result && (
                            <div className="flex items-center gap-2">
                                <button 
                                    onClick={() => downloadJobImage(job)}
                                    className="p-1.5 bg-slate-700 hover:bg-slate-600 text-white rounded transition-colors"
                                    title="Baixar Imagem"
                                >
                                    <Download className="w-3 h-3" />
                                </button>
                                {job.result.imageUrl ? (
                                    <img 
                                        src={job.result.imageUrl} 
                                        alt="Result" 
                                        className="w-10 h-10 rounded object-cover border border-slate-600 cursor-pointer hover:border-purple-500 transition-colors" 
                                        onClick={() => onImageClick?.(job.result!)}
                                    />
                                ) : (
                                    <div className="w-10 h-10 rounded bg-slate-700 flex items-center justify-center border border-slate-600 text-xs text-slate-400" title="Image in Gallery">IMG</div>
                                )}
                            </div>
                        )}

                        {job.status === 'processing' && (
                            <button 
                                onClick={() => pauseJobAndBatch(job.id)}
                                className="p-1.5 bg-orange-900/30 hover:bg-orange-600 text-orange-400 hover:text-white rounded transition-colors"
                                title="Pausar este prompt e o lote"
                            >
                                <PauseCircle className="w-4 h-4" />
                            </button>
                        )}

                        <span className={`text-xs uppercase font-bold px-2 py-1 rounded ${
                             job.status === 'processing' ? 'bg-purple-500/20 text-purple-400' :
                             job.status === 'completed' ? 'bg-green-500/20 text-green-400' :
                             job.status === 'failed' ? 'bg-red-500/20 text-red-400' :
                             'bg-slate-700 text-slate-400'
                        }`}>
                            {job.status}
                        </span>

                        <button 
                            onClick={() => removeJob(job.id)}
                            className="p-1.5 text-slate-500 hover:text-red-400 hover:bg-red-900/20 rounded transition-colors"
                            title="Remover da fila"
                        >
                            <Trash2 className="w-4 h-4" />
                        </button>
                    </div>
                </div>
            ))}
        </div>
      </div>
    </div>
  );
};

export default JobRunner;
