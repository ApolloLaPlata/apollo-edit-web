export async function scrapeUrlWithApify(url: string, apifyKey: string) {
    if (!apifyKey) throw new Error("A chave da API do Apify não foi configurada.");

    // We will use the widely known 'apify/website-content-crawler' or a simple 'apify/cheerio-scraper' to extract text quickly.
    // The fast apify/website-content-crawler is perfect for RAG text extraction
    const actorId = 'apify~website-content-crawler';
    
    // Instead of run-sync-get-dataset-items which can timeout, we'll try it with a low maxCrawlPages.
    const input = {
        startUrls: [{ url }],
        maxCrawlPages: 1,
        crawlerType: "playwright:adaptive", // ensure it can render page
        htmlSnippetOutput: false,
        markdownOutput: true,
        textOutput: true,
    };

    const runResponse = await fetch(`https://api.apify.com/v2/acts/${actorId}/runs?token=${apifyKey}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(input)
    });

    if (!runResponse.ok) {
        throw new Error(`Erro ao iniciar o scraper no Apify: ${runResponse.statusText}`);
    }

    const runData = await runResponse.json();
    const runId = runData.data.id;

    // Polling for completion
    let isFinished = false;
    let datasetId = null;

    while (!isFinished) {
        await new Promise(r => setTimeout(r, 2000)); // wait 2s
        const statusResponse = await fetch(`https://api.apify.com/v2/actor-runs/${runId}?token=${apifyKey}`);
        if (!statusResponse.ok) continue;
        const statusData = await statusResponse.json();
        
        const status = statusData.data.status;
        if (status === 'SUCCEEDED') {
            isFinished = true;
            datasetId = statusData.data.defaultDatasetId;
        } else if (status === 'FAILED' || status === 'ABORTED' || status === 'TIMED-OUT') {
            throw new Error(`A extração pelo Apify falhou (Status: ${status}).`);
        }
    }

    // Get the dataset
    const datasetResponse = await fetch(`https://api.apify.com/v2/datasets/${datasetId}/items?token=${apifyKey}`);
    if (!datasetResponse.ok) {
        throw new Error("Erro ao buscar o conteúdo extraído.");
    }

    const items = await datasetResponse.json();
    if (!items || items.length === 0) {
        throw new Error("O Apify não encontrou nenhum conteúdo textual nesta URL.");
    }

    // Attempt to return markdown first, else text
    return items[0].markdown || items[0].text || JSON.stringify(items[0]);
}
