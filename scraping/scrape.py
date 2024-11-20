from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from confidential import MY_NETID_PASSWORD
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException
import json

import time
# from pprint import pprint

MY_NETID = 'xzy2201'

CAESAR_LOGIN_URL = 'https://caesar.ent.northwestern.edu/psc/CS860PRD/EMPLOYEE/SA/c/NUI_FRAMEWORK.PT_LANDINGPAGE.GBL'

CSS_SELECTORS = {
    'netid_input_field': '#idToken1',
    'password_input_field': '#idToken2',
    'log_in_button': '#content > div > form > fieldset > div:nth-child(5)',
    'no__other_people_use_this_device_button': '#dont-trust-browser-button',
    'manage_classes_button': r'#PTNUI_LAND_REC14\$0_row_8',
    'search_ctecs_button': r'#win5div\$ICField\$11\$\$7',
    'academic_career_dropdown': '#NW_CT_PB_SRCH_ACAD_CAREER', 
    'first_academic_subject_dropdown_option': '#NW_CT_PB_SRCH_SUBJECT > option:nth-child(2)',
    'academic_subject_dropdown': '#NW_CT_PB_SRCH_SUBJECT',
    'search_button': '#win0divNW_CT_PB_SRCH_SRCH_BTN',
    'course_button': r'#NW_CT_PV_DRV\$0_row_',
    'ctec_button': r'#NW_CT_PV4_DRV\$0_row_',
    'term': r'#MYDESCR2\$',
    'rating_table': "[id^='BlockLayoutController'][id*='_BaseReportBlockUCPreview_TableStat_'] > tbody",
    'course_rating_average': "tr.CondensedTabularEvenRows > td",
    'course_rating_student_count': "tr.CondensedTabularOddRows > td",
    'student_opinion': "[id^='BlockLayoutController'][id*='_BaseReportBlockUCPreview_CommentBoxbac5fa25-de6b-4010-bf3d-3e511cb8d63dReportSummary_'] > tbody > tr > td",
    'table': "[id^='BlockLayoutController'][id*='_BaseReportBlockUCPreview_TableFrequency_'] > tbody",
    'number_of_weinberg_students': 'tr:nth-child(10) > td:nth-child(2)',
    'number_of_mccormick_students': 'tr:nth-child(5) > td:nth-child(2)',
    'number_of_medill_students': 'tr:nth-child(6) > td:nth-child(2)',
    'number_of_comm_students': 'tr:nth-child(2) > td:nth-child(2)',
    'number_of_sesp_students': 'tr:nth-child(1) > td:nth-child(2)',
    'number_of_bienen_students': 'tr:nth-child(7) > td:nth-child(2)',
    'number_of_freshmen': 'tr:nth-child(1) > td:nth-child(2)',
    'number_of_sophomores': 'tr:nth-child(2) > td:nth-child(2)',
    'number_of_juniors': 'tr:nth-child(3) > td:nth-child(2)',
    'number_of_seniors': 'tr:nth-child(4) > td:nth-child(2)',

    'back_arrow_button': '#win0hdrdivPT_WORK_PT_BUTTON_BACK > span'

    # 'course_button': r'#MYLABEL\$',
    # 'ctecs': r"[id^='NW_CT_PV4_DRV\$0_row_']",
    # 'ctec': r'#NW_CT_PV4_DRV\$0_row_',
    # 'term_container': r'#MYDESCR2\$',
    # 'undergraduate_school_demographics_image': "[id^='report_'] > div:nth-child(12) > div.report-block > div.FrequencyBlockRow > div > div.FrequencyBlock_chart > img",
    # 'class_demographics_image': "[id^='report_'] > div:nth-child(13) > div.FrequencyBlockRow > div > div.FrequencyBlock_chart > img"
}

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
results = {}

