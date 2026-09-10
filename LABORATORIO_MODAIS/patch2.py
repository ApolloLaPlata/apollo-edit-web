import re
with open("E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/public/modal_ai_studio.html", "r", encoding="utf-8") as f:
    text = f.read()

# Fix the broken downloadCurrentMedia
broken_block = """function downloadCurrentMedia() {
    if (currentAudioData) {
        downloadAudio();
    } else if (currentImageData) {
        downloadImage();
    } else if (currentVideoData) {
        downloadVideo();
    }
} else if (currentVideoData) {
        downloadVideo();
    }
}"""

fixed_block = """function downloadCurrentMedia() {
    if (currentAudioData) {
        downloadAudio();
    } else if (currentImageData) {
        downloadImage();
    } else if (currentVideoData) {
        downloadVideo();
    }
}"""

text = text.replace(broken_block, fixed_block)

with open("E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/public/modal_ai_studio.html", "w", encoding="utf-8") as f:
    f.write(text)
