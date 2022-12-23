import os
import requests
import concurrent.futures
try:
    from scripts.functions import Print, createLogger, clear_tts, inform_logs, get_percentage
except ModuleNotFoundError:
    from functions import Print, createLogger, clear_tts, inform_logs, get_percentage
from time import sleep, time
from collections import Counter
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import JavascriptException, NoSuchElementException

ERROR = "ERROR"
TIMEOUT = "TIMEOUT"
BUILD = "build"
TTS = os.path.join(BUILD, "tts")
firefox_on_snap = False

log = createLogger("tts")

@inform_logs(log)
def texts_to_tts(list_of_texts, one_by_one=True, max_timeout=30):
    if not list_of_texts: # Liste vide
        print(f"{Print.red}La liste de textes doit au moins contenir 1 texte !{Print.end}")
        log.error("The list of texts need to have at least 1 text!")
        return ERROR

    if type(max_timeout) not in [int, float]:
        log.error(f"Incorrect max_timeout value ({max_timeout}) -> changed to 30")
        max_timeout = 30
    
    clear_tts(delete_folder=False)

    texts_numbers = {}
    num = 1
    for text in list_of_texts:
        texts_numbers[str(num)] = text # num = nom du fichier (1.mp3 par exemple)
        num += 1
    
    min_files = 1
    max_files = len(texts_numbers)
    global checkpoints
    checkpoints = 12 * max_files
    global check_done # check_done = nombre de checkpoints passés
    check_done = 0
    global in_process
    in_process = 0
    global waiting
    waiting = max_files
    global done
    done = 0

    print(f"{Print.previous()}\r🎧{Print.purple}Création des audio :{Print.end} {Print.bold}({done}✅/{in_process}🔁/{waiting}⌛️){Print.end} {Print.blue}({get_percentage(check_done, checkpoints)}){Print.end}")

    if one_by_one:
        for filename, text in texts_numbers.items():
            try:
                value = get_mp3(text, filename, max_timeout)
                if value == TIMEOUT:
                    print(f"{Print.red}Une fonction a pris trop de temps à s'exécuter (max {max_timeout}s) ! Des fichiers audio sont possiblement manquants !{Print.end}")
                    log.critical(f"A function took too much time to execute (max {max_timeout}s)! Some audio files may be missing!")
            except Exception as err:
                print(f"{Print.red}Une erreur inattendue est survenue pendant l'exécution de get_mp3 : {err}{Print.end}")
                log.critical(f"An unexpected error occurred while get_mp3 execution: {err}", exc_info=True)

    else:
        with concurrent.futures.ThreadPoolExecutor() as executor: # optimally defined number of threads
            res = [executor.submit(get_mp3, text, filename, max_timeout) for filename, text in texts_numbers.items()]
            concurrent.futures.wait(res)
        
            for return_value in res:
                try:
                    result = return_value.result()
                    if result == TIMEOUT:
                        print(f"{Print.red}Une fonction a pris trop de temps à s'exécuter (max {max_timeout}s) ! Des fichiers audio sont possiblement manquants !{Print.end}")
                        log.critical(f"A function took too much time to execute (max {max_timeout}s)! Some audio files may be missing!")
                except Exception as err:
                    print(f"{Print.red}Une erreur inattendue est survenue pendant l'exécution de get_mp3 : {err}{Print.end}")
                    log.critical(f"An unexpected error occurred while get_mp3 execution: {err}", exc_info=True)

    wanted_list = [f"{num}.mp3" for num in range(min_files, max_files + 1)]
    tts_list = os.listdir(TTS)
    if Counter(tts_list) != Counter(wanted_list): # Same values but not in the same order
        print(f"{Print.red}Des pistes audio sont manquantes :{Print.end} {Print.bold}{[file for file in wanted_list if file not in tts_list]}{Print.end}")
        log.error(f"Some audio files are missing: {[file for file in wanted_list if file not in tts_list]}")
        return ERROR
    else:
        print(f"{Print.green}Tous les audio ont été enregistrés avec succès !{Print.end}")
        log.info("All the audio files have been saved successfully!")

