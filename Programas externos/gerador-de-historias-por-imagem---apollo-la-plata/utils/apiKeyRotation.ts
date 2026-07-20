import { ApiKey } from '../types';

/**
 * Intelligent API Key Rotation
 * 
 * Strategy:
 * 1. Filter for active and non-rate-limited keys.
 * 2. Sort by usage percentage (used / limit).
 * 3. Return the key with the lowest usage percentage.
 * 4. If all keys are rate-limited, return null (or handle gracefully).
 */

export const getNextKey = (apiKeys: ApiKey[]): string | null => {
    const bestKey = getBestKey(apiKeys);
    return bestKey ? bestKey.key : null;
};

export const getBestKey = (apiKeys: ApiKey[]): ApiKey | null => {
    const now = Date.now();
    
    // Filter available keys
    const availableKeys = apiKeys.filter(k => {
        if (!k.isActive) return false;
        
        // Check if rate limited (blocked temporarily)
        if (k.isRateLimited) {
            // Check if cooldown passed (e.g. 1 minute or custom)
            if (k.rateLimitedUntil && now > k.rateLimitedUntil) {
                return true; // It's ready to try again (will be unblocked by checkDailyReset or similar logic)
            }
            return false;
        }
        
        // Check hard limit (if usageLimit is set and > 0)
        if (k.usageLimit > 0 && k.usageCount >= k.usageLimit) return false;
        
        return true;
    });

    if (availableKeys.length === 0) {
        // Fallback: If all are blocked, try to find one that is just rate limited but cooldown expired
        // (This is a safety net if checkDailyReset hasn't run yet)
        const expiredCooldown = apiKeys.find(k => k.isActive && k.isRateLimited && k.rateLimitedUntil && now > k.rateLimitedUntil);
        if (expiredCooldown) return expiredCooldown;
        
        const hasRateLimitedKeys = apiKeys.some(k => k.isActive && k.isRateLimited);
        if (hasRateLimitedKeys) {
             throw new Error("Todas as chaves da API estão no limite de uso (Rate Limit). Aguarde 1 minuto ou adicione mais chaves nas Configurações.");
        }
        
        return null;
    }

    // Sort by usage percentage (ascending)
    // We create a copy to avoid mutating the original array in place during sort
    const sortedKeys = [...availableKeys].sort((a, b) => {
        const limitA = a.usageLimit || 100;
        const limitB = b.usageLimit || 100;
        const usageA = (a.usageCount || 0) / limitA;
        const usageB = (b.usageCount || 0) / limitB;
        return usageA - usageB;
    });

    return sortedKeys[0];
};

// Helper to update usage state - Returns NEW state
export const registerKeyUsage = (keyString: string, apiKeys: ApiKey[]): ApiKey[] => {
    return apiKeys.map(k => {
        if (k.key === keyString) {
            const newUsage = (k.usageCount || 0) + 1;
            return {
                ...k,
                usageCount: newUsage,
                isRateLimited: false, // Clear rate limit on success
                rateLimitedUntil: undefined,
                errorCount: 0 // Reset error count on success
            };
        }
        return k;
    });
};

// Helper to handle failure (Rate Limit) - Returns NEW state
export const registerKeyFailure = (keyString: string, apiKeys: ApiKey[], errorMessage?: string): ApiKey[] => {
    return apiKeys.map(k => {
        if (k.key === keyString) {
            // Determine cooldown based on error type
            let cooldownMs = 2 * 60 * 1000; // 2 minutos padrão para limites de velocidade (RPM)
            
            const errStr = (errorMessage || "").toLowerCase();
            
            // Como o Gemini retorna "billing details" tanto para limite diário quanto para limite por minuto (RPM),
            // NÃO podemos bloquear a chave por 12 horas, senão inutilizamos contas gratuitas legítimas.
            // Vamos usar 2 minutos de cooldown. Se for limite diário, ela vai falhar de novo e voltar pra geladeira.
            // Se for limite por minuto, 2 minutos é tempo suficiente para a cota resetar.
            if (errStr.includes('per day') && !errStr.includes('billing details')) {
                // Apenas se disser explicitamente "per day" sem a mensagem genérica
                cooldownMs = 12 * 60 * 60 * 1000; 
            }

            return {
                ...k,
                isRateLimited: true,
                rateLimitedUntil: Date.now() + cooldownMs,
                errorCount: (k.errorCount || 0) + 1
            };
        }
        return k;
    });
};

