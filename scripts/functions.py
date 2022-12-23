import os
import shutil
import logging
import datetime
import subprocess

BUILD = "build"
TTS = os.path.join(BUILD, "tts")
SCREENSHOTS = os.path.join(BUILD, "screenshots")
LOGS = "logs"
JSONS = "jsons"
SCRIPTS = "scripts"

def createLogger(name: str, max_logs: int=5) -> logging.Logger:
    """
    It creates a logger that logs to a file in the logs directory
    
    :param name: The name of the logger. This is used to create a folder in the 'logs' directory
    :param max_logs: The maximum number of logs to keep, defaults to 5
    :return: A logger object.
    """

    if not os.path.exists("logs"):
        os.mkdir("logs")
    if not os.path.exists(os.path.join("logs", name)):
        os.mkdir(os.path.join("logs", name))

    today = str(datetime.datetime.now())
    logs = os.listdir(os.path.join("logs", name))

    if len(logs) >= max_logs:
        oldest = min([datetime.datetime.strptime(file[:-4], "%Y-%m-%d %H:%M:%S.%f") for file in logs if file[-4:] == ".log"])
        os.remove(os.path.join("logs", name, f"{oldest}.log"))
    
    logger = logging.getLogger(name)
    handler = logging.FileHandler(os.path.join("logs", name, f"{today}.log"))
    formatter = logging.Formatter("%(asctime)s - %(levelname)s: %(message)s")

    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    return logger

def inform_logs(log: logging.Logger):
    def decorateur(fonction):
        def wrapper(*args, **kwargs):
            log.debug(f"---STARTING {fonction.__name__}---")
            value = fonction(*args, **kwargs)
            log.debug(f"---END OF {fonction.__name__}---")
            return value
        return wrapper
    return decorateur

log = createLogger("functions")

class Print():
    black = "\033[30m"
    red = "\033[31m"
    green = "\033[32m"
    yellow = "\033[33m"
    blue = "\033[34m"
    purple = "\033[35m"
    cyan = "\033[36m"
    white = "\033[37m"
    bold = "\033[1m"
    underline = "\033[2;40m"
    end = "\033[0m"
    clear = "\033[K"

    def previous(lines: int=1) -> str:
        return "\033[F" * lines

    def move(cols: int) -> str:
        return f"\033[{cols}G"

@inform_logs(log)
def clear_tts(delete_folder=True):
    if os.path.exists(TTS):
        if delete_folder:
            shutil.rmtree(TTS)
        else:
            for file in os.listdir(TTS):
                os.remove(os.path.join(TTS, file))
        log.info(f"{TTS} (ou les fichiers de {TTS}) ont été supprimés.")

@inform_logs(log)
def clear_screenshots(delete_folder=True):
    if os.path.exists(SCREENSHOTS):
        if delete_folder:
            shutil.rmtree(SCREENSHOTS)
        else:
            for file in os.listdir(SCREENSHOTS):
                if file == "1":
                    shutil.rmtree(os.path.join(SCREENSHOTS, "1"))
                else:
                    os.remove(os.path.join(SCREENSHOTS, file))
        log.info(f"{SCREENSHOTS} (ou les fichiers de {SCREENSHOTS}) ont été supprimés.")

@inform_logs(log)
def clear_build(delete_folder=True):
    clear_tts(delete_folder)
    clear_screenshots(delete_folder)

@inform_logs(log)
def clear_logs(delete_folder=True):
    if os.path.exists(LOGS):
        if delete_folder:
            shutil.rmtree(LOGS)
        else:
            for folder in os.listdir(LOGS):
                shutil.rmtree(os.path.join(LOGS, folder))

def clear_data(videos=False):
    if videos:
        if os.path.exists("vids"):
            shutil.rmtree("vids")
    if os.path.exists(done_posts := os.path.join(JSONS, "done_posts.json")):
        os.remove(done_posts)
    clear_build()
    clear_logs()

def get_percentage(nb, total):
    percent = str(nb / total * 100)
    percent = percent[:percent.index(".") + 3]
    return percent + "%"

@inform_logs(log)
def get_length(filename):
    log.info(f"Getting the length of {filename}")
    result = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                             "format=duration", "-of",
                             "default=noprint_wrappers=1:nokey=1", filename],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT)
    return float(result.stdout)
