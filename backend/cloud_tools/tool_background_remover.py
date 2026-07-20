import sys
import cv2
import numpy as np
from rembg import remove

def remove_video_bg(input_path, output_path):
    print(f"[ToolRembg] Removendo fundo quadro a quadro: {input_path}")
    cap = cv2.VideoCapture(input_path)
    
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    # We will output as mp4 with a greenscreen or alpha if supported
    # Greenscreen is easiest for standard mp4 compatibility
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    frame_count = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
            
        # apply rembg
        # Note: running rembg on CPU per frame is slow but it's free.
        bg_removed = remove(frame)
        
        # bg_removed has alpha channel, create green background
        alpha_channel = bg_removed[:, :, 3] / 255.0
        green_bg = np.zeros_like(frame, dtype=np.uint8)
        green_bg[:] = (0, 255, 0)
        
        for c in range(0, 3):
            green_bg[:, :, c] = (alpha_channel * bg_removed[:, :, c] +
                                 (1 - alpha_channel) * green_bg[:, :, c])
            
        out.write(green_bg)
        frame_count += 1
        if frame_count % 30 == 0:
            print(f"[ToolRembg] Processado {frame_count} frames...")
            
    cap.release()
    out.release()
    print(f"[ToolRembg] Concluido: {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python tool_background_remover.py <input_video> <output_video_green>")
        sys.exit(1)
        
    remove_video_bg(sys.argv[1], sys.argv[2])
