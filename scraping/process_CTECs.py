import os
import glob
from bs4 import BeautifulSoup
import json
from tqdm import tqdm
from openai import OpenAI
from functools import reduce

from scrape import LATEST_QUARTERS_WITH_CTECS_PUBLISHED
from confidential import OPENAI_API_KEY


CSS_SELECTORS = {
    'rating_tbodys': "[id^='BlockLayoutController'][id*='_BaseReportBlockUCPreview_TableStat_'] > tbody",
    'rating_td_values': 'tr > td',
    'student_opinions': "[id^='BlockLayoutController'][id*='_BaseReportBlockUCPreview_CommentBoxbac5fa25-de6b-4010-bf3d-3e511cb8d63dReportSummary_'] > tbody > tr > td",
    'distribution_tbodys': "[id^='BlockLayoutController'][id*='_BaseReportBlockUCPreview_TableFrequency_'] > tbody",
    'distribution_td_counts': 'tr > td:nth-child(2)'
}


def get_course_and_quarter(CTEC_path):
    quarter, course, professor = [x.replace('$', ' ') for x in CTEC_path.split('%')[1:4]]
    index_of_first_hyphen_in_course = course.index('-')
    index_of_second_hyphen_in_course = course.index('-', index_of_first_hyphen_in_course + 1)
    # index_of_first_space_in_course = course.index(' ')
    # index_of_second_space_in_course = course.index(' ', index_of_first_space_in_course + 1)
    # course = f'{course[:index_of_second_hyphen_in_course]} ({course[index_of_second_space_in_course + 1:]})'
    course = course[:index_of_second_hyphen_in_course]
    return course, quarter

def get_course_rating_data(soup):
    course_rating_td_values = [course_rating_td_value.text for course_rating_td_value in soup.select(CSS_SELECTORS['rating_tbodys'])[1].select(CSS_SELECTORS['rating_td_values'])]
    return float(course_rating_td_values[1]), int(course_rating_td_values[0])

def get_avg_hw_hrs_per_week_data(soup):
    avg_hw_hrs_per_week_td_counts = [int(avg_hw_hrs_per_week_td_count.text) for avg_hw_hrs_per_week_td_count in soup.select(CSS_SELECTORS['distribution_tbodys'])[0].select(CSS_SELECTORS['distribution_td_counts'])]
    votes = sum(avg_hw_hrs_per_week_td_counts)
    return (
        (
            avg_hw_hrs_per_week_td_counts[0] * 1.75 +
            avg_hw_hrs_per_week_td_counts[1] * 5.5 +
            avg_hw_hrs_per_week_td_counts[2] * 9.5 +
            avg_hw_hrs_per_week_td_counts[3] * 13.5 +
            avg_hw_hrs_per_week_td_counts[4] * 17.5 +
            avg_hw_hrs_per_week_td_counts[5] * 21.25
        ) / votes,
        votes
    )

def get_student_opinions(soup):
    return set(student_opinion.text for student_opinion in soup.select(CSS_SELECTORS['student_opinions']))

def get_school_data(soup):
    school_distribution_td_counts = [int(school_distribution_td_count.text) for school_distribution_td_count in soup.select(CSS_SELECTORS['distribution_tbodys'])[1].select(CSS_SELECTORS['distribution_td_counts'])]
    return school_distribution_td_counts[9], school_distribution_td_counts[4], school_distribution_td_counts[5], school_distribution_td_counts[1], school_distribution_td_counts[0], school_distribution_td_counts[6]

def get_year_data(soup):
    return [int(year_distribution_td_count.text) for year_distribution_td_count in soup.select(CSS_SELECTORS['distribution_tbodys'])[2].select(CSS_SELECTORS['distribution_td_counts'])[:4]]

