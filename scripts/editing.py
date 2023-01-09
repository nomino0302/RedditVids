import os
import moviepy.editor as mp
from moviepy.audio.fx.volumex import volumex
from random import choice
try:
    from scripts.functions import Print, createLogger, inform_logs, get_length
except ModuleNotFoundError:
    from functions import Print, createLogger, inform_logs, get_length

ERROR = "ERROR"
BUILD = "build"
SCREENSHOTS = os.path.join(BUILD, "screenshots")
TTS = os.path.join(BUILD, "tts")
VIDS = "vids"
BACKGROUND = [os.path.join(BUILD, "background", file) for file in os.listdir(os.path.join(BUILD, "background")) if file != ".DS_Store"]
MUSIC = [os.path.join(BUILD, "music", file) for file in os.listdir(os.path.join(BUILD, "music")) if file != ".DS_Store"]
invalid_chars = {
    "/": "∫",
    "<": "∑",
    ">": "∏",
    "\"": "ª",
    "*": "Ω",
    "?": "∆",
    "\\": "•",
    "|": "‰",
    ":": "ı"
}

log = createLogger("editing")

@inform_logs(log)
def make_video(subreddit, author, post_id, title):
    log.debug(f"subreddit: {subreddit}, author: {author}, post_id: {post_id}, title: {title}")
    if not os.listdir(SCREENSHOTS):
        print(f"{Print.red}Dossier 'screenshots' vide ! Veuillez lancer la fonction get_screenshots_and_texts().{Print.end}")
        log.error("'screenshots' directory empty! Please execute get_screenshots_and_texts() function.")
        return ERROR

    if not os.listdir(TTS):
        print(f"{Print.red}Dossier 'tts' vide ! Veuillez lancer la fonction texts_to_tts().{Print.end}")
        log.error("'tts' directory empty! Please execute texts_to_tts() function.")
        return ERROR
    
    if len(os.listdir(SCREENSHOTS)) != len(os.listdir(TTS)):
        print(f"{Print.red}Les dossiers 'screenshots' et 'tts' ne possèdent pas les mêmes contenus ! Veuillez recommencer tout le processus.{Print.end}")
        log.error("'screenshots' and 'tts' directories don't have the same content! Please retry the entire process.")
        return ERROR
    
    print(f"🖥️ {Print.purple}Édition de la vidéo...{Print.end}")
    log.info("Starting the editing of the video")

    time_per_tts = [get_length(os.path.join(TTS, file)) for file in sorted(os.listdir(TTS), key=lambda file: int(file[:-4]))]
    duration_tts = sum(time_per_tts)
    background_path = choice(BACKGROUND)
    music_path = choice(MUSIC)
    duration_background = get_length(background_path)
    duration_music = get_length(music_path)
    temp_dur_vid = duration_tts

    making_base_vid = True
    vids = []
    while making_base_vid:
        if duration_background < temp_dur_vid:
            vids.append(mp.VideoFileClip(background_path))
            temp_dur_vid -= duration_background
        else:
            vids.append(mp.VideoFileClip(background_path).subclip(0, temp_dur_vid))
            making_base_vid = False
    vid = mp.concatenate_videoclips(vids)

    #! La musique se joue qu'une seule fois lors des grandes videos
    temp_dur_vid = duration_tts
    making_base_music = True
    musics = []
    while making_base_music:
        if duration_music < temp_dur_vid:
            musics.append(volumex(mp.AudioFileClip(music_path), 0.05))
            temp_dur_vid -= duration_music
        else:
            musics.append(volumex(mp.AudioFileClip(music_path).subclip(0, temp_dur_vid), 0.05))
            making_base_music = False
    vid.audio = mp.concatenate_audioclips(musics)

    slides = []
    for nb in range(1, len(time_per_tts) + 1):
        screenshot = mp.ImageClip(os.path.join(SCREENSHOTS, f"{nb}.png")).set_duration(time_per_tts[nb - 1]).set_opacity(0.95)
        tts = mp.AudioFileClip(os.path.join(TTS, f"{nb}.mp3"))
        if nb == 1:
            screenshot = screenshot.set_start(0)
            tts = tts.set_start(0).set_end(tts.duration - 0.2)
        else:
            screenshot = screenshot.set_start(sum(time_per_tts[:nb - 2 + 1]))
            tts = tts.set_start(sum(time_per_tts[:nb - 2 + 1])).set_end(sum(time_per_tts[:nb - 2 + 1]) + tts.duration - 0.2)

        if screenshot.w > vid.w:
            screenshot = screenshot.resize(width=vid.w)
        if screenshot.h > vid.h:
            screenshot = screenshot.resize(height=vid.h)
        screenshot = screenshot.set_pos(("center", "center"))

        screenshot.audio = tts

        slides.append(screenshot)

    slides.insert(0, vid)
    final = mp.CompositeVideoClip(slides)

    if not os.path.exists(VIDS):
        os.mkdir(VIDS)
    name = f"{subreddit} - {author} - {post_id} - {title}"[:80] # 255 or 256 chars is the maximum for a filename
    for char in name:
        if char in invalid_chars:
            name = name.replace(char, invalid_chars[char])
    nb = 1
    first = True
    while name + ".mp4" in os.listdir(VIDS):
        if first:
            first = False
            name += f" ({nb})"
        else:
            name = name[:-(3 + len(str(nb)))] 
            nb += 1
            name += f" ({nb})"

    final.write_videofile(os.path.join(VIDS, f"{name}.mp4"))

if __name__ == "__main__":
    make_video("confession", "me", "1234azerty", "the title")