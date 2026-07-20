
export interface ComfyWorkflow {
  id: string;
  name: string;
  type: 'image' | 'video';
  category?: string; // Classification/Tag
  json: string;
}

export interface StylePreset {
  id: string;
  name: string;
  globalContext: string;
  sceneContext: string;
  negativePrompt: string;
  styleReferenceImage?: string;
}

export interface BrandKit {
  colors: string[]; // Hex codes
  logoUrl?: string; // Base64 image
  fontFamily?: string;
}

export interface KnowledgeDocument {
  id: string;
  name: string;
  content: string;
}

export interface Project {
  id: string;
  name: string;
  globalContext?: string; // Visual Style / Art Direction specific to this channel
  sceneContext?: string; // Scene context specific to this channel
  negativePrompt?: string; // Elements to exclude specific to this channel
  styleReferenceImage?: string; // Style reference image specific to this channel
  presets?: StylePreset[]; // Presets exclusive to this channel
  activePresetId?: string; // Currently active preset
  aspectRatio?: '1:1' | '16:9' | '9:16' | '4:3' | '3:4' | '1:4' | '1:8' | '4:1' | '8:1';
  modelId?: string; // AI Model specific to this channel
  imageSize?: '1K' | '2K' | '4K'; // Resolution specific to this channel
  color?: string; // Channel color (e.g., tailwind color class or hex)
  icon?: string; // Channel icon name
  defaultImageWorkflowId?: string; // Default ComfyUI image workflow for this channel
  defaultVideoWorkflowId?: string; // Default ComfyUI video workflow for this channel
  brandKit?: BrandKit; // Brand Kit specific to this channel
  knowledgeBase?: KnowledgeDocument[]; // Text documents for RAG/Context
}

export interface Character {
  id: string;
  name: string; // The tag, e.g., "#Hero"
  description?: string; // Explicit description of the character's features
  category?: string; // Category/Group (e.g., "Heróis", "Políticos", "História X")
  images: string[]; // Array of Base64 strings (Multiple angles/poses)
  previewUrl: string; // The main thumbnail
  projectId?: string; // To separate characters by channel/project
}

export interface ApiKey {
  key: string;
  label?: string;
  isActive: boolean;
  errorCount: number;
  // Intelligent Rotation Fields
  usageCount: number;
  usageLimit: number; // Daily limit (e.g., 100 for free tier)
  lastReset: number; // Timestamp of last daily reset
  isRateLimited: boolean; // Temporarily blocked due to 429
  rateLimitedUntil?: number; // Timestamp when it can be used again
}

export interface GenerationSettings {
  aspectRatio: '1:1' | '16:9' | '9:16' | '4:3' | '3:4' | '1:4' | '1:8' | '4:1' | '8:1';
  modelId: string;
  imageSize?: '1K' | '2K' | '4K'; // New: Resolution control for supported models
  useThinking: boolean;
  delayBetweenRequests: number; // in milliseconds
  temperature?: number;
  maxOutputTokens?: number;
  topP?: number;
  useStoryContinuity: boolean; // Uses previous image as context
  globalContext: string; // Visual Style / Art Direction
  sceneContext: string; // New: Narrative environment for the specific batch
  generateVideoPrompt: boolean; // New: Generates a text prompt specifically for I2V tools
  negativePrompt?: string; // New: Elements to exclude
  useGrounding?: boolean; // New: Use Google Search for grounding
  styleReferenceImage?: string; // New: Global style reference image
  brandKit?: BrandKit; // New: Brand Kit for social generation
  knowledgeBase?: KnowledgeDocument[]; // New: RAG context documents
  
  // Model Providers
  textProvider?: 'gemini' | 'openrouter' | 'openai' | 'xai';
  imageProvider?: 'gemini' | 'openrouter' | 'comfyui' | 'flux_modal' | 'flux_pulid' | 'apollo-cloud-multipass';
  videoProvider?: 'gemini' | 'comfyui';
  
  // OpenRouter Specifics
  openRouterKey?: string; 
  openRouterTextModel?: string;

  // New Provider Keys (Future Use)
  xaiKey?: string; // Grok
  xaiModel?: string;
  openaiKey?: string; // ChatGPT
  openaiModel?: string;

  // ComfyUI Integration
  comfyUrl?: string;
  comfyApiKey?: string; // New: Bearer token for ComfyUI Cloud or authenticated servers
  comfyImageWorkflow?: string; // Legacy: JSON string of the API workflow
  comfyVideoWorkflow?: string; // Legacy: JSON string of the API workflow
  comfyWorkflows?: ComfyWorkflow[]; // New: Array of saved workflows

  // Apify Integration
  apifyApiKey?: string;
}

export interface OpenRouterModel {
    id: string;
    name: string;
    contextLength?: number;
    isFree?: boolean;
}

export interface GeneratedImage {
  id: string;
  prompt: string;
  imageUrl: string;
  timestamp: number;
  characterIds: string[];
  aspectRatio: string;
  videoPrompt?: string; // New: Stores the AI-generated motion prompt
  videoUrl?: string; // Base64 string of the generated video
  projectId?: string; // To separate gallery by channel/project
}

export interface JobItem {
  id: string;
  prompt: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  result?: GeneratedImage;
  error?: string;
  retryCount?: number;
  originalCharacterMap?: { alias: string, originalName: string }[];
}

