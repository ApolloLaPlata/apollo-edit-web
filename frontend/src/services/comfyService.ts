export interface ComfyPromptResponse {
  prompt_id: string;
  number: number;
  node_errors: any;
}

export interface ComfyHistoryResponse {
  [prompt_id: string]: {
    prompt: any;
    outputs: {
      [node_id: string]: {
        images?: Array<{
          filename: string;
          subfolder: string;
          type: string;
        }>;
        gifs?: Array<{
          filename: string;
          subfolder: string;
          type: string;
        }>;
      };
    };
    status: {
      status_str: string;
      completed: boolean;
      messages: any[];
    };
  };
}

/**
 * Helper to normalize the ComfyUI URL (removes trailing slashes)
 */
const getBaseUrl = (url: string) => {
  return url.trim().replace(/\/+$/, '');
};

const isCloudComfy = (url: string) => {
  try {
    const parsed = new URL(getBaseUrl(url));
    return parsed.hostname === 'cloud.comfy.org';
  } catch {
    return false;
  }
};

const getEndpoint = (comfyUrl: string, path: string) => {
  const base = getBaseUrl(comfyUrl);
  if (isCloudComfy(comfyUrl)) {
    if (path === '/system_stats') return `${base}/api/user`;
    if (path.startsWith('/history/')) return `${base}/api/history_v2/${path.split('/')[2]}`;
    return `${base}/api${path}`;
  }
  return `${base}${path}`;
};

const getHeaders = (apiKey?: string, isJson = false) => {
  const headers: Record<string, string> = {};
  if (isJson) {
    headers['Content-Type'] = 'application/json';
  }
  if (apiKey && !apiKey.startsWith('comfyui-')) {
    // ComfyUI Cloud uses Bearer token
    headers['Authorization'] = `Bearer ${apiKey}`;
  }
  return headers;
};

/**
 * Determines if we should use the backend proxy.
 * We should NOT use the proxy for local/private IP addresses because the backend container cannot access the user's local network.
 */
const shouldUseProxy = (url: string) => {
  try {
    const parsed = new URL(url);
    const hostname = parsed.hostname;
    if (
      hostname === 'localhost' || 
      hostname === '127.0.0.1' || 
      hostname.startsWith('192.168.') || 
      hostname.startsWith('10.') || 
      hostname.match(/^172\.(1[6-9]|2[0-9]|3[0-1])\./)
    ) {
      return false;
    }
    return true;
  } catch {
    return false;
  }
};

/**
 * Helper to make requests through the backend proxy to avoid CORS issues
 */
const proxyFetch = async (url: string, options: RequestInit = {}) => {
  if (!shouldUseProxy(url)) {
    return fetch(url, options);
  }

  const proxyUrl = '/api/proxy';
  const proxyBody = {
    url,
    method: options.method || 'GET',
    headers: options.headers || {},
    body: options.body ? (typeof options.body === 'string' ? JSON.parse(options.body) : options.body) : undefined
  };

  const response = await fetch(proxyUrl, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(proxyBody)
  });
  
  // If the proxy itself failed, throw
  if (!response.ok && response.status === 500) {
      throw new Error(`Proxy error: ${response.statusText}`);
  }
  
  return response;
};

/**
 * Checks if the ComfyUI server is reachable.
 */
export const checkComfyConnection = async (comfyUrl: string, comfyApiKey?: string): Promise<boolean> => {
  try {
    const response = await proxyFetch(getEndpoint(comfyUrl, '/system_stats'), {
      method: 'GET',
      headers: getHeaders(comfyApiKey),
    });
    if (!response.ok) {
        let errorText = response.statusText;
        try {
            const errorBody = await response.text();
            if (errorBody) errorText += ` - ${errorBody}`;
        } catch {
            // ignore
        }
        throw new Error(`HTTP Error ${response.status}: ${errorText}`);
    }
    return true;
  } catch (error) {
    console.error("ComfyUI Connection Error:", error);
    throw error;
  }
};

/**
 * Submits a workflow to ComfyUI.
 * The workflow must be the JSON object exported from ComfyUI (Save (API Format)).
 */