def scrape_CTEC(CTEC):
    soup = BeautifulSoup(CTEC, 'lxml')
    course_rating, course_rating_votes = get_course_rating_data(soup)
    # print(f"course_rating: {course_rating} ({type(course_rating)}).")
    # print(f"course_rating_votes: {course_rating_votes} ({type(course_rating_votes)}).")
    avg_hw_hrs_per_week, avg_hw_hrs_per_week_votes = get_avg_hw_hrs_per_week_data(soup)
    # print(f"avg_hw_hrs_per_week: {avg_hw_hrs_per_week} ({type(avg_hw_hrs_per_week)}).")
    # print(f"avg_hw_hrs_per_week_votes: {avg_hw_hrs_per_week_votes} ({type(avg_hw_hrs_per_week_votes)}).")
    student_opinions = get_student_opinions(soup)
    # print(f"student_opinions: {student_opinions} ({type(student_opinions)}).")
    weinberg_students, mccormick_students, medill_students, comm_students, sesp_students, bienen_students = get_school_data(soup)
    # print(f"weinberg_students: {weinberg_students} ({type(weinberg_students)}).")
    # print(f"mccormick_students: {mccormick_students} ({type(mccormick_students)}).")
    # print(f"medill_students: {medill_students} ({type(medill_students)}).")
    # print(f"comm_students: {comm_students} ({type(comm_students)}).")
    # print(f"sesp_students: {sesp_students} ({type(sesp_students)}).")
    # print(f"bienen_students: {bienen_students} ({type(bienen_students)}).")
    freshmen, sophomores, juniors, seniors = get_year_data(soup)
    # print(f"freshmen: {freshmen} ({type(freshmen)}).")
    # print(f"sophomores: {sophomores} ({type(sophomores)}).")
    # print(f"juniors: {juniors} ({type(juniors)}).")
    # print(f"seniors: {seniors} ({type(seniors)}).")
    return (
        course_rating, course_rating_votes, 
        avg_hw_hrs_per_week, avg_hw_hrs_per_week_votes, 
        student_opinions, 
        weinberg_students, mccormick_students, medill_students, comm_students, sesp_students, bienen_students, 
        freshmen, sophomores, juniors, seniors
    )

client = OpenAI(api_key=OPENAI_API_KEY)
def get_ai_generated_aggregate_student_opinion(student_opinions):
    return client.chat.completions.create(
        model = 'gpt-4o-mini',
        messages = [
            {
                'role': 'user',
                'content': f'Provide only a one-sentence summary (that doesn\'t mention the professor) of these opinions that were written about a course by students who completed the course: {student_opinions}'
            }
        ]
    ).choices[0].message.content


