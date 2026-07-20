import sys
from scenedetect import VideoManager, SceneManager
from scenedetect.detectors import ContentDetector

def find_scenes(video_path):
    print(f"[ToolSceneDetect] Buscando cortes no video {video_path}...")
    video_manager = VideoManager([video_path])
    scene_manager = SceneManager()
    scene_manager.add_detector(ContentDetector())
    
    video_manager.set_downscale_factor()
    video_manager.start()
    
    scene_manager.detect_scenes(frame_source=video_manager)
    scene_list = scene_manager.get_scene_list()
    
    for i, scene in enumerate(scene_list):
        print(f"Cena {i+1}: Start {scene[0].get_timecode()} | End {scene[1].get_timecode()}")
    
    # Save to a text file for Apollo to read
    output_txt = video_path + ".scenes.txt"
    with open(output_txt, "w") as f:
        for i, scene in enumerate(scene_list):
            f.write(f"{scene[0].get_seconds()},{scene[1].get_seconds()}\n")
            
    print(f"[ToolSceneDetect] Concluido: {output_txt}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python tool_scene_detect.py <input_video>")
        sys.exit(1)
        
    find_scenes(sys.argv[1])
