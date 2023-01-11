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
from PIL import Image

ERROR = "ERROR"
TIMEOUT = "TIMEOUT"
BUILD = "build"
SCREENSHOTS = os.path.join(BUILD, "screenshots")
JSONS = "jsons"
DIR_DONE_POSTS = os.path.join(JSONS, "done_posts.json")

log = createLogger("screenshots")

@inform_logs(log)
def get_screenshots_and_texts(subreddit, post_number, url=None, sort="hot", top_time=None, max_timeout=30):
    log.debug(f"subreddit: {subreddit}, post_number: {post_number}, url: {url}, sort: {sort}, top_time: {top_time}, max_timeout: {max_timeout}")
    if not subreddit:
        print(f"{Print.red}Vous devez préciser le subreddit à scrapper ! Votre subreddit = {subreddit} !{Print.end}")
        log.error(f"You need to precise the subreddit to scrap! Your subreddit = {subreddit} !")
        return ERROR
    
    if post_number > 28:
        last_number = post_number
        post_number = randint(0, 28)
        print(f"{Print.red}post_number changé de {last_number} en {post_number}.{Print.end}")
        log.error(f"post_number changed from {last_number} to {post_number}.")

    if (sort not in ["hot", "new", "rising"]) and (sort == "top" and top_time not in ["hour", "day", "week", "month", "year", "all"]):
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
    options.set_preference('intl.accept_languages', 'en-US, en')
    options.set_preference('layout.css.devPixelsPerPx','3.0') # this sets high resolution
    options.set_preference("dom.webnotifications.enabled", False)
    options.set_preference("devtools.selfxss.count", 100)
    driver = webdriver.Firefox(options=options)
    driver.set_window_size(1200, 800)
    start_time = time()

    # Setting reddit to dark theme first
    link = f"https://www.reddit.com/r/{subreddit}/{sort}/"
    if sort == "top":
        link += f"?t={top_time}"
    
    check = 1
    max_check = 7
    print(f"🌍{Print.purple}Recherche du post {Print.end}{Print.bold}({check}/{max_check}) :{Print.end}{Print.blue} Ouverture du navigateur{Print.end}")
    log.info(f"Recherche du post ({check}/{max_check}) : Ouverture du navigateur")
    driver.get(link)

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
    if not url:
        while True:
            print(f"{Print.previous()}🌍{Print.purple}Recherche du post {Print.end}{Print.bold}({check}/{max_check}) :{Print.end}{Print.blue} Recherche post valide {Print.bold}({essais} essai(s) / post_number = {post_number}){Print.end}")
            log.info(f"[Essai {essais} / post_number = {post_number}] -> Recherche du post ({check}/{max_check}) : Recherche post valide")
            sleep(0.5)

            if (time() - start_time) >= max_timeout:
                return TIMEOUT

            posts = driver.find_elements(By.CLASS_NAME, "_1oQyIsiPHYt6nx7VOmd1sz")
            if posts:
                break
            essais += 1

        to_check_post = [nb for nb in range(len(posts))]

        while True:
            if (time() - start_time) >= max_timeout:
                return TIMEOUT
            if not to_check_post:
                print(f"{Print.red}Aucun post n'a été trouvé... (to_check_post == []){Print.end}")
                log.error("No post has been found... (to_check_post == [])")
                return ERROR
            
            if post_number in to_check_post:
                nb = post_number
            else:
                nb = choice(to_check_post)
            to_check_post.remove(nb)

            print(f"{Print.previous()}🌍{Print.purple}Recherche du post {Print.end}{Print.bold}({check}/{max_check}) :{Print.end}{Print.blue} Recherche post valide {Print.bold}({essais} essai(s) / post_number = {nb}){Print.end}")
            log.info(f"[Essai {essais} / post_number = {nb}] -> Recherche du post ({check}/{max_check}) : Recherche post valide")
            
            post = posts[nb]
            
            ad_tag = post.find_elements(By.CLASS_NAME, "_2oEYZXchPfHwcf9mTMGMg8") # "Sponsorisé(e)" or "Promoted" tag in the post
            pinned = post.find_elements(By.CLASS_NAME, "rewiG9XNj_xqkQDcyR88j")
            if ad_tag or pinned:
                log.debug(f"[Essai {essais} / post_number = {nb}] -> Ad or pinned post -> skipped")
                essais += 1
                continue
            
            link = post.find_elements(By.CLASS_NAME, "SQnoC3ObvgnGjWt90zD9Z")[0].get_attribute("href")
            if link in done_posts:
                log.debug(f"[Essai {essais} / post_number = {nb}] -> Post already done -> skipped")
                essais += 1
                continue

            driver.execute_script(f'window.open("");')
            driver.switch_to.window(driver.window_handles[-1])
            driver.get(link)

            conditions_passed = True
            while True:
                if (time() - start_time) >= max_timeout:
                    return TIMEOUT
                try:
                    body_elem = driver.find_elements(By.CLASS_NAME, "_3xX726aBn29LDbsDtzr_6E")
                    if not body_elem:
                        conditions_passed = False
                    elif len(body_elem[0].text) < 300:
                        conditions_passed = False
                    break
                except IndexError:
                    sleep(0.1)

            if not conditions_passed:
                log.debug(f"[Essai {essais} / post_number = {nb}] -> No body or body not long enough (< 300 chars) -> skipped")
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
                essais += 1
                continue

            break
    else:
        driver.get(url)

    # Downloading the screenshots
    check += 1
    print(f"{Print.previous()}{Print.clear}🌍{Print.purple}Recherche du post {Print.end}{Print.bold}({check}/{max_check}) :{Print.end}{Print.blue} Screenshots du post{Print.end}")
    log.info(f"Recherche du post ({check}/{max_check}) : Screenshots du post")
    
    texts = [] # List of all the texts in order
    if not os.path.exists(BUILD):
        os.mkdir(BUILD)
    if not os.path.exists(SCREENSHOTS):
        os.mkdir(SCREENSHOTS)
    
    post_id = driver.current_url.replace("https://", "").split("/")[4]

    while True:
        if (time() - start_time) >= max_timeout:
            return TIMEOUT
        try:
            banner_elem = driver.find_elements(By.CLASS_NAME, "_26j3FxU4jTfjqi8m96HMmI")[0]
            upvotes_elem = driver.find_elements(By.CLASS_NAME, "_23h0-EcaBUorIHC-JZyh6J")[0]
            assert upvotes_elem.text # If the upvotes are showed (have text)
            header_elem = driver.find_elements(By.CLASS_NAME, "_14-YvdFiW5iVvfe5wdgmET")[0]
            title_elem = driver.find_elements(By.CLASS_NAME, "_2FCtq-QzlfuN-SwVMUZMM3")[0]
            tags_elem = driver.find_elements(By.CLASS_NAME, "_2fiIRtMpITeCAzXc4cANKp")
            footer_elem = driver.find_elements(By.CLASS_NAME, "_1hwEKkB_38tIoal6fcdrt9")[0]
            author_elem = header_elem.find_elements(By.TAG_NAME, "a")[0]

            title = title_elem.text
            texts.append(title)
            author = author_elem.text.replace("u/", "")
            banner_elem.screenshot(os.path.join(SCREENSHOTS, "banner.png"))
            upvotes_elem.screenshot(os.path.join(SCREENSHOTS, "upvotes.png"))
            header_elem.screenshot(os.path.join(SCREENSHOTS, "header.png"))
            title_elem.screenshot(os.path.join(SCREENSHOTS, "title.png"))
            if tags_elem:
                tags_elem[0].screenshot(os.path.join(SCREENSHOTS, "tags.png"))
            footer_elem.screenshot(os.path.join(SCREENSHOTS, "footer.png"))

            break
        except (IndexError, JavascriptException, AssertionError):
            sleep(0.1)

    # Making 1.png
    to_delete = ["banner.png", "upvotes.png", "header.png", "title.png", "footer.png"]
    if tags_elem:
        to_delete.append("tags.png")
    banner_img = Image.open(os.path.join(SCREENSHOTS, "banner.png"))
    upvotes_img = Image.open(os.path.join(SCREENSHOTS, "upvotes.png"))
    header_img = Image.open(os.path.join(SCREENSHOTS, "header.png"))
    title_img = Image.open(os.path.join(SCREENSHOTS, "title.png"))
    footer_img = Image.open(os.path.join(SCREENSHOTS, "footer.png"))
    widths = [header_img.width, title_img.width]
    heights = [upvotes_img.height, header_img.height + title_img.height]
    if tags_elem:
        tags_img = Image.open(os.path.join(SCREENSHOTS, "tags.png"))
        widths.append(tags_img.width)
        heights[1] += tags_img.height

    max_width = max(widths)
    max_height = max(heights)
    rgb_background = (26, 26, 27)
    new_image = Image.new("RGB", (max([upvotes_img.width + max_width, banner_img.width, footer_img.width]), banner_img.height + max_height + footer_img.height), rgb_background)

    if new_image.width <= banner_img.width:
        new_image.paste(banner_img, (0, 0))
    else:
        new_image.paste(banner_img, ((new_image.width - banner_img.width) // 2, 0))
    new_image.paste(upvotes_img, (0, banner_img.height))
    new_image.paste(header_img, (upvotes_img.width, banner_img.height))
    new_image.paste(title_img, (upvotes_img.width, banner_img.height + header_img.height))
    if tags_elem:
        new_image.paste(tags_img, (upvotes_img.width, banner_img.height + header_img.height + title_img.height))
        # Footer
        new_image.paste(footer_img, (0, banner_img.height + header_img.height + title_img.height + tags_img.height))
    else:
        new_image.paste(footer_img, (0, banner_img.height + header_img.height + title_img.height))
    new_image.save(os.path.join(SCREENSHOTS, "1.png"), "PNG")

    for file in to_delete:
        os.remove(os.path.join(SCREENSHOTS, file))

    # Making the other files
    while True:
        if (time() - start_time) >= max_timeout:
            return TIMEOUT
        try:
            body_elem = driver.find_elements(By.CLASS_NAME, "_3xX726aBn29LDbsDtzr_6E")[0]
            break
        except IndexError:
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

    return texts, author, post_id, title

if __name__ == "__main__":
    value = get_screenshots_and_texts("entitledparents", 0, url="https://www.reddit.com/r/entitledparents/comments/cr7dc9/my_family_is_pressuring_me_to_give_my_23f_sister/")
    if value == TIMEOUT:
        print("TIMEOUT!")
    printing = False
    if printing:
        texts, author, post_id, title = value[0], value[1], value[2], value[3]
        print(f"Author : {author}\n")
        print(f"Post ID : {post_id}")
        print(f"Title : {title}\n")
        for nb, elt in enumerate(texts):
            print(f"{nb + 1} : {elt}\n")
