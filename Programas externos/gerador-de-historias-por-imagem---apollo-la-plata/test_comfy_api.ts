const apiKey = "comfyui-0cbda5826747a9428fdd7d5db2964a6543bb51c09045fe9fb4bd426797c13fb9";

async function test() {
  console.log("Testing /api/prompt...");
  const res = await fetch("https://cloud.comfy.org/api/prompt", {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${apiKey}`,
      "Content-Type": "application/json",
      "User-Agent": "Mozilla/5.0"
    },
    body: JSON.stringify({ prompt: {} })
  });
  console.log("Bearer /api/prompt status:", res.status, res.statusText);
  console.log(await res.text());
}

test();
