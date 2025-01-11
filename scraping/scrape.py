from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from time import time
from tqdm import tqdm
import concurrent.futures
import random

from confidential import NETID, NETID_PASSWORD


CAESAR_LOGIN_URL = 'https://caesar.ent.northwestern.edu/psc/CS860PRD/EMPLOYEE/SA/c/NUI_FRAMEWORK.PT_LANDINGPAGE.GBL'

CSS_SELECTORS = {
    'netid_input_field': '#idToken1',
    'netid_password_input_field': '#idToken2',
    'log_in_button': '#content > div > form > fieldset > div:nth-child(5)',
    'no__other_people_use_this_device_button': '#dont-trust-browser-button',
    'manage_classes_button': r'#PTNUI_LAND_REC14\$0_row_8',
    'search_ctecs_button': r"[id^='win'][id$='divPTGP_STEPS_L1_row\$7']",
    'academic_career_dropdown': '#NW_CT_PB_SRCH_ACAD_CAREER',
    'academic_subject_dropdown': '#NW_CT_PB_SRCH_SUBJECT',
    'search_button': '#win0divNW_CT_PB_SRCH_SRCH_BTN',
    'first_course_button': r'#NW_CT_PV_DRV\$0_row_0',
    'course_buttons': r"[id^='NW_CT_PV_DRV\$0_row_']",
    'course_button': r'#NW_CT_PV_DRV\$0_row_',
    'first_ctec_button': r'#NW_CT_PV4_DRV\$0_row_0',
    'ctec_buttons': r"[id^='NW_CT_PV4_DRV\$0_row_']",
    'ctec_button': r'#NW_CT_PV4_DRV\$0_row_',
    'quarter': r'#MYDESCR2\$',
    'course': r'#MYDESCR\$',
    'professor': r'#CTEC_INSTRUCTOR\$',
    'back_arrow_button': '#win0hdrdivPT_WORK_PT_BUTTON_BACK > span'
}

LATEST_QUARTERS_WITH_CTECS_PUBLISHED = {
    'Spring': '2024 Spring',
    'Winter': '2024 Winter',
    'Fall': '2023 Fall'
}

NUMBER_OF_DRIVERS = 17
# NUMBER_OF_DRIVERS = 2


# academic_subjects_to_scrape = [
#     'AAL', 'AFST', 'AF_AM_ST', 'ALT_CERT', 'AMER_ST', 'AMES', 'ANIM_ART', 'ANTHRO', 'ARABIC', 'ART', 'ART_HIST', 'ASIAN_AM', 'ASIAN_LC', 'ASIAN_ST', 
#     'ASTRON', 'BIOL_SCI', 'BLK_ST', 'BMD_ENG', 'BUS_INST', 'CAT', 'CFS', 'CHEM', 'CHEM_ENG', 'CHINESE', 'CHRCH_MU', 'CIV_ENG', 'CIV_ENV', 'CLASSICS', 
#     'CMN', 'COG_SCI', 'COMM_SCI', 'COMM_ST', 'COMP_ENG', 'COMP_LIT', 'COMP_SCI', 'CONDUCT', 'COOP', 'CRDV', 'CSD', 'DANCE', 'DATA_ENG', 'DSGN', 'EARTH', 
#     'ECE', 'ECON', 'EDIT', 'EECS', 'ELEC_ENG', 'ENGLISH', 'ENTREP', 'ENVR_POL', 'ENVR_SCI', 'EPICS', 'ES_APPM', 'EUR_ST', 'EUR_TH', 'FRENCH', 'GBL_HLTH', 
#     'GEN_CMN', 'GEN_ENG', 'GEN_LA', 'GEN_MUS', 'GEN_SPCH', 'GEOG', 'GEOL_SCI', 'GERMAN', 'GNDR_ST', 'GREEK', 'HDC', 'HDPS', 'HEBREW', 'HINDI', 'HIND_URD', 
#     'HISTORY', 'HUM', 'IDEA', 'IEMS', 'IMC', 'INTG_ART', 'INTG_SCI', 'INTL_ST', 'ISEN', 'ITALIAN', 'JAPANESE', 'JAZZ_ST', 'JOUR', 'JWSH_ST', 'KELLG_CP', 
#     'KELLG_FE', 'KELLG_MA', 'KOREAN', 'LATIN', 'LATINO', 'LATIN_AM', 'LDRSHP', 'LEGAL_ST', 'LING', 'LOC', 'LRN_DIS', 'LRN_SCI', 'MATH', 'MAT_SCI', 'MECH_ENG', 
#     'MENA', 'MFG_ENG', 'MMSS', 'MUSIC', 'MUSICOL', 'MUSIC_ED', 'MUS_COMP', 'MUS_TECH', 'MUS_THRY', 'NEUROSCI', 'NICO', 'PERF_ST', 'PERSIAN', 'PHIL', 'PHYSICS', 
#     'PIANO', 'POLISH', 'POLI_SCI', 'PORT', 'PRDV', 'PSYCH', 'RELIGION', 'RTVF', 'RUSSIAN', 'SESP', 'SHC', 'SLAVIC', 'SOCIOL', 'SOC_POL', 'SPANISH', 'SPCH', 
#     'STAT', 'STRINGS', 'SWAHILI', 'TEACH_ED', 'THEATRE', 'TRANS', 'TURKISH', 'URBAN_ST', 'VOICE', 'WIND_PER', 'WM_ST', 'WRITING', 'YIDDISH'
# ]
academic_subjects_to_scrape = [
    'MATH', 'COMP_SCI', 'GEN_ENG', 'IEMS', 'ELEC_ENG', 'STAT', 'COG_SCI', 'COMP_ENG', 'MECH_ENG', 'ES_APPM', 'BIOL_SCI', 'CHEM', 
    'PHYSICS', 'CHEM_ENG', 'CIV_ENV', 'ASTRON', 'EARTH', 'CSD', 'PSYCH', 'DSGN', 'ENGLISH', 'COMM_ST', 'PERF_ST', 
    'BMD_ENG', 'BUS_INST', 'GEOG', 'MMSS', 'PRDV', 'TEACH_ED', 'TRANS', 'ECON', 'KELLG_FE', 'KELLG_MA', 'LING'
] # 34


