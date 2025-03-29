from dotenv import load_dotenv
import os
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from time import time
from concurrent.futures import ThreadPoolExecutor
from random import randint
import shutil


CSS_SELECTORS = {
    "netid_input_field": "#idToken1",
    "netid_password_input_field": "#idToken2",
    "log_in_button": "#loginButton_0",
    "no__other_people_use_this_device_button": "#dont-trust-browser-button",
    "manage_classes_button": r"#PTNUI_LAND_REC14\$0_row_8",
    "search_ctecs_button": r"[id^='win'][id$='div\$ICField\$11\$\$7']",
    "academic_career_dropdown": "#NW_CT_PB_SRCH_ACAD_CAREER",
    "academic_subject_dropdown": "#NW_CT_PB_SRCH_SUBJECT",
    "search_button": r"#NW_CT_PB_SRCH_SRCH_BTN\$span",
    "first_course_button": r"#NW_CT_PV_DRV\$0_row_0",
    "course_buttons": r"[id^='NW_CT_PV_DRV\$0_row_']",
    "course_button": r"#NW_CT_PV_DRV\$0_row_",
    "ctec_buttons": r"[id^='NW_CT_PV4_DRV\$0_row_']",
    "ctec_button": r"#NW_CT_PV4_DRV\$0_row_",
    "back_arrow_button": "#PT_WORK_PT_BUTTON_BACK"
}

PAGES = {
    "view_my_class_schedule": "NW_TERM_STA1_FL",
    "search_ctecs": "NW_CTEC_SRCH_FL",
    "search_ctecs_results_by_course": "NW_CTEC_RSLT1_FL",
    "search_results": "NW_CTEC_RSLT2_FL"
}

CHROMEDRIVER_PATH = "/opt/homebrew/bin/chromedriver"

UNDERGRADUATE_ACADEMIC_CAREER_DROPDOWN_INDEX = 15

MIN_UNDERGRADUATE_ACADEMIC_SUBJECT_DROPDOWN_INDEX = 1
MAX_UNDERGRADUATE_ACADEMIC_SUBJECT_DROPDOWN_INDEX = 147

PATH_TO_RAW_DATA_FOLDER = "data/raw"

GARBAGE_CSS_SELECTOR = "#snjfsdfndjkf"

CAESAR_LOGIN_URL = "https://caesar.ent.northwestern.edu/psc/CS860PRD/EMPLOYEE/SA/c/NUI_FRAMEWORK.PT_LANDINGPAGE.GBL"

LONGEST_WAIT = float("inf")

NUM_WORKERS = 12

SECONDS_NEEDED_TO_AUTHENTICATE_WORKER = 12
SECONDS_NEEDED_TO_AUTHENTICATE_ALL_OTHER_WORKERS = SECONDS_NEEDED_TO_AUTHENTICATE_WORKER * (NUM_WORKERS - 1)

load_dotenv()
NETID, NETID_PASSWORD = os.getenv("NETID"), os.getenv("NETID_PASSWORD")


def wait_for_loading(driver):
    WebDriverWait(driver, LONGEST_WAIT).until(EC.text_to_be_present_in_element_attribute((By.CSS_SELECTOR, "body"), "style", "pointer-events: none;"))
    WebDriverWait(driver, LONGEST_WAIT).until_not(EC.text_to_be_present_in_element_attribute((By.CSS_SELECTOR, "body"), "style", "pointer-events: none;"))

def wait_for_page_to_load(driver, page):
    WebDriverWait(driver, LONGEST_WAIT).until(EC.text_to_be_present_in_element_attribute((By.CSS_SELECTOR, "#pt_pageinfo"), "page", page))

def get_academic_subject(driver, academic_subject_index):
    return WebDriverWait(driver, LONGEST_WAIT).until(EC.presence_of_element_located((By.CSS_SELECTOR, f"#NW_CT_PB_SRCH_SUBJECT > option:nth-child({academic_subject_index + 1})"))).get_attribute("value")

