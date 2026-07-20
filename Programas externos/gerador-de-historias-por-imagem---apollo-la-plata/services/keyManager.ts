import { ApiKey } from '../types';

class KeyManager {
  private static instance: KeyManager;
  private currentIndex: number = 0;

  private constructor() {}

  public static getInstance(): KeyManager {
    if (!KeyManager.instance) {
      KeyManager.instance = new KeyManager();
    }
    return KeyManager.instance;
  }

  /**
   * Returns the next active API key using a Round-Robin strategy.
   * This ensures even distribution of requests across all available keys.
   */
  public getNextKey(apiKeys: ApiKey[]): string | null {
    const activeKeys = apiKeys.filter(k => k.isActive);
    
    if (activeKeys.length === 0) return null;

    // If index is out of bounds (e.g. keys removed), reset
    if (this.currentIndex >= activeKeys.length) {
      this.currentIndex = 0;
    }

    const selectedKey = activeKeys[this.currentIndex];
    
    // Move to next index for the next call
    this.currentIndex = (this.currentIndex + 1) % activeKeys.length;

    return selectedKey.key;
  }

  /**
   * Resets the rotation index.
   */
  public resetRotation() {
    this.currentIndex = 0;
  }
}

export const keyManager = KeyManager.getInstance();