def driver_scrape(academic_subjects):
    
    # Initialize driver:
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install())) # Open Google Chrome
    driver.maximize_window() # Maximize the window

    def wait_for_page_to_load(page):
        WebDriverWait(driver, 10000).until(EC.text_to_be_present_in_element_attribute((By.CSS_SELECTOR, '#pt_pageinfo'), 'page', page))

    def wait_for_loading():
        WebDriverWait(driver, 10000).until(EC.text_to_be_present_in_element_attribute((By.CSS_SELECTOR, 'body'), 'style', 'pointer-events: none;'))
        WebDriverWait(driver, 10000).until_not(EC.text_to_be_present_in_element_attribute((By.CSS_SELECTOR, 'body'), 'style', 'pointer-events: none;'))

    def click_element(css_selector):
        WebDriverWait(driver, 10000).until(EC.element_to_be_clickable((By.CSS_SELECTOR, css_selector))).click()

    def enter_text_into_input_element(css_selector, text):
        WebDriverWait(driver, 10000).until(EC.element_to_be_clickable((By.CSS_SELECTOR, css_selector))).send_keys(text)

    def select_option_in_dropdown(css_selector, value):
        Select(WebDriverWait(driver, 10000).until(EC.element_to_be_clickable((By.CSS_SELECTOR, css_selector)))).select_by_value(value)
    
    def wait(seconds):
        # Not using time.sleep() because it crashes the concurrent process
        try:
            WebDriverWait(driver, seconds).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'idnfienf9f13f943nf1349nzfeufneufndfndkfd432')))
        except TimeoutException:
            pass

    def stop(): # for debugging
        wait(1e6)

    # Log in to CAESAR:
    driver.get(CAESAR_LOGIN_URL) # Fetch CAESAR login URL
    enter_text_into_input_element(CSS_SELECTORS['netid_input_field'], NETID) # Enter NetID
    enter_text_into_input_element(CSS_SELECTORS['netid_password_input_field'], NETID_PASSWORD) # Enter NetID password
    click_element(CSS_SELECTORS['log_in_button']) # Click 'LOG IN' button
    click_element(CSS_SELECTORS['no__other_people_use_this_device_button']) # Wait for Duo authentication, then click 'No, other people use this device.' button

    wait(11 * (NUMBER_OF_DRIVERS - 1)) # This is to give time to allow the user to authenticate the Duos for other drivers before it starts going and taking over their computer.

    # Navigate to CTEC search section:
    click_element(CSS_SELECTORS['manage_classes_button']) # Click 'Manage Classes' button
    wait_for_page_to_load('NW_VIEW_MY_CLS_FL') # Wait for loading
    click_element(CSS_SELECTORS['search_ctecs_button']) # Click 'Search CTECs' button

    # Scrape CTECS:
    for i in range(len(academic_subjects)):

        wait_for_page_to_load('NW_CTEC_SRCH_FL') # Wait for loading

        select_option_in_dropdown(CSS_SELECTORS['academic_career_dropdown'], 'UGRD')
        # wait_for_loading()
        wait(2)

        select_option_in_dropdown(CSS_SELECTORS['academic_subject_dropdown'], academic_subjects[i])
        # wait_for_loading()
        wait(2)

        click_element(CSS_SELECTORS['search_button'])
        wait_for_page_to_load('NW_CTEC_RSLT1_FL')

        # Make sure there are any courses:
        try:
            WebDriverWait(driver, 60).until(EC.element_to_be_clickable((By.CSS_SELECTOR, CSS_SELECTORS['first_course_button']))).click()
        except TimeoutException:
            click_element(CSS_SELECTORS['search_ctecs_button'])
            continue

        wait_for_page_to_load('NW_CTEC_RSLT2_FL')

        for j in range(len(WebDriverWait(driver, 10000).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, CSS_SELECTORS['course_buttons']))))):
            
            if j:
                click_element(rf"{CSS_SELECTORS['course_button']}{j}")
                wait_for_loading()
            
            # Make sure there are any CTECs:
            try:
                WebDriverWait(driver, 60).until(EC.element_to_be_clickable((By.CSS_SELECTOR, CSS_SELECTORS['first_ctec_button'])))
            except TimeoutException:
                print(f'No CTECs found for {academic_subjects[i]} course')
                continue

            for k in range(len(WebDriverWait(driver, 10000).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, CSS_SELECTORS['ctec_buttons']))))):
                
                quarter = WebDriverWait(driver, 10000).until(EC.presence_of_element_located((By.CSS_SELECTOR, rf'{CSS_SELECTORS['quarter']}{k}'))).get_attribute('innerHTML')
                
                if quarter in LATEST_QUARTERS_WITH_CTECS_PUBLISHED.values():

                    course = WebDriverWait(driver, 10000).until(EC.presence_of_element_located((By.CSS_SELECTOR, rf'{CSS_SELECTORS['course']}{k}'))).get_attribute('innerHTML')

                    professor = WebDriverWait(driver, 10000).until(EC.presence_of_element_located((By.CSS_SELECTOR, rf'{CSS_SELECTORS['professor']}{k}'))).get_attribute('innerHTML')

                    click_element(rf"{CSS_SELECTORS['ctec_button']}{k}")
                    
                    WebDriverWait(driver, 10000).until(EC.number_of_windows_to_be(2))
                    driver.switch_to.window(driver.window_handles[1])

                    WebDriverWait(driver, 10000).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div'))) # Wait for the CTEC content to load

                    with open(f"data/raw/%{quarter.replace(' ', '$')}%{course.replace(' ', '$')}%{professor.replace(' ', '$')}%.html", "w", encoding="utf-8") as file:
                        file.write(driver.page_source)

                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])
        
        if i != len(academic_subjects) - 1:
            click_element(CSS_SELECTORS['back_arrow_button'])
        else:
            driver.quit()


def get_drivers_academic_subjects(number_of_drivers, academic_subjects):
    res = [[] for i in range(NUMBER_OF_DRIVERS)]
    while True:
        for driver_academic_subjects in res:
            if not academic_subjects:
                return res
            driver_academic_subjects.append(academic_subjects.pop(random.randint(0, len(academic_subjects) - 1)))


if __name__ == '__main__':

    drivers_academic_subjects = get_drivers_academic_subjects(NUMBER_OF_DRIVERS, academic_subjects_to_scrape)

    start_time = time()

    with concurrent.futures.ProcessPoolExecutor(max_workers=NUMBER_OF_DRIVERS) as executor:
        executor.map(driver_scrape, drivers_academic_subjects)

    print(f"Scraping completed in {(time() - start_time):.0f} seconds.")