@inform_logs(log)
def get_mp3(text, filename, max_timeout):
    global checkpoints
    global check_done
    global in_process
    global waiting
    global done

    waiting -= 1
    in_process += 1
    print(f"{Print.previous()}\r🎧{Print.purple}Création des audio :{Print.end} {Print.bold}({done}✅/{in_process}🔁/{waiting}⌛️){Print.end} {Print.blue}({get_percentage(check_done, checkpoints)}){Print.end}")

    # Setting the web driver options
    options = Options()
    if firefox_on_snap:
        options.binary_location = os.path.join("/", "snap", "firefox", "current", "usr", "lib", "firefox", "firefox")
    options.headless = True
    options.set_preference("media.volume_scale", "0.0")
    options.set_preference("dom.webnotifications.enabled", False)
    options.set_preference("devtools.selfxss.count", 100)
    driver = webdriver.Firefox(options=options)
    start_time = time()

    # Getting the .mp3 file of the TTS
    # Putting the text in the text field
    driver.get("https://soundbite.speechify.com/edit?minimizeWidget=true&ttsOnline=true")
    while True:
        if (time() - start_time) >= max_timeout:
            return TIMEOUT
        try:
            driver.execute_script(f'document.getElementsByClassName("cdx-block")[0].innerText = "{text}";')
            break
        except JavascriptException:
            sleep(0.1)
    log.info(f"[{filename}.mp3] -> Text written in the field")
    check_done += 1
    print(f"{Print.previous()}\r🎧{Print.purple}Création des audio :{Print.end} {Print.bold}({done}✅/{in_process}🔁/{waiting}⌛️){Print.end} {Print.blue}({get_percentage(check_done, checkpoints)}){Print.end}")

    # Getting the .mp3 link
    while True:
        if (time() - start_time) >= max_timeout:
            return TIMEOUT
        try:
            save_button = driver.find_elements(By.CLASS_NAME, "mr-2")[2]
            save_button.click()
            break
        except IndexError:
            sleep(0.1)
    log.info(f"[{filename}.mp3] -> Save button clicked")
    check_done += 1
    print(f"{Print.previous()}\r🎧{Print.purple}Création des audio :{Print.end} {Print.bold}({done}✅/{in_process}🔁/{waiting}⌛️){Print.end} {Print.blue}({get_percentage(check_done, checkpoints)}){Print.end}")

    while True:
        if (time() - start_time) >= max_timeout:
            return TIMEOUT
        try:
            pop_up_quit_button = driver.find_elements(By.CLASS_NAME, "reactour__close-button")[0]
            pop_up_quit_button.click()
            break
        except IndexError:
            sleep(0.1)
    log.info(f"[{filename}.mp3] -> Pop-up closed")
    check_done += 1
    print(f"{Print.previous()}\r🎧{Print.purple}Création des audio :{Print.end} {Print.bold}({done}✅/{in_process}🔁/{waiting}⌛️){Print.end} {Print.blue}({get_percentage(check_done, checkpoints)}){Print.end}")

    while True:
        if (time() - start_time) >= max_timeout:
            return TIMEOUT
        try:
            share_quit_button = driver.find_elements(By.CLASS_NAME, "rounded-md")[4]
            share_quit_button.click()
            break
        except IndexError:
            sleep(0.1)
    log.info(f"[{filename}.mp3] -> Share window closed")
    log.info(f"URL of the audio making platform: {driver.current_url}")
    check_done += 1
    print(f"{Print.previous()}\r🎧{Print.purple}Création des audio :{Print.end} {Print.bold}({done}✅/{in_process}🔁/{waiting}⌛️){Print.end} {Print.blue}({get_percentage(check_done, checkpoints)}){Print.end}")

    while True:
        if (time() - start_time) >= max_timeout:
            return TIMEOUT
        try:
            more_button = driver.find_elements(By.CLASS_NAME, "header-menu-button")[0]
            more_button.click()
            break
        except IndexError:
            sleep(0.1)
    log.info(f"[{filename}.mp3] -> More button clicked")
    check_done += 1
    print(f"{Print.previous()}\r🎧{Print.purple}Création des audio :{Print.end} {Print.bold}({done}✅/{in_process}🔁/{waiting}⌛️){Print.end} {Print.blue}({get_percentage(check_done, checkpoints)}){Print.end}")

    while True:
        if (time() - start_time) >= max_timeout:
            return TIMEOUT
        try:
            download_button = driver.find_element(By.ID, "headlessui-menu-item-:r2:")
            download_button.click()
            break
        except NoSuchElementException:
            sleep(0.1)
    log.info(f"[{filename}.mp3] -> Download button clicked")
    check_done += 1
    print(f"{Print.previous()}\r🎧{Print.purple}Création des audio :{Print.end} {Print.bold}({done}✅/{in_process}🔁/{waiting}⌛️){Print.end} {Print.blue}({get_percentage(check_done, checkpoints)}){Print.end}")

    while True:
        if (time() - start_time) >= max_timeout:
            return TIMEOUT
        try:
            driver.switch_to.window(driver.window_handles[1])
            while (mp3_url := driver.current_url) == "about:blank":
                sleep(0.1)
            driver.close()
            break
        except IndexError:
            sleep(0.1)
    log.info(f"[{filename}.mp3] -> URL got and tab closed")
    log.info(f"URL of the .mp3: {mp3_url}")
    check_done += 1
    print(f"{Print.previous()}\r🎧{Print.purple}Création des audio :{Print.end} {Print.bold}({done}✅/{in_process}🔁/{waiting}⌛️){Print.end} {Print.blue}({get_percentage(check_done, checkpoints)}){Print.end}")

    # Downloading the mp3
    res = requests.get(mp3_url, timeout=10) # 10s max
    if not os.path.exists(BUILD):
        os.mkdir(BUILD)
    if not os.path.exists(TTS):
        os.mkdir(TTS)
    with open(os.path.join(TTS, f"{filename}.mp3"), "wb") as f:
        f.write(res.content)
    log.info(f"[{filename}.mp3] -> File downloaded at {os.path.join(TTS, f'{filename}.mp3')}")
    check_done += 1
    print(f"{Print.previous()}\r🎧{Print.purple}Création des audio :{Print.end} {Print.bold}({done}✅/{in_process}🔁/{waiting}⌛️){Print.end} {Print.blue}({get_percentage(check_done, checkpoints)}){Print.end}")

    driver.switch_to.window(driver.window_handles[0])

    while True:
        if (time() - start_time + (max_timeout // 3)) >= max_timeout: # (max_timeout // 3) == 10s
            return TIMEOUT
        try:
            more_button = driver.find_elements(By.CLASS_NAME, "header-menu-button")[0]
            more_button.click()
            break
        except IndexError:
            sleep(0.1)
    log.info(f"[{filename}.mp3] -> More button clicked")
    check_done += 1
    print(f"{Print.previous()}\r🎧{Print.purple}Création des audio :{Print.end} {Print.bold}({done}✅/{in_process}🔁/{waiting}⌛️){Print.end} {Print.blue}({get_percentage(check_done, checkpoints)}){Print.end}")

    while True:
        if (time() - start_time + (max_timeout // 3)) >= max_timeout:
            return TIMEOUT
        try:
            delete_button = driver.find_elements(By.CLASS_NAME, "text-gray-700")[4]
            delete_button.click()
            break
        except IndexError:
            sleep(0.1)
    log.info(f"[{filename}.mp3] -> Delete button clicked")
    check_done += 1
    print(f"{Print.previous()}\r🎧{Print.purple}Création des audio :{Print.end} {Print.bold}({done}✅/{in_process}🔁/{waiting}⌛️){Print.end} {Print.blue}({get_percentage(check_done, checkpoints)}){Print.end}")

    while True:
        if (time() - start_time + (max_timeout // 3)) >= max_timeout:
            return TIMEOUT
        try:
            confirm_delete = driver.find_elements(By.CLASS_NAME, "shadow-sm")[3]
            confirm_delete.click()
            break
        except IndexError:
            sleep(0.1)
    log.info(f"[{filename}.mp3] -> Confirm delete button clicked")
    check_done += 1
    print(f"{Print.previous()}\r🎧{Print.purple}Création des audio :{Print.end} {Print.bold}({done}✅/{in_process}🔁/{waiting}⌛️){Print.end} {Print.blue}({get_percentage(check_done, checkpoints)}){Print.end}")
    
    while True:
        if (time() - start_time + (max_timeout // 3)) >= max_timeout:
            return TIMEOUT
        try:
            driver.find_elements(By.CLASS_NAME, "go685806154")[0]
            break
        except IndexError:
            sleep(0.1)
    log.info(f"[{filename}.mp3] -> Delete confirmed button seen")
    check_done += 1
    in_process -= 1
    done += 1
    print(f"{Print.previous()}\r🎧{Print.purple}Création des audio :{Print.end} {Print.bold}({done}✅/{in_process}🔁/{waiting}⌛️){Print.end} {Print.blue}({get_percentage(check_done, checkpoints)}){Print.end}")

    driver.close()
    driver.quit()

if __name__ == "__main__":
    texts = ['I used to trauma dump on people when I was younger', 'Another month, another vent.', 'When I was younger, my coping method was to trauma dump to strangers in the toilet. During recess, instead of eating or hanging out with friends, I would rush to the toilet and wait for someone else to come in, then try to “make conversation” with them.', 'A normal “conversation” was basically just be trauma dumping on them and it usually sounded like:', 'Me: Hey! How are you? What class are you from?', 'Her: Uh….', 'Me: How’s life? Mine’s horrible!', 'Her: It’s fine….um…why is yours horrible?', 'Me: Well, yesterday my mom decided to punish me by making me climb up and down the stairs cos I had a sore throat and she was angry that I didn’t tell her about it earlier! Then my younger brother tried to help me and she caned him. My older brother sided with her and told her what she was doing was correct and stuff like that. I’ve never felt so fecking betrayed! I bet you like your life! Hahahah!', 'Her: I-Uh….my dad is the strict one but I still love him. I hope you love your mother too? Anyways, I got to go pee now..', 'Me: Oh yes of course! Sorry for bothering you! Byeee!', 'I only stopped when my mom found out cos someone I trauma dumped on told her mother about me and her mother knew my mother and told her that I called her a slut that she’s pregnant nearly every year.', 'Guess who couldn’t see the end of punishments till like a month later.', 'Thinking back I was so dumb. What do ya’ll think? Anyone can relate?']
    texts_to_tts(texts)
