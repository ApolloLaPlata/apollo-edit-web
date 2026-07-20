// This is a browser utility file test. Not for Node.
export const extractLastFrame = async (videoUrlOrBase64: string): Promise<string> => {
    return new Promise((resolve, reject) => {
      const video = document.createElement('video');
      video.crossOrigin = 'anonymous'; // Important for CORS if using URLs
      video.src = videoUrlOrBase64;
      video.muted = true;
      video.playsInline = true;
      
      video.onloadeddata = () => {
          if (!isFinite(video.duration) || video.duration === 0) {
              // Sometimes duration is not populated immediately
              // Wait for metadata
              return;
          }
           video.currentTime = Math.max(0, video.duration - 0.1); 
      }

      video.onloadedmetadata = () => {
        // Seek to the end (or slightly before the end to ensure frame is available)
        if (isFinite(video.duration) && video.duration > 0) {
            video.currentTime = Math.max(0, video.duration - 0.1); 
        }
      };
      
      video.ondurationchange = () => {
          if (isFinite(video.duration) && video.duration > 0) {
            video.currentTime = Math.max(0, video.duration - 0.1); 
          }
      }
  
      video.onseeked = () => {
        const canvas = document.createElement('canvas');
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        const ctx = canvas.getContext('2d');
        ctx?.drawImage(video, 0, 0, canvas.width, canvas.height);
        const dataUrl = canvas.toDataURL('image/png'); // Output Base64 image
        resolve(dataUrl);
      };
  
      video.onerror = (e) => {
          // If it's a GIF or unsupported format, just return the original if it's a data url image, else throw
          if (videoUrlOrBase64.startsWith('data:image/')) {
              resolve(videoUrlOrBase64);
          } else {
              reject(new Error("Failed to load video for frame extraction. Format might be unsupported."));
          }
      };
      
      video.load();
    });
  };