def scrape():
    driver.maximize_window()
    driver.get(CAESAR_LOGIN_URL)
    WebDriverWait(driver, 10000).until(EC.presence_of_element_located((By.CSS_SELECTOR, CSS_SELECTORS['netid_input_field']))).send_keys(MY_NETID)
    driver.find_element(By.CSS_SELECTOR, CSS_SELECTORS['password_input_field']).send_keys(MY_NETID_PASSWORD)
    driver.find_element(By.CSS_SELECTOR, CSS_SELECTORS['log_in_button']).click()
    WebDriverWait(driver, 10000).until(EC.element_to_be_clickable((By.CSS_SELECTOR, CSS_SELECTORS['no__other_people_use_this_device_button']))).click()
    WebDriverWait(driver, 10000).until(EC.element_to_be_clickable((By.CSS_SELECTOR, CSS_SELECTORS['manage_classes_button']))).click()
    wait_for_loading()
    driver.find_element(By.CSS_SELECTOR, CSS_SELECTORS['search_ctecs_button']).click()

    for academic_subject in ['COMP_SCI']:

        wait_for_loading()
        Select(driver.find_element(By.CSS_SELECTOR, CSS_SELECTORS['academic_career_dropdown'])).select_by_visible_text('Undergraduate')
        wait_for_loading()

        Select(driver.find_element(By.CSS_SELECTOR, CSS_SELECTORS['academic_subject_dropdown'])).select_by_value(academic_subject)
        wait_for_loading()
        driver.find_element(By.CSS_SELECTOR, CSS_SELECTORS['search_button']).click()
        wait_for_loading()
        driver.find_element(By.CSS_SELECTOR, f'{CSS_SELECTORS['course_button']}0').click()

        for i in range(len(driver.find_elements(By.CSS_SELECTOR, f"[id^='{CSS_SELECTORS['course_button'][1:]}']"))):
            try:
                WebDriverWait(driver, 90).until(EC.element_to_be_clickable((By.CSS_SELECTOR, f'{CSS_SELECTORS['ctec_button']}0')))
            except TimeoutException:
                continue
            course_name = f'{academic_subject} {driver.find_element(By.CSS_SELECTOR, rf'#MYLABEL\${i}').get_attribute('innerHTML')}'
            course_name = course_name[:course_name.index(':')]
            driver.find_element(By.CSS_SELECTOR, f'{CSS_SELECTORS['course_button']}{i}').click()
            wait_for_loading()
            for j in range(len(driver.find_elements(By.CSS_SELECTOR, f"[id^='{CSS_SELECTORS['ctec_button'][1:]}']"))):
                term = driver.find_element(By.CSS_SELECTOR, f'{CSS_SELECTORS['term']}{j}').get_attribute('innerHTML')
                if term in {'2023 Fall', '2024 Winter', '2024 Spring'}:
                    driver.find_element(By.CSS_SELECTOR, f'{CSS_SELECTORS['ctec_button']}{j}').click()
                    WebDriverWait(driver, 10000).until(EC.number_of_windows_to_be(2))
                    driver.switch_to.window(driver.window_handles[1])
                    WebDriverWait(driver, 10000).until(EC.presence_of_element_located((By.CSS_SELECTOR, CSS_SELECTORS['rating_table'])))
                    extract_info_from_ctec(academic_subject, course_name, term)
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])
        
        WebDriverWait(driver, 10000).until(EC.element_to_be_clickable((By.CSS_SELECTOR, CSS_SELECTORS['back_arrow_button']))).click()

    
    time.sleep(1e6)


def wait_for_loading():
    WebDriverWait(driver, 10000).until(EC.text_to_be_present_in_element_attribute((By.CSS_SELECTOR, 'body'), 'style', 'pointer-events: none;'))
    WebDriverWait(driver, 10000).until_not(EC.text_to_be_present_in_element_attribute((By.CSS_SELECTOR, 'body'), 'style', 'pointer-events: none;'))


