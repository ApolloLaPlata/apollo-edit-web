import re
with open("E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/public/modal_ai_studio.html", "r", encoding="utf-8") as f:
    text = f.read()

text = text.replace("currentImageData = data.audio_base64", "currentAudioData = data.audio_base64")

f1 = """function downloadCurrentMedia() {
    if (currentAudioData) {
        downloadAudio();
    } else if (currentImageData) {
        downloadImage();
    } else if (currentVideoData) {
        downloadVideo();
    }
}"""

text = re.sub(r"function downloadCurrentMedia\(\) \{[\s\S]*?\}", f1, text)

f2 = """
function downloadAudio() {
    if (!currentAudioData) return;
    const a = document.createElement('a');
    if (currentAudioData.startsWith('http') || currentAudioData.startsWith('data:')) {
        a.href = currentAudioData;
    } else {
        a.href = 'data:audio/wav;base64,' + currentAudioData;
    }
    a.download = `apollo_audio_generated.wav`;
    a.click();
}
function downloadImage() {"""
text = text.replace("function downloadImage() {", f2)

with open("E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/public/modal_ai_studio.html", "w", encoding="utf-8") as f:
    f.write(text)