def get_course_number(driver, course_index):
    res = WebDriverWait(driver, LONGEST_WAIT).until(EC.presence_of_element_located((By.CSS_SELECTOR, rf"#MYLABEL\${course_index}"))).get_attribute("innerHTML")
    return res[:res.index(':')]

def get_ctec_quarter(driver, ctec_index):
    return WebDriverWait(driver, LONGEST_WAIT).until(EC.presence_of_element_located((By.CSS_SELECTOR, rf"#MYDESCR2\${ctec_index}"))).get_attribute("innerHTML")

def wait(driver, num_seconds):
    # Not using time.sleep() because it crashes the concurrent process
    try:
        WebDriverWait(driver, num_seconds).until(EC.presence_of_element_located((By.CSS_SELECTOR, GARBAGE_CSS_SELECTOR)))
    except:
        pass

def wait_for_authentication_of_other_workers(driver):
    wait(driver, SECONDS_NEEDED_TO_AUTHENTICATE_ALL_OTHER_WORKERS)

def click_element(driver, css_selector):
    WebDriverWait(driver, LONGEST_WAIT).until(EC.element_to_be_clickable((By.CSS_SELECTOR, css_selector))).click()

def enter_text_into_input_element(driver, css_selector, text):
    WebDriverWait(driver, LONGEST_WAIT).until(EC.element_to_be_clickable((By.CSS_SELECTOR, css_selector))).send_keys(text)

def select_option_in_dropdown(driver, css_selector, index):
    Select(WebDriverWait(driver, LONGEST_WAIT).until(EC.element_to_be_clickable((By.CSS_SELECTOR, css_selector)))).select_by_index(index)

def stop(driver): # for debugging
    wait(driver, LONGEST_WAIT)

def get_most_recent_quarter_with_ctecs_published(driver, num_ctecs):
    res = ""
    res_numerical = float("-inf")
    for ctec_index in range(num_ctecs):
        quarter = get_ctec_quarter(driver, ctec_index)
        if quarter[5:7] == "Su":
            continue
        quarter_numerical = int(quarter[:4])
        if quarter[5] == 'S':
            quarter_numerical += 0.1
        elif quarter[5] == 'F':
            quarter_numerical += 0.2
        if quarter_numerical > res_numerical:
            res_numerical = quarter_numerical
            res = quarter
    return res


def scrape_academic_subject(driver, academic_subject_index):

    wait_for_page_to_load(driver, PAGES["search_ctecs"])

    select_option_in_dropdown(driver, CSS_SELECTORS["academic_career_dropdown"], UNDERGRADUATE_ACADEMIC_CAREER_DROPDOWN_INDEX)
    # wait_for_loading(driver)
    wait(driver, 5)

    academic_subject = get_academic_subject(driver, academic_subject_index)

    select_option_in_dropdown(driver, CSS_SELECTORS["academic_subject_dropdown"], academic_subject_index)
    # wait_for_loading(driver)
    wait(driver, 5)

    click_element(driver, CSS_SELECTORS["search_button"])

    wait_for_page_to_load(driver, PAGES["search_ctecs_results_by_course"])

    # Make sure there are any courses:
    try:
        WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.CSS_SELECTOR, CSS_SELECTORS["first_course_button"]))).click()
    except:
        click_element(driver, CSS_SELECTORS["search_ctecs_button"])
        wait(driver, 5)
        return

    wait_for_page_to_load(driver, PAGES["search_results"])

    num_courses = len(WebDriverWait(driver, LONGEST_WAIT).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, CSS_SELECTORS["course_buttons"]))))

    for course_index in range(num_courses):
        
        if course_index != 0:
            click_element(driver, rf"{CSS_SELECTORS['course_button']}{course_index}")
            wait_for_loading(driver)
        
        course_number = get_course_number(driver, course_index)
        
        # Make sure there are any CTECs:
        try:
            num_ctecs = len(WebDriverWait(driver, 5).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, CSS_SELECTORS["ctec_buttons"]))))
        except:
            continue
        
        most_recent_quarter_with_ctecs_published = get_most_recent_quarter_with_ctecs_published(driver, num_ctecs)

        if most_recent_quarter_with_ctecs_published != "":

            for ctec_index in range(num_ctecs):

                quarter = get_ctec_quarter(driver, ctec_index)
                
                if quarter == most_recent_quarter_with_ctecs_published:

                    click_element(driver, rf"{CSS_SELECTORS['ctec_button']}{ctec_index}")
                    
                    WebDriverWait(driver, LONGEST_WAIT).until(EC.number_of_windows_to_be(2))
                    driver.switch_to.window(driver.window_handles[1])

                    try:
                        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div"))) # Wait for the CTEC content to load
                        with open(f"data/raw/%{academic_subject}%{course_number}%{quarter.replace(' ', '$')}%{ctec_index}.html", "w", encoding="utf-8") as file:
                            file.write(driver.page_source)
                            
                    except:
                        pass

                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])
    
    click_element(driver, CSS_SELECTORS["back_arrow_button"])