export const queuePrompt = async (comfyUrl: string, workflow: any, comfyApiKey?: string): Promise<string> => {
  const payload: any = { prompt: workflow };
  
  if (comfyApiKey && comfyApiKey.startsWith('comfyui-')) {
    payload.extra_data = {
      api_key_comfy_org: comfyApiKey
    };
  }

  const response = await proxyFetch(getEndpoint(comfyUrl, '/prompt'), {
    method: 'POST',
    headers: getHeaders(comfyApiKey, true),
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    let errorText = response.statusText || 'Unknown Error';
    try {
      const errorBody = await response.text();
      if (errorBody) {
        errorText += ` - ${errorBody}`;
      }
    } catch {
      // Ignore
    }
    throw new Error(`Failed to queue prompt: ${errorText}`);
  }

  const data: ComfyPromptResponse = await response.json();
  
  if (data.node_errors && Object.keys(data.node_errors).length > 0) {
    console.warn("ComfyUI Node Errors:", data.node_errors);
    // Depending on severity, we might want to throw here.
  }

  return data.prompt_id;
};

/**
 * Polls the history endpoint until the prompt is completed.
 */
export const waitForPromptCompletion = async (
  comfyUrl: string, 
  promptId: string, 
  comfyApiKey?: string,
  pollIntervalMs = 2000,
  maxWaitMs = 300000 // 5 minutes max wait
): Promise<ComfyHistoryResponse> => {
  const startTime = Date.now();

  while (Date.now() - startTime < maxWaitMs) {
    try {
      const response = await proxyFetch(getEndpoint(comfyUrl, `/history/${promptId}`), {
        headers: getHeaders(comfyApiKey),
      });
      if (response.ok) {
        const history: any = await response.json();
        // If the prompt_id is in the history, it means it's done processing
        // For standard ComfyUI, history is { [promptId]: { outputs: ... } }
        // For ComfyUI Cloud (history_v2), it might be a list or direct object.
        // Let's handle both.
        if (history[promptId]) {
          return history;
        } else if (history.outputs || (history.messages && history.status_str === 'success')) {
            // It's likely the direct object from history_v2
            return { [promptId]: history } as unknown as ComfyHistoryResponse;
        } else if (Array.isArray(history)) {
            const item = history.find(h => h.prompt_id === promptId);
            if (item && item.outputs) {
                return { [promptId]: item } as unknown as ComfyHistoryResponse;
            }
        }
      }
    } catch (error) {
      console.warn("Error polling ComfyUI history:", error);
    }

    // Wait before polling again
    await new Promise(resolve => setTimeout(resolve, pollIntervalMs));
  }

  throw new Error("Timeout waiting for ComfyUI prompt to complete.");
};

/**
 * Fetches the generated image/video as a base64 string.
 */
export const fetchMediaAsBase64 = async (
  comfyUrl: string, 
  filename: string, 
  subfolder: string, 
  type: string,
  comfyApiKey?: string
): Promise<string> => {
  const params = new URLSearchParams({
    filename,
    subfolder,
    type
  });
  
  const response = await proxyFetch(getEndpoint(comfyUrl, `/view?${params.toString()}`), {
    headers: getHeaders(comfyApiKey),
  });
  
  if (!response.ok) {
    let errorText = response.statusText || 'Unknown Error';
    try {
      const errorBody = await response.text();
      if (errorBody) {
        errorText += ` - ${errorBody}`;
      }
    } catch {
      // Ignore
    }
    throw new Error(`Failed to fetch media: ${errorText}`);
  }

  const blob = await response.blob();
  
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onloadend = () => {
      if (typeof reader.result === 'string') {
        resolve(reader.result);
      } else {
        reject(new Error("Failed to convert blob to base64"));
      }
    };
    reader.onerror = reject;
    reader.readAsDataURL(blob);
  });
};

/**
 * Uploads a base64 image to ComfyUI's input folder.
 * Returns the filename of the uploaded image.
 */
export const uploadImageToComfyUI = async (comfyUrl: string, base64Image: string, comfyApiKey?: string): Promise<string> => {
  const base64Data = base64Image.split(',')[1];
  const filename = `upload_${Date.now()}.png`;
  const url = getEndpoint(comfyUrl, '/upload/image');

  let response;

  if (!shouldUseProxy(url)) {
    // Convert base64 to Blob for direct upload
    const byteString = atob(base64Data);
    const mimeString = base64Image.split(',')[0].split(':')[1].split(';')[0];
    const ab = new ArrayBuffer(byteString.length);
    const ia = new Uint8Array(ab);
    for (let i = 0; i < byteString.length; i++) {
      ia[i] = byteString.charCodeAt(i);
    }
    const blob = new Blob([ab], { type: mimeString });

    const formData = new FormData();
    formData.append('image', blob, filename);
    formData.append('overwrite', 'true');
    formData.append('type', 'input');

    response = await fetch(url, {
      method: 'POST',
      headers: getHeaders(comfyApiKey),
      body: formData,
    });
  } else {
    // Use proxy
    response = await fetch('/api/proxy/upload', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        url,
        headers: getHeaders(comfyApiKey),
        filename,
        base64Data
      })
    });
  }

  if (!response.ok) {
    let errorText = response.statusText || 'Unknown Error';
    try {
      const errorBody = await response.text();
      if (errorBody) {
        errorText += ` - ${errorBody}`;
      }
    } catch {
      // Ignore
    }
    throw new Error(`Failed to upload image to ComfyUI: ${errorText}`);
  }

  const data = await response.json();
  return data.name; // Returns the filename saved on the server
};