// Helper to check for daily reset - Returns NEW state
export const checkDailyReset = (apiKeys: ApiKey[]): ApiKey[] => {
    const now = Date.now();
    const oneDay = 24 * 60 * 60 * 1000;
    let changed = false;

    const newKeys = apiKeys.map(k => {
        // Initialize if missing
        const lastReset = k.lastReset || 0;
        
        // Daily Reset
        if (now - lastReset > oneDay) {
            changed = true;
            return {
                ...k,
                usageCount: 0,
                lastReset: now,
                isRateLimited: false,
                rateLimitedUntil: 0,
                errorCount: 0
            };
        }
        
        // Cooldown Expiry Check
        if (k.isRateLimited && k.rateLimitedUntil && now > k.rateLimitedUntil) {
            changed = true;
            return {
                ...k,
                isRateLimited: false,
                rateLimitedUntil: 0
            };
        }

        return k;
    });

    return changed ? newKeys : apiKeys;
};

/**
 * Executes an async function with automatic key rotation.
 * If the function throws a 429 or quota error, it registers the failure,
 * gets the next best key, and retries up to maxRetries.
 */
export const executeWithKeyRotation = async <T>(
    apiKeysRef: React.MutableRefObject<ApiKey[]>,
    setApiKeys: React.Dispatch<React.SetStateAction<ApiKey[]>>,
    action: (apiKey: string) => Promise<T>,
    maxRetries?: number,
    signal?: AbortSignal
): Promise<T> => {
    const retries = maxRetries !== undefined ? maxRetries : Math.max(3, apiKeysRef.current.length);
    
    let attempts = 0;
    let lastError: any = null;

    while (attempts < retries) {
        if (signal?.aborted) {
            throw new Error("AbortError: Operação cancelada pelo usuário.");
        }

        const currentKeys = apiKeysRef.current;
        const bestKey = getBestKey(currentKeys);

        if (!bestKey) {
            throw new Error("Nenhuma chave API Gemini ativa ou disponível.");
        }

        const apiKey = bestKey.key;

        try {
            const actionPromise = action(apiKey);
            actionPromise.catch(() => {}); // Prevent unhandled rejection if aborted
            
            const result = await Promise.race([
                actionPromise,
                new Promise<never>((_, reject) => {
                    if (signal?.aborted) reject(new Error("AbortError: Operação cancelada pelo usuário."));
                    signal?.addEventListener('abort', () => reject(new Error("AbortError: Operação cancelada pelo usuário.")), { once: true });
                })
            ]);
            
            if (signal?.aborted) {
                throw new Error("AbortError: Operação cancelada pelo usuário.");
            }

            // Success: Register usage
            setApiKeys(prev => registerKeyUsage(apiKey, prev));
            apiKeysRef.current = registerKeyUsage(apiKey, apiKeysRef.current);
            
            return result;
        } catch (error: any) {
            if (signal?.aborted) {
                throw new Error("AbortError: Operação cancelada pelo usuário.");
            }

            lastError = error;
            const errorMessage = error.message || String(error);
            const isSafetyBlock = errorMessage.includes('safety') || errorMessage.includes('blocked') || errorMessage.includes('policy');
            const isTextProviderError = errorMessage.includes('TextProviderError:');

            if (isTextProviderError) {
                console.error(`Text Provider Error: ${errorMessage}`);
                throw error; // Don't rotate Gemini keys if the error is from another provider
            }

            if (!isSafetyBlock) {
                console.warn(`Key ${apiKey.substring(0, 8)}... failed (${errorMessage}). Rotating...`);
                // Register failure
                setApiKeys(prev => registerKeyFailure(apiKey, prev, errorMessage));
                apiKeysRef.current = registerKeyFailure(apiKey, apiKeysRef.current, errorMessage);
                
                attempts++;
                if (attempts < retries) {
                    // Wait a bit before retrying, but listen to abort
                    await new Promise<void>((resolve, reject) => {
                        const timeout = setTimeout(resolve, 2000);
                        if (signal) {
                            signal.addEventListener('abort', () => {
                                clearTimeout(timeout);
                                reject(new Error("AbortError: Operação cancelada pelo usuário."));
                            }, { once: true });
                        }
                    });
                    continue;
                }
            } else {
                // Safety block, throw immediately
                throw error;
            }
        }
    }

    if (attempts >= retries) {
        throw new Error(`Todas as ${retries} tentativas de rotação falharam. Último erro: ${lastError?.message || lastError}`);
    }

    throw lastError;
};
