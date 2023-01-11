from scripts.screenshots import get_screenshots_and_texts
from scripts.tts import texts_to_tts
from scripts.editing import make_video
from scripts.functions import clear_data, Print
from random import choice

ERROR = "ERROR"
TIMEOUT = "TIMEOUT"
MAKE = "MAKE"
CLEAR = "CLEAR"

def make_reddit_video(subreddit, post_number, url=None, sort="hot", top_time=None, one_by_one=True, max_timeout=30):

    value = get_screenshots_and_texts(subreddit, post_number, url, sort, top_time, max_timeout)
    if value not in [ERROR, TIMEOUT]:
        texts, author, post_id, title = value[0], value[1], value[2], value[3]
    else:
        if value == TIMEOUT:
            print(f"{Print.red}The function timeouted!{Print.end}")
        return

    value = texts_to_tts(texts, one_by_one, max_timeout)
    if value == ERROR:
        return

    make_video(subreddit, author, post_id, title)

if __name__ == "__main__":
    action  = MAKE
    random = True

    if action == MAKE:
        if not random:
            make_reddit_video("entitledparents", 16, url="https://www.reddit.com/r/entitledparents/comments/cr7dc9/my_family_is_pressuring_me_to_give_my_23f_sister/", sort="rising", one_by_one=False, max_timeout=60)
        else:
            random_subs = ["confession", "AmItheAsshole", "entitledparents", "tifu", "pettyrevenge", "NuclearRevenge", "unpopularopinion", "stories", "ParanormalEncounters"]
            random_post_number = list(range(0, 9)) * 3 + list(range(9, 19)) * 2 + list(range(19, 28))
            random_sort = ["hot"] * 4 + ["top"] * 2 + ["rising"] * 2 + ["new"]
            random_top_time = ["year"] * 5 + ["all"] * 4 + ["month"] * 3 + ["week"] * 2 + ["day"] + ["hour"]

            subreddit = choice(random_subs)
            post_number = choice(random_post_number)
            sort = choice(random_sort)
            if sort == "top":
                top_time = choice(random_top_time)
            else:
                top_time = None

            make_reddit_video(subreddit, post_number, sort=sort, top_time=top_time, one_by_one=False, max_timeout=40)

    elif action == CLEAR:
        clear_data(videos=True)