/**
 * Utility to inject an image filename into a ComfyUI workflow.
 * Looks for a node with class_type "LoadImage" and updates its image property.
 */
export const injectImageIntoWorkflow = (workflow: any, filename: string): any => {
  const newWorkflow = JSON.parse(JSON.stringify(workflow)); // Deep copy

  let foundLoadImage = false;

  for (const nodeId in newWorkflow) {
    const node = newWorkflow[nodeId];
    if (node.class_type === "LoadImage") {
      if (node.inputs) {
        node.inputs.image = filename;
        foundLoadImage = true;
      }
    }
  }

  if (!foundLoadImage) {
    console.warn("Could not find a LoadImage node in the workflow to inject the image.");
  }

  return newWorkflow;
}

/**
 * Utility to inject a text prompt into a ComfyUI workflow.
 * This is a basic implementation. It looks for a node with class_type "CLIPTextEncode"
 * and updates its text. For more complex workflows, users might need specific node IDs.
 */
export const injectPromptIntoWorkflow = (workflow: any, positivePrompt: string, negativePrompt?: string) => {
  const newWorkflow = JSON.parse(JSON.stringify(workflow)); // Deep copy
  
  // Simple heuristic: find the first CLIPTextEncode for positive, second for negative
  // Or better, look for specific node titles if the user set them.
  // For now, we'll just try to find nodes that look like text prompts.
  
  let positiveNodeFound = false;

  for (const nodeId in newWorkflow) {
    const node = newWorkflow[nodeId];
    
    // Look for standard CLIPTextEncode
    if (node.class_type === "CLIPTextEncode" || node.class_type === "CLIPTextEncodeSDXL") {
      // If it has a title "Positive", use it
      if (node._meta?.title?.toLowerCase().includes("positive")) {
        node.inputs.text = positivePrompt;
        positiveNodeFound = true;
      } else if (node._meta?.title?.toLowerCase().includes("negative")) {
        if (negativePrompt) node.inputs.text = negativePrompt;
      }
    }
  }

  // Fallback if no titles were found: just use the first one for positive, second for negative
  if (!positiveNodeFound) {
    const textNodes = Object.keys(newWorkflow).filter(id => {
      const node = newWorkflow[id];
      return node.inputs && typeof node.inputs.text === 'string';
    });
    
    if (textNodes.length > 0) {
      newWorkflow[textNodes[0]].inputs.text = positivePrompt;
      if (textNodes.length > 1 && negativePrompt) {
        newWorkflow[textNodes[1]].inputs.text = negativePrompt;
      }
    } else {
        console.warn("Could not find any node with a 'text' input to inject the prompt.");
    }
  }

  return newWorkflow;
};

/**
 * Utility to randomize seeds in a ComfyUI workflow to ensure varied generations.
 * Looks for common seed input names ('seed', 'noise_seed') and replaces them with a random number.
 */
export const randomizeSeedInWorkflow = (workflow: any): any => {
  const newWorkflow = JSON.parse(JSON.stringify(workflow));
  // Generate a large random integer for the seed
  const randomSeed = Math.floor(Math.random() * Number.MAX_SAFE_INTEGER);

  for (const nodeId in newWorkflow) {
    const node = newWorkflow[nodeId];
    if (node.inputs) {
      if (node.inputs.seed !== undefined && typeof node.inputs.seed === 'number') {
        node.inputs.seed = randomSeed;
      }
      if (node.inputs.noise_seed !== undefined && typeof node.inputs.noise_seed === 'number') {
        node.inputs.noise_seed = randomSeed;
      }
    }
  }

  return newWorkflow;
};

/**
 * Runs the Multi-Pass Generation directly on Modal backend through our local proxy
 */
export const runModalMultiPass = async (script: any): Promise<any> => {
  const url = '/api/studio/modal/multi_pass';
  
  const response = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ script })
  });

  if (!response.ok) {
    let errorText = response.statusText || 'Unknown Error';
    try {
      const errorBody = await response.text();
      if (errorBody) {
        errorText += ` - ${errorBody}`;
      }
    } catch {
      // Ignore
    }
    throw new Error(`Failed to run Multi-Pass on Modal: ${errorText}`);
  }

  return await response.json();
};
