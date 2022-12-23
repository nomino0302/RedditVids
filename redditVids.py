import os
from scripts.screenshots import get_screenshots_and_texts
from scripts.tts import texts_to_tts
from scripts.editing import make_video
from scripts.functions import clear_data

ERROR = "ERROR"
TIMEOUT = "TIMEOUT"
MAKE = "MAKE"
CLEAR = "CLEAR"

def make_reddit_video(subreddit, post_number, sort="hot", top_time=None, one_by_one=True, max_timeout=30):

    value = get_screenshots_and_texts(subreddit, post_number, sort, top_time, max_timeout)
    if value not in [ERROR, TIMEOUT]:
        texts, author, title = value[0], value[1], value[2]
    else:
        return

    value = texts_to_tts(texts, one_by_one, max_timeout)
    if value == ERROR:
        return

    make_video(author, subreddit, title)

if __name__ == "__main__":
    os.chdir(os.path.dirname(__file__))

    action  = CLEAR

    if action == MAKE:
        make_reddit_video("confession", 0)
    elif action == CLEAR:
        clear_data()