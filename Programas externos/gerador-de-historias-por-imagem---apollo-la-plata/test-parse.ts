const parseGeminiError = (error: any) => {
    let errorMessage = error.message ? error.message : "Unknown error during generation";
    try {
        // Try to extract JSON if it's embedded in a string like "[429 Resource Exhausted] {...}"
        const jsonMatch = errorMessage.match(/\{.*\}/s);
        if (jsonMatch) {
            const parsed = JSON.parse(jsonMatch[0]);
            if (parsed.error && parsed.error.message) {
                errorMessage = parsed.error.message;
            }
        } else {
            const parsed = JSON.parse(errorMessage);
            if (parsed.error && parsed.error.message) {
                errorMessage = parsed.error.message;
            }
        }
    } catch {
        // Not JSON, ignore
    }
    return errorMessage;
};

const err = new Error('[429 Resource Exhausted] {"error":{"code":429,"message":"You exceeded your current quota","status":"RESOURCE_EXHAUSTED"}}');
console.log(parseGeminiError(err));
