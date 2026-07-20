async function fetchDocs() {
  const res = await fetch('https://docs.comfy.org/');
  const text = await res.text();
  const links = text.match(/href="([^"]*)"/g);
  console.log(links?.join('\n'));
}
fetchDocs();
