const url = "https://cloud.comfy.org/api/user";

fetch(url).then(res => {
  console.log(res.status, res.statusText);
  return res.text();
}).then(text => console.log(text)).catch(console.error);