def extract_info_from_ctec(academic_subject, course_name, term):
    course_rating_table = driver.find_elements(By.CSS_SELECTOR, CSS_SELECTORS['rating_table'])[1]
    course_rating_average = float(course_rating_table.find_element(By.CSS_SELECTOR, CSS_SELECTORS['course_rating_average']).get_attribute('innerHTML'))
    course_rating_student_count = int(course_rating_table.find_element(By.CSS_SELECTOR, CSS_SELECTORS['course_rating_student_count']).get_attribute('innerHTML'))
    student_opinions = {}
    student_opinion_index = 0
    for student_opinion in driver.find_elements(By.CSS_SELECTOR, CSS_SELECTORS['student_opinion']):
        student_opinions[student_opinion_index] = student_opinion.get_attribute('innerHTML')
        student_opinion_index += 1
    tables = driver.find_elements(By.CSS_SELECTOR, CSS_SELECTORS['table'])
    school_demographic_info_table = tables[1]
    number_of_weinberg_students = int(school_demographic_info_table.find_element(By.CSS_SELECTOR, CSS_SELECTORS['number_of_weinberg_students']).get_attribute('innerHTML'))
    number_of_mccormick_students = int(school_demographic_info_table.find_element(By.CSS_SELECTOR, CSS_SELECTORS['number_of_mccormick_students']).get_attribute('innerHTML'))
    number_of_medill_students = int(school_demographic_info_table.find_element(By.CSS_SELECTOR, CSS_SELECTORS['number_of_medill_students']).get_attribute('innerHTML'))
    number_of_comm_students = int(school_demographic_info_table.find_element(By.CSS_SELECTOR, CSS_SELECTORS['number_of_comm_students']).get_attribute('innerHTML'))
    number_of_sesp_students = int(school_demographic_info_table.find_element(By.CSS_SELECTOR, CSS_SELECTORS['number_of_sesp_students']).get_attribute('innerHTML'))
    number_of_bienen_students = int(school_demographic_info_table.find_element(By.CSS_SELECTOR, CSS_SELECTORS['number_of_bienen_students']).get_attribute('innerHTML'))
    class_demographic_info_table = tables[2]
    number_of_freshmen = int(class_demographic_info_table.find_element(By.CSS_SELECTOR, CSS_SELECTORS['number_of_freshmen']).get_attribute('innerHTML'))
    number_of_sophomores = int(class_demographic_info_table.find_element(By.CSS_SELECTOR, CSS_SELECTORS['number_of_sophomores']).get_attribute('innerHTML'))
    number_of_juniors = int(class_demographic_info_table.find_element(By.CSS_SELECTOR, CSS_SELECTORS['number_of_juniors']).get_attribute('innerHTML'))
    number_of_seniors = int(class_demographic_info_table.find_element(By.CSS_SELECTOR, CSS_SELECTORS['number_of_seniors']).get_attribute('innerHTML'))

    cur_ctec = {
        'course_rating': {
            'average': course_rating_average,
            'student_count': course_rating_student_count
        },
        'student_opinions': student_opinions,
        'school_demographics': {
            'Weinberg': number_of_weinberg_students,
            'McCormick': number_of_mccormick_students,
            'Medill': number_of_medill_students,
            'Comm': number_of_comm_students,
            'SESP': number_of_sesp_students,
            'Bienen': number_of_bienen_students
        },
        'class_demographics': {
            'Freshmen': number_of_freshmen,
            'Sophomores': number_of_sophomores,
            'Juniors': number_of_juniors,
            'Seniors': number_of_seniors
        }
    }

    if academic_subject not in results:
        results[academic_subject] = {
            course_name: {
                term: cur_ctec
            }
        }
    elif course_name not in results[academic_subject]:
        results[academic_subject][course_name] = {
            term: cur_ctec
        }
    elif term not in results[academic_subject][course_name]:
        results[academic_subject][course_name][term] = cur_ctec
    else:
        existing_cumulative_ctec = results[academic_subject][course_name][term]
        if cur_ctec['course_rating'] != existing_cumulative_ctec['course_rating']:
            existing_cumulative_ctec['course_rating']['average'] = (existing_cumulative_ctec['course_rating']['average'] * existing_cumulative_ctec['course_rating']['student_count'] + cur_ctec['course_rating']['average'] * cur_ctec['course_rating']['student_count']) / (existing_cumulative_ctec['course_rating']['student_count'] + cur_ctec['course_rating']['student_count'])
            existing_cumulative_ctec['course_rating']['student_count'] += cur_ctec['course_rating']['student_count']
        if cur_ctec['student_opinions'] != existing_cumulative_ctec['student_opinions']:
            number_of_existing_student_opinions = len(existing_cumulative_ctec['student_opinions'])
            for i in range(len(cur_ctec['student_opinions'])):
                existing_cumulative_ctec['student_opinions'][number_of_existing_student_opinions + i] = cur_ctec['student_opinions'][i]
        for demographics in {'school_demographics', 'class_demographics'}:
            if cur_ctec[demographics] != existing_cumulative_ctec[demographics]:
                for demographic in existing_cumulative_ctec[demographics]:
                    existing_cumulative_ctec[demographics][demographic] += cur_ctec[demographics][demographic]

    with open('data/data.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=4)






scrape()













def change_academic_subject_and_enter_into_those_ctecs(new_academic_subject):
    # Locate the back arrow button
    back_arrow_button = WebDriverWait(driver, 10000).until(EC.element_to_be_clickable((By.CSS_SELECTOR, CSS_SELECTORS['back_arrow_button'])))
    # Click the back arrow button button
    back_arrow_button.click()
    # Enter into the CTECs for the new academic subject
    enter_into_ctecs_for_academic_subject(new_academic_subject)

def scrape_ctecs_for_course(academic_subject, course_number):
    course_name = academic_subject + ' ' + course_number
    x = WebDriverWait(driver, 10000).until(EC.text_to_be_present_in_element_attribute((By.CSS_SELECTOR, r'#MYDESCR\$0'), 'innerHTML', course_number))
    # Count the number of CTECs for this particular course
    number_of_ctecs = len(WebDriverWait(driver, 10000).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, CSS_SELECTORS['ctecs']))))
    for i in range(number_of_ctecs):
        # Locate the term container
        term_container = WebDriverWait(driver, 10000).until(EC.element_to_be_clickable((By.CSS_SELECTOR, CSS_SELECTORS['term_container'] + str(i))))
        term = term_container.get_attribute('innerHTML')
        # If the term of the CTEC is one of the recent variety
        if term in ['2023 Fall', '2024 Winter', '2024 Spring']:
            # Click the CTEC button
            term_container.click()
            # Wait 1 second for the CTEC to open in a separate tab
            time.sleep(0.5)
            # Switch the active tab to the newly opened CTEC tab
            driver.switch_to.window(driver.window_handles[1])
            # Get the course rating
            course_rating = float(WebDriverWait(driver, 10000).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, CSS_SELECTORS['course_rating_container'])))[1].get_attribute('innerHTML'))
            # # Get the number of undergradute school students that are McCormick
            
            undergraduate_school_demographics_image_url = driver.find_element(By.CSS_SELECTOR, CSS_SELECTORS['undergraduate_school_demographics_image']).get_attribute('src')
            text_from_undergraduate_school_demographics_image = pytesseract.image_to_string(Image.open(BytesIO(requests.get(undergraduate_school_demographics_image_url).content)))
            index_of_mccormick = text_from_undergraduate_school_demographics_image.index('McCormick')
            number_of_undergraduate_students_that_are_mccormick = int(text_from_undergraduate_school_demographics_image[text_from_undergraduate_school_demographics_image.index('(', index_of_mccormick) + 1 : text_from_undergraduate_school_demographics_image.index(')', index_of_mccormick)])
            index_of_total = text_from_undergraduate_school_demographics_image.index('Total')
            total_number_of_undergraduate_students = int(text_from_undergraduate_school_demographics_image[text_from_undergraduate_school_demographics_image.index('(', index_of_total) + 1 : text_from_undergraduate_school_demographics_image.index(')', index_of_total)])
            
            class_demographics_image_url = driver.find_element(By.CSS_SELECTOR, CSS_SELECTORS['class_demographics_image']).get_attribute('src')
            text_from_class_demographics_image = pytesseract.image_to_string(Image.open(BytesIO(requests.get(class_demographics_image_url).content)))
            index_of_sophomore = text_from_class_demographics_image.index('Sophomore')
            number_of_class_students_that_are_sophomores = int(text_from_class_demographics_image[text_from_class_demographics_image.index('(', index_of_sophomore) + 1 : text_from_class_demographics_image.index(')', index_of_sophomore)])
            index_of_total = text_from_class_demographics_image.index('Total')
            total_number_of_class_students = int(text_from_class_demographics_image[text_from_class_demographics_image.index('(', index_of_total) + 1 : text_from_class_demographics_image.index(')', index_of_total)])
            
            driver.close()
            cursor.execute('''
                INSERT INTO CTECs (course_name, term, course_rating, count_undergrad_students_mccormick, count_total_undergrad_students, count_class_students_sophomores, count_total_class_students)
                VALUES (?, ?, ?, ?, ?, ?, ?);
            ''', (course_name, term, course_rating, number_of_undergraduate_students_that_are_mccormick, total_number_of_undergraduate_students, number_of_class_students_that_are_sophomores, total_number_of_class_students))
            conn.commit()
            driver.switch_to.window(driver.window_handles[0])

def scrape_ctecs_for_all_courses_of_a_certain_academic_subject(academic_subject):
    number_of_courses = len(WebDriverWait(driver, 10000).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, CSS_SELECTORS['courses']))))
    for i in range(number_of_courses):
        time.sleep(10)
        course_button = WebDriverWait(driver, 10000).until(EC.element_to_be_clickable((By.CSS_SELECTOR, CSS_SELECTORS['course_button'] + str(i))))
        course_name = course_button.get_attribute('innerHTML')
        course_button.click()
        scrape_ctecs_for_course(academic_subject, course_name[:course_name.index(':')])

def scrape_ctecs_for_multiple_academic_subjects(academic_subjects):
    for academic_subject in academic_subjects:
        enter_into_ctecs_for_academic_subject(academic_subject)
        scrape_ctecs_for_all_courses_of_a_certain_academic_subject(academic_subject.split()[0])
        WebDriverWait(driver, 10000).until(EC.element_to_be_clickable((By.CSS_SELECTOR, CSS_SELECTORS['back_arrow_button']))).click()
