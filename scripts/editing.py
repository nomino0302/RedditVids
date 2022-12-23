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
GAMEPLAYS = [os.path.join(BUILD, "gameplays", file) for file in os.listdir(os.path.join(BUILD, "gameplays")) if file != ".DS_Store"]
MUSIC = [os.path.join(BUILD, "music", file) for file in os.listdir(os.path.join(BUILD, "music")) if file != ".DS_Store"]

log = createLogger("editing")

@inform_logs(log)
def make_video(author, subreddit, title):
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

    time_per_tts = [get_length(os.path.join(TTS, file)) for file in os.listdir(TTS)]
    duration_tts = sum(time_per_tts)
    gameplay_path = choice(GAMEPLAYS)
    music_path = choice(MUSIC)
    duration_gameplay = get_length(gameplay_path)
    duration_music = get_length(music_path)
    temp_dur_tts = duration_tts
    vid_time = duration_tts + (0.5 * (len(time_per_tts) - 1))
    temp_vid_time = vid_time

    making_base_vid = True
    vids = []
    while making_base_vid:
        if duration_gameplay < temp_dur_tts + (0.5 * (len(time_per_tts) - 1)): # 0.5s of blank between each clips (except the first one)
            vids.append(mp.VideoFileClip(gameplay_path))
            temp_dur_tts -= duration_gameplay
        else:
            vids.append(mp.VideoFileClip(gameplay_path).subclip(0, temp_dur_tts + (0.5 * (len(time_per_tts) - 1))))
            making_base_vid = False
    vid = mp.concatenate_videoclips(vids)

    making_base_music = True
    musics = []
    while making_base_music:
        if duration_music < temp_vid_time:
            musics.append(volumex(mp.AudioFileClip(music_path), 0.03))
            temp_vid_time -= duration_music
        else:
            musics.append(volumex(mp.AudioFileClip(music_path).subclip(0, temp_vid_time), 0.03))
            making_base_music = False
    vid.audio = mp.CompositeAudioClip(musics)

    vid.write_videofile("test.mp4")

if __name__ == "__main__":
    make_video("me", "confession", "the title")