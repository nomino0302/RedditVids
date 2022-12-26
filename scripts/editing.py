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
def make_video(subreddit, author, title):
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

    time_per_tts = [get_length(os.path.join(TTS, file)) for file in sorted(os.listdir(TTS))]
    duration_tts = sum(time_per_tts)
    background_path = choice(BACKGROUND)
    music_path = choice(MUSIC)
    duration_background = get_length(background_path)
    duration_music = get_length(music_path)
    temp_dur_tts = duration_tts
    vid_time = duration_tts + 0.5 * len(time_per_tts)
    temp_vid_time = vid_time

    making_base_vid = True
    vids = []
    while making_base_vid:
        if duration_background < temp_dur_tts + (0.5 * (len(time_per_tts) - 1)): # 0.5s of blank between each clips (except the first one)
            vids.append(mp.VideoFileClip(background_path))
            temp_dur_tts -= duration_background
        else:
            vids.append(mp.VideoFileClip(background_path).subclip(0, temp_dur_tts + (0.5 * (len(time_per_tts) - 1))))
            making_base_vid = False
    vid = mp.concatenate_videoclips(vids)

    making_base_music = True
    musics = []
    while making_base_music:
        if duration_music < temp_vid_time:
            musics.append(volumex(mp.AudioFileClip(music_path), 0.05))
            temp_vid_time -= duration_music
        else:
            musics.append(volumex(mp.AudioFileClip(music_path).subclip(0, temp_vid_time), 0.05))
            making_base_music = False
    vid.audio = mp.CompositeAudioClip(musics)

    slides = []
    for nb in range(1, len(time_per_tts) + 1):
        screenshot = mp.ImageClip(os.path.join(SCREENSHOTS, f"{nb}.png")).set_duration(time_per_tts[nb - 1] + 0.5).set_opacity(0.95)
        tts = mp.AudioFileClip(os.path.join(TTS, f"{nb}.mp3"))
        if nb == 1:
            screenshot = screenshot.set_start(0)
            tts = tts.set_start(0)
        else:
            screenshot = screenshot.set_start(sum(time_per_tts[:nb - 2 + 1]) + 0.5 * (nb - 1))
            tts = tts.set_start(sum(time_per_tts[:nb - 2 + 1]) + 0.5 * (nb - 1))

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
    name = f"{subreddit} - {author} - {title}"[:60] # 255 or 256 chars is the maximum for a filename
    for char in name:
        if char in invalid_chars:
            name = name.replace(char, invalid_chars[char])
    nb = 1
    first = True
    while name + ".mp4" in os.listdir(VIDS):
        if first:
            first = False
            name += f"({nb})"
        else:
            name = name[:-(2 + len(str(nb)))] 
            nb += 1
            name += f"({nb})"

    final.write_videofile(os.path.join(VIDS, f"{name}.mp4"))

if __name__ == "__main__":
    make_video("confession", "me", "the title")