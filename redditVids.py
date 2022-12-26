from scripts.screenshots import get_screenshots_and_texts
from scripts.tts import texts_to_tts
from scripts.editing import make_video
from scripts.functions import clear_data
from random import choice

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

    make_video(subreddit, author, title)

if __name__ == "__main__":
    action  = MAKE
    random = True

    if action == MAKE:
        if not random:
            make_reddit_video("confession", one_by_one=True, max_timeout=30)
        else:
            random_subs = ["confession", "AmItheAsshole", "entitledparents", "tifu", "pettyrevenge", "NuclearRevenge", "unpopularopinion", "stories" "ParanormalEncounters"]
            random_post_number = list(range(1, 9)) * 3 + list(range(9, 19)) * 2 + list(range(19, 28))
            random_sort = ["hot"] * 4 + ["top"] * 2 + ["rising"] * 2 + ["new"]
            random_top_time = ["year"] * 5 + ["all"] * 4 + ["month"] * 3 + ["week"] * 2 + ["day"] + ["hour"]

            subreddit = choice(random_subs)
            post_number = choice(random_post_number)
            sort = choice(random_sort)
            if sort == "top":
                top_time = choice(random_top_time)
            else:
                top_time = None

            make_reddit_video(subreddit, post_number, sort, top_time, one_by_one=True, max_timeout=30)

    elif action == CLEAR:
        clear_data(videos=True)
