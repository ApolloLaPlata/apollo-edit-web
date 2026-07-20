import express from "express";
import { createServer as createViteServer } from "vite";
import cors from "cors";
import path from "path";

async function startServer() {
  const app = express();
  const PORT = 5000;

  app.use(cors());
  app.use(express.json({ limit: '50mb' }));

  // API proxy route
  app.post("/api/proxy", async (req, res) => {
    try {
      const { url, method, headers, body } = req.body;
      
      if (!url) {
        return res.status(400).json({ error: "URL is required" });
      }

      const fetchOptions: RequestInit = {
        method: method || "GET",
        headers: {
          ...headers,
          "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        },
      };

      if (body && (method === "POST" || method === "PUT")) {
        fetchOptions.body = typeof body === 'string' ? body : JSON.stringify(body);
      }

      const response = await fetch(url, fetchOptions);
      
      const contentType = response.headers.get("content-type");
      if (contentType) {
        res.setHeader("Content-Type", contentType);
      }
      res.status(response.status);

      if (contentType && (contentType.includes("image/") || contentType.includes("video/") || contentType.includes("audio/") || contentType.includes("application/octet-stream"))) {
        const arrayBuffer = await response.arrayBuffer();
        return res.send(Buffer.from(arrayBuffer));
      } else if (contentType && contentType.includes("application/json")) {
        const data = await response.json();
        return res.json(data);
      } else {
        const text = await response.text();
        return res.send(text);
      }
    } catch (error: any) {
      console.error("Proxy error:", error);
      return res.status(500).json({ error: error.message || "Internal server error" });
    }
  });

  // API proxy route for file uploads
  app.post("/api/proxy/upload", async (req, res) => {
    try {
      const { url, headers, filename, base64Data } = req.body;
      
      if (!url || !filename || !base64Data) {
        return res.status(400).json({ error: "URL, filename, and base64Data are required" });
      }

      // Convert base64 back to buffer
      const buffer = Buffer.from(base64Data, 'base64');
      const blob = new Blob([buffer], { type: 'image/png' });

      const formData = new FormData();
      formData.append('image', blob, filename);
      formData.append('overwrite', 'true');
      formData.append('type', 'input');

      const response = await fetch(url, {
        method: 'POST',
        headers: {
          ...headers,
          "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        },
        body: formData,
      });
      
      const data = await response.json();
      return res.status(response.status).json(data);
    } catch (error: any) {
      console.error("Proxy upload error:", error);
      return res.status(500).json({ error: error.message || "Internal server error" });
    }
  });

  // Vite middleware for development
  if (process.env.NODE_ENV !== "production") {
    const vite = await createViteServer({
      server: { middlewareMode: true },
      appType: "spa",
    });
    app.use(vite.middlewares);
  } else {
    const distPath = path.join(process.cwd(), 'dist');
    app.use(express.static(distPath));
    app.get('*all', (req, res) => {
      res.sendFile(path.join(distPath, 'index.html'));
    });
  }

  app.listen(PORT, "0.0.0.0", () => {
    console.log(`Server running on http://localhost:${PORT}`);
  });
}

startServer();
