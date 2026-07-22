const fetch = require('node-fetch');

async function test() {
  try {
    const res = await fetch('http://localhost:3000/api/grok/models', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ apiKey: 'xai-dummy-key' })
    });
    console.log(res.status);
    const data = await res.json();
    console.log(data);
  } catch (e) {
    console.error(e);
  }
}

test();