def process_CTECs():

    data = {}

    CTEC_paths = glob.glob(os.path.join('data/raw', '*.html*'))

    for CTEC_path in tqdm(CTEC_paths, 'Scraping CTECs'):

        course, quarter = get_course_and_quarter(CTEC_path)

        with open(CTEC_path, 'r', encoding='utf-8') as file:
            CTEC = file.read()

        (
            course_rating, course_rating_votes, 
            avg_hw_hrs_per_week, avg_hw_hrs_per_week_votes, 
            student_opinions, 
            weinberg_students, mccormick_students, medill_students, comm_students, sesp_students, bienen_students, 
            freshmen, sophomores, juniors, seniors
        ) = scrape_CTEC(CTEC)

        CTEC_data = {
            'course_rating': course_rating,
            'course_rating_votes': course_rating_votes,
            'avg_hw_hrs_per_week': avg_hw_hrs_per_week,
            'avg_hw_hrs_per_week_votes': avg_hw_hrs_per_week_votes,
            'student_opinions': student_opinions,
            'weinberg_students': weinberg_students,
            'mccormick_students': mccormick_students,
            'medill_students': medill_students,
            'comm_students': comm_students,
            'sesp_students': sesp_students,
            'bienen_students': bienen_students,
            'freshmen': freshmen,
            'sophomores': sophomores,
            'juniors': juniors,
            'seniors': seniors
        }

        if course not in data:
            data[course] = { quarter: [CTEC_data] }
        elif quarter not in data[course]:
            data[course][quarter] = [CTEC_data]
        elif CTEC_data not in data[course][quarter]:
            data[course][quarter].append(CTEC_data)

    for course in tqdm(data, 'Generating data for each course'):

        for latest_quarter in LATEST_QUARTERS_WITH_CTECS_PUBLISHED.values():

            if latest_quarter in data[course]:

                latest_course_rating = sum(CTEC_data['course_rating'] * CTEC_data['course_rating_votes'] for CTEC_data in data[course][latest_quarter]) / sum(CTEC_data['course_rating_votes'] for CTEC_data in data[course][latest_quarter])

                latest_avg_hw_hrs_per_week = sum(CTEC_data['avg_hw_hrs_per_week'] * CTEC_data['avg_hw_hrs_per_week_votes'] for CTEC_data in data[course][latest_quarter]) / sum(CTEC_data['avg_hw_hrs_per_week_votes'] for CTEC_data in data[course][latest_quarter])

                # ai_generated_aggregate_latest_student_opinion = get_ai_generated_aggregate_student_opinion(reduce(lambda x, y: x | y, [CTEC_data['student_opinions'] for CTEC_data in data[course][latest_quarter]]))
                ai_generated_aggregate_latest_student_opinion = 'Coming soon'

                break

        for quarter in data[course]:
            
            total_weinberg_students = sum([CTEC_data['weinberg_students'] for CTEC_data in data[course][quarter]])
            total_mccormick_students = sum([CTEC_data['mccormick_students'] for CTEC_data in data[course][quarter]])
            total_medill_students = sum([CTEC_data['medill_students'] for CTEC_data in data[course][quarter]])
            total_comm_students = sum([CTEC_data['comm_students'] for CTEC_data in data[course][quarter]])
            total_sesp_students = sum([CTEC_data['sesp_students'] for CTEC_data in data[course][quarter]])
            total_bienen_students = sum([CTEC_data['bienen_students'] for CTEC_data in data[course][quarter]])
            total_school_students = total_weinberg_students + total_mccormick_students + total_medill_students + total_comm_students + total_sesp_students + total_bienen_students
            if total_school_students:
                weinberg_students = total_weinberg_students / total_school_students
                mccormick_students = total_mccormick_students / total_school_students
                medill_students = total_medill_students / total_school_students
                comm_students = total_comm_students / total_school_students
                sesp_students = total_sesp_students / total_school_students
                bienen_students = total_bienen_students / total_school_students
            else:
                weinberg_students = 'N/A'
                mccormick_students = 'N/A'
                medill_students = 'N/A'
                comm_students = 'N/A'
                sesp_students = 'N/A'
                bienen_students = 'N/A'

            total_freshmen = sum([CTEC_data['freshmen'] for CTEC_data in data[course][quarter]])
            total_sophomores = sum([CTEC_data['sophomores'] for CTEC_data in data[course][quarter]])
            total_juniors = sum([CTEC_data['juniors'] for CTEC_data in data[course][quarter]])
            total_seniors = sum([CTEC_data['seniors'] for CTEC_data in data[course][quarter]])
            total_year_students = total_freshmen + total_sophomores + total_juniors + total_seniors
            if total_year_students:
                freshmen = total_freshmen / total_year_students
                sophomores = total_sophomores / total_year_students
                juniors = total_juniors / total_year_students
                seniors = total_seniors / total_year_students
            else:
                freshmen = 'N/A'
                sophomores = 'N/A'
                juniors = 'N/A'
                seniors = 'N/A'
            
            data[course][quarter] = {
                'weinberg_students': weinberg_students,
                'mccormick_students': mccormick_students,
                'medill_students': medill_students,
                'comm_students': comm_students,
                'sesp_students': sesp_students,
                'bienen_students': bienen_students,
                'freshmen': freshmen,
                'sophomores': sophomores,
                'juniors': juniors,
                'seniors': seniors
            }
        
        data[course]['latest_course_rating'] = latest_course_rating
        data[course]['latest_avg_hw_hrs_per_week'] = latest_avg_hw_hrs_per_week
        data[course]['ai_generated_aggregate_latest_student_opinion'] = ai_generated_aggregate_latest_student_opinion

    data = dict(sorted(data.items())) # sort the data

    with open('data/processed/data_processed.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


process_CTECs()
