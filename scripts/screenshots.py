import os
import json
try:
    from scripts.functions import Print, createLogger, clear_screenshots, inform_logs
except ModuleNotFoundError:
    from functions import Print, createLogger, clear_screenshots, inform_logs
from time import sleep, time
from random import randint, choice
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import NoSuchElementException, JavascriptException

ERROR = "ERROR"
TIMEOUT = "TIMEOUT"
BUILD = "build"
SCREENSHOTS = os.path.join(BUILD, "screenshots")
JSONS = "jsons"
DIR_DONE_POSTS = os.path.join(JSONS, "done_posts.json")

log = createLogger("screenshots")

@inform_logs(log)
def get_screenshots_and_texts(subreddit, post_number, sort="hot", top_time=None, max_timeout=30):
    if not subreddit:
        print(f"{Print.red}Vous devez préciser le subreddit à scrapper ! Votre subreddit = {subreddit} !{Print.end}")
        log.error(f"You need to precise the subreddit to scrap! Your subreddit = {subreddit} !")
        return ERROR
    
    if post_number > 28:
        last_number = post_number
        post_number = randint(0, 28)
        print(f"{Print.red}post_number changé de {last_number} en {post_number}.{Print.end}")
        log.error(f"post_number changed from {last_number} to {post_number}.")

    if (sort not in ["hot", "new", "rising"]) or (sort == "top" and top_time not in ["hour", "day", "week", "month", "year", "all"]):
        print(f'{Print.red}Vous devez préciser le triage à respecter ! Votre sort = {sort}, votre top_time = {top_time} ! (sort = ["hot", "new", "top", "rising"], top_time = [None, "hour", "day", "week", "month", "year", "all"]){Print.end}')
        log.error(f'You need to precise the subreddit to scrap! Your sort = {sort}, your top_time = {top_time} ! (sort = ["hot", "new", "top", "rising"], top_time = [None, "hour", "day", "week", "month", "year", "all"])')
        return ERROR
    
    if type(max_timeout) not in [int, float]:
        log.error(f"Incorrect max_timeout value ({max_timeout}) -> changed to 30")
        max_timeout = 30

    clear_screenshots(delete_folder=False)

    if not os.path.exists(JSONS):
        os.mkdir(JSONS)
    if os.path.exists(DIR_DONE_POSTS):
        with open(DIR_DONE_POSTS, "r") as f:
            done_posts = json.load(f)
    else:
        done_posts = []

     # Setting the web driver options
    options = Options()
    options.headless = True
    options.set_preference("media.volume_scale", "0.0")
    options.set_preference("dom.webnotifications.enabled", False)
    options.set_preference("devtools.selfxss.count", 100)
    driver = webdriver.Firefox(options=options)
    driver.set_window_size(1200, 800)
    start_time = time()

    # Setting reddit to dark theme first
    url = f"https://www.reddit.com/r/{subreddit}/{sort}/"
    if sort == "top":
        url += f"?t={top_time}"
    
    check = 1
    max_check = 7
    print(f"🌍{Print.purple}Recherche du post {Print.end}{Print.bold}({check}/{max_check}) :{Print.end}{Print.blue} Ouverture du navigateur{Print.end}")
    log.info(f"Recherche du post ({check}/{max_check}) : Ouverture du navigateur")
    driver.get(url)

    check += 1
    print(f"{Print.previous()}🌍{Print.purple}Recherche du post {Print.end}{Print.bold}({check}/{max_check}) :{Print.end}{Print.blue} Rejet des cookies{Print.end}")
    log.info(f"Recherche du post ({check}/{max_check}) : Rejet des cookies")
    while True:
        if (time() - start_time) >= max_timeout:
            return TIMEOUT
        try:
            reject_cookies_button = driver.find_elements(By.CLASS_NAME, "_1tI68pPnLBjR1iHcL7vsee")[0]
            reject_cookies_button.click()
            break
        except IndexError:
            sleep(0.1)

    check += 1
    print(f"{Print.previous()}🌍{Print.purple}Recherche du post {Print.end}{Print.bold}({check}/{max_check}) :{Print.end}{Print.blue} Click sur le bouton +{Print.end}")
    log.info(f"Recherche du post ({check}/{max_check}) : Click sur le bouton +")
    while True:
        if (time() - start_time) >= max_timeout:
            return TIMEOUT
        try:
            more_button = driver.find_element(By.ID,"USER_DROPDOWN_ID")
            more_button.click()
            break
        except NoSuchElementException:
            sleep(0.1)
    
    check += 1
    print(f"{Print.previous()}🌍{Print.purple}Recherche du post {Print.end}{Print.bold}({check}/{max_check}) :{Print.end}{Print.blue} Activation du mode sombre{Print.end}")
    log.info(f"Recherche du post ({check}/{max_check}) : Activation du mode sombre")
    while True:
        if (time() - start_time) >= max_timeout:
            return TIMEOUT
        try:
            on_darkmode = driver.find_elements(By.CLASS_NAME, "_2e2g485kpErHhJQUiyvvC2")[0]
            on_darkmode.click()
            break
        except IndexError:
            sleep(0.1)
    
    # Check if this is a valuable post
    check += 1
    essais = 0
    first_loop = True
    while True:
        print(f"{Print.previous()}🌍{Print.purple}Recherche du post {Print.end}{Print.bold}({check}/{max_check}) :{Print.end}{Print.blue} Recherche post valide {Print.bold}({essais} essai(s) / post_number = {post_number}){Print.end}")
        log.info(f"[Essai {essais} / post_number = {post_number}] -> Recherche du post ({check}/{max_check}) : Recherche post valide")

        if (time() - start_time) >= max_timeout:
            return TIMEOUT

        if not first_loop and not to_check_post:
            print(f"{Print.red}Aucun post n'a été trouvé... (post_number < 0){Print.end}")
            log.error("No post has been found... (post_number < 0)")
            return ERROR
        
        # Creating the possible posts to take
        posts = driver.find_elements(By.CLASS_NAME, "_1oQyIsiPHYt6nx7VOmd1sz")
        log.debug(f"[Essai {essais} / post_number = {post_number}] -> Max posts available = {len(posts)}")

        if not posts or len(posts) < 10:
            log.debug(f"[Essai {essais} / post_number = {post_number}] -> No post found or < 10 -> waiting")
            essais += 1
            sleep(0.1)
            continue

        # Creating the list of possible posts
        elif first_loop:
            first_loop = False
            to_check_post = [nb for nb in range(len(posts))]
            if post_number not in to_check_post:
                log.debug(f"[Essai {essais} / post_number = {post_number}] -> post_number {post_number} not in to_check_post -> skipped")
                post_number = choice(to_check_post)
                essais += 1
                continue
        
        to_check_post.remove(post_number)

        post = posts[post_number]
        
        ad_tag = post.find_elements(By.CLASS_NAME, "_2oEYZXchPfHwcf9mTMGMg8") # "Sponsorisé(e)" or "Promoted" tag in the post
        pinned = post.find_elements(By.CLASS_NAME, "rewiG9XNj_xqkQDcyR88j")
        if ad_tag or pinned:
            log.debug(f"[Essai {essais} / post_number = {post_number}] -> Ad or pinned post -> skipped")
            post_number = choice(to_check_post)
            essais += 1
            continue
        
        link = post.find_elements(By.TAG_NAME, "a")[1].get_attribute("href")
        if link in done_posts:
            log.debug(f"[Essai {essais} / post_number = {post_number}] -> Post already done -> skipped")
            post_number = choice(to_check_post)
            essais += 1
            continue

        driver.execute_script(f'window.open("{link}","_blank");')
        driver.switch_to.window(driver.window_handles[-1])

        conditions_passed = True
        while True:
            if (time() - start_time) >= max_timeout:
                return TIMEOUT
            try:
                body_elem = driver.find_elements(By.CLASS_NAME, "_3xX726aBn29LDbsDtzr_6E")[0]
                if not body_elem or len(body_elem.text) < 300:
                    conditions_passed = False
                break
            except IndexError:
                sleep(0.1)

        if not conditions_passed:
            log.debug(f"[Essai {essais} / post_number = {post_number}] -> No body or body not long enough (< 300 chars) -> skipped")
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
            post_number = choice(to_check_post)
            essais += 1
            continue

        break

    # Downloading the screenshots
    check += 1
    print(f"{Print.previous()}{Print.clear}🌍{Print.purple}Recherche du post {Print.end}{Print.bold}({check}/{max_check}) :{Print.end}{Print.blue} Screenshots du post{Print.end}")
    log.info(f"Recherche du post ({check}/{max_check}) : Screenshots du post")
    
    texts = [] # List of all the texts in order
    if not os.path.exists(BUILD):
        os.mkdir(BUILD)
    if not os.path.exists(SCREENSHOTS):
        os.mkdir(SCREENSHOTS)
    
    driver.execute_script('document.getElementsByClassName("_2RkQc9Gtsq3cPQNZLYv4zc")[0].remove()')

    title_elem = driver.find_elements(By.CLASS_NAME, "_eYtD2XCVieq6emjKBH3m")[0]
    title_elem.screenshot(os.path.join(SCREENSHOTS, "1.png"))
    title = title_elem.text
    texts.append(title)

    while True:
        if (time() - start_time) >= max_timeout:
            return TIMEOUT
        try:
            header_elem = driver.find_elements(By.CLASS_NAME, "cZPZhMe-UCZ8htPodMyJ5")[-1]
            author_elem = header_elem.find_elements(By.TAG_NAME, "a")[0]
            author = author_elem.text.replace("u/", "")
            break
        except (IndexError, JavascriptException):
            sleep(0.1)

    parts_of_texts_elem = body_elem.find_elements(By.CLASS_NAME, "_1qeIAgB0cPwnLhDF9XSiJM")
    for index in range(len(parts_of_texts_elem)):
        parts_of_texts_elem[index].screenshot(os.path.join(SCREENSHOTS, f"{index + 2}.png"))
        texts.append(parts_of_texts_elem[index].text)
    
    done_posts.append(driver.current_url)
    with open(DIR_DONE_POSTS, "w", encoding="utf8") as f:
        json.dump(done_posts, f, ensure_ascii=False, indent=4)
    
    check += 1
    print(f"{Print.previous()}🌍{Print.purple}Recherche du post {Print.end}{Print.bold}({check}/{max_check}) :{Print.end}{Print.blue} Fin de get_screenshots_and_texts(){Print.end}")
    log.info(f"Recherche du post ({check}/{max_check}) : Fin de get_screenshots_and_texts()")

    driver.close()
    driver.quit()

    print(f"{Print.green}Tous les screenshots et textes ont été enregistrés avec succès !{Print.end}\n")
    log.info(f"All the screenshots and texts have been saved successfully!")

    return texts, author, title

if __name__ == "__main__":
    value = get_screenshots_and_texts("confession", 0)
    if value == TIMEOUT:
        print("TIMEOUT!")
    elif value == ERROR:
        print("ERROR!")
