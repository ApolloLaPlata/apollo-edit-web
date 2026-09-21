# -*- coding: utf-8 -*-
with open('servidor_web.py', 'r', encoding='utf-8') as f:
    code = f.read()

old_duration = '''        duration = body.get("duration", 30)
        if lyrics and engine in ["acestep", "minimax"]:
            duration = 180  # Forca um limite alto para a musica terminar naturalmente'''

new_duration = '''        duration = body.get("duration", 30)
        if lyrics and engine in ["acestep", "minimax"]:
            linhas_reais = [L for L in lyrics.split('\\n') if L.strip() and not L.strip().startswith('[')]
            est_dur = max(30, min(len(linhas_reais) * 7 + 10, 180)) 
            duration = est_dur'''

code = code.replace(old_duration, new_duration)

old_ace = '''"ace-step": "ACE-STEP 1.5 FORMULA:\\n- CRITICAL: DO NOT TRANSLATE THE PROMPT. Keep the genre and prompt in its original language (e.g., Portuguese).\\n- Prompt MUST be a comma-separated list: [Genre], [Mood], [2-3 Instruments], [Vocal type], [Production style], [BPM] bpm.\\n- Do NOT write conversational sentences.\\n- Append mastering tags: high quality, studio mix, masterpiece.\\n- Lyrics MUST begin with [pt] (if Portuguese) or [en] (if English), followed by structural tags like [Verse], [Chorus], [Outro].\\n- Keep the original lyrical meaning and language completely intact.",'''

new_ace = '''"ace-step": "ACE-STEP 1.5 FORMULA:\\n- CRITICAL: Translate vocal and mood tags to English (e.g., 'male vocals', 'female vocals', 'upbeat') so the AI understands them, but keep culturally specific genre names.\\n- Prompt MUST be a comma-separated list: [Genre], [Mood in English], [Instruments in English], [Vocal type in English (e.g. male vocals, female vocals)], [Production style], [BPM] bpm.\\n- Do NOT write conversational sentences.\\n- Append tags: high quality, studio mix, masterpiece.\\n- Lyrics MUST begin with [pt] (if Portuguese), followed by structural tags like [Verse], [Chorus]. Add [Outro] and (Fade out) at the end.\\n- Keep the original lyrical meaning and language completely intact.",'''

code = code.replace(old_ace, new_ace)

with open('servidor_web.py', 'w', encoding='utf-8') as f:
    f.write(code)
print("Replaced!")
