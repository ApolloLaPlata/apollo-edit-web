import sys
import cv2
try:
    import mediapipe as mp
    pass
except ImportError:
    pass

def smart_crop(input_path, output_path, target_aspect=9/16):
    print(f"[ToolSmartCrop] Analisando {input_path} para tracking facial...")
    mp_face_detection = mp.solutions.face_detection
    cap = cv2.VideoCapture(input_path)
    
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    # Compute target width based on aspect ratio (e.g. 9:16)
    target_h = height
    target_w = int(height * target_aspect)
    
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (target_w, target_h))
    
    with mp_face_detection.FaceDetection(model_selection=0, min_detection_confidence=0.5) as face_detection:
        frame_count = 0
        last_center_x = width // 2
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
                
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = face_detection.process(frame_rgb)
            
            if results.detections:
                bbox = results.detections[0].location_data.relative_bounding_box
                center_x = int((bbox.xmin + bbox.width / 2) * width)
                last_center_x = center_x
            else:
                center_x = last_center_x
                
            # Smoothing or direct clamp
            # Calculate crop boundaries
            x1 = center_x - target_w // 2
            x2 = center_x + target_w // 2
            
            # Clamp to screen edges
            if x1 < 0:
                x1 = 0
                x2 = target_w
            elif x2 > width:
                x2 = width
                x1 = width - target_w
                
            cropped = frame[0:target_h, x1:x2]
            out.write(cropped)
            
            frame_count += 1
            if frame_count % 60 == 0:
                print(f"[ToolSmartCrop] Processados {frame_count} frames...")
                
    cap.release()
    out.release()
    print(f"[ToolSmartCrop] Concluido: {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python tool_smart_crop.py <input_video> <output_video_9x16>")
        sys.exit(1)
        
    smart_crop(sys.argv[1], sys.argv[2])