def scrape_academic_subjects(driver, academic_subjects_indices):
    for academic_subject_index in academic_subjects_indices:
        scrape_academic_subject(driver, academic_subject_index)
    driver.quit()

def init_driver():
    res = Chrome(service=Service(CHROMEDRIVER_PATH))
    res.maximize_window()
    return res

def navigate_to_search_ctecs(driver):
    driver.get(CAESAR_LOGIN_URL)
    enter_text_into_input_element(driver, CSS_SELECTORS["netid_input_field"], NETID)
    enter_text_into_input_element(driver, CSS_SELECTORS["netid_password_input_field"], NETID_PASSWORD)
    click_element(driver, CSS_SELECTORS["log_in_button"])
    click_element(driver, CSS_SELECTORS["no__other_people_use_this_device_button"])
    wait_for_authentication_of_other_workers(driver)
    click_element(driver, CSS_SELECTORS["manage_classes_button"])
    wait_for_page_to_load(driver, PAGES["view_my_class_schedule"])
    click_element(driver, CSS_SELECTORS["search_ctecs_button"])
    wait(driver, 5)

def worker(academic_subjects_indices):
    driver = init_driver()
    navigate_to_search_ctecs(driver)
    scrape_academic_subjects(driver, academic_subjects_indices)

def get_workers_undergraduate_academic_subjects_dropdown_indices():
    res = [[] for i in range(NUM_WORKERS)]
    undergraduate_academic_subjects_dropdown_indices = list(range(MIN_UNDERGRADUATE_ACADEMIC_SUBJECT_DROPDOWN_INDEX, MAX_UNDERGRADUATE_ACADEMIC_SUBJECT_DROPDOWN_INDEX + 1))
    while True:
        for i in range(len(res)):
            if len(undergraduate_academic_subjects_dropdown_indices) == 0:
                return res
            res[i].append(undergraduate_academic_subjects_dropdown_indices.pop(randint(0, len(undergraduate_academic_subjects_dropdown_indices) - 1)))

def clear_raw_data_folder():
    if os.path.exists(PATH_TO_RAW_DATA_FOLDER):
        shutil.rmtree(PATH_TO_RAW_DATA_FOLDER)
    os.makedirs(PATH_TO_RAW_DATA_FOLDER)


if __name__ == "__main__":

    workers_undergraduate_academic_subjects_dropdown_indices = get_workers_undergraduate_academic_subjects_dropdown_indices()

    clear_raw_data_folder()

    start_time = time()

    with ThreadPoolExecutor(max_workers=len(workers_undergraduate_academic_subjects_dropdown_indices)) as executor:
        executor.map(worker, workers_undergraduate_academic_subjects_dropdown_indices)
    # worker(workers_undergraduate_academic_subjects_dropdown_indices[randint(0, len(workers_undergraduate_academic_subjects_dropdown_indices) - 1)]) # for testing

    print(f"Scraping completed in {((time() - start_time) / 60):.1f} minutes.")
