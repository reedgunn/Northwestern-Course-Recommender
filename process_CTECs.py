import os
from bs4 import BeautifulSoup
import json
from tqdm import tqdm
# from openai import OpenAI
# from functools import reduce
from time import sleep

# from scrape import PATH_TO_RAW_DATA_FOLDER, MOST_RECENT_QUARTERS_WITH_CTECS_PUBLISHED
PATH_TO_RAW_DATA_FOLDER = "data/raw"
MOST_RECENT_QUARTERS_WITH_CTECS_PUBLISHED = ["2024 Fall", "2024 Spring", "2024 Winter"]


CSS_SELECTORS = {
    "rating_tbodys": "[id^='BlockLayoutController'][id*='_BaseReportBlockUCPreview_TableStat_'] > tbody",
    "rating_tbody_response_count": "tr.CondensedTabularOddRows > td",
    "rating_tbody_mean": "tr.CondensedTabularEvenRows > td",

    "distribution_tbodys": "[id^='BlockLayoutController'][id*='_BaseReportBlockUCPreview_TableFrequency_'] > tbody",
    "distribution_tbody_counts": "tr > td:nth-child(2)",

    # "student_opinions": "[id^='BlockLayoutController'][id*='_BaseReportBlockUCPreview_CommentBoxbac5fa25-de6b-4010-bf3d-3e511cb8d63dReportSummary_'] > tbody > tr > td"
}

COURSE_RATING_RATING_TBODYS_INDEX = 1

AVG_HR_HRS_PER_WEEK_DISTRIBUTION_TBODY_INDEX = 0

SCHOOL_DISTRIBUTION_TBODY_INDEX = 1

def get_int(string):
    try:
        res = int(string)
    except:
        res = 0
    return res

def get_float(string):
    try:
        res = float(string)
    except:
        res = 0
    return res

def get_course_rating_data(soup):
    tbody = soup.select(CSS_SELECTORS['rating_tbodys'])[COURSE_RATING_RATING_TBODYS_INDEX]
    response_count = get_int(tbody.select_one(CSS_SELECTORS["rating_tbody_response_count"]).text)
    mean = get_float(tbody.select_one(CSS_SELECTORS["rating_tbody_mean"]).text)
    return response_count, mean

def get_avg_hw_hrs_per_week_data(soup):
    tbody = soup.select(CSS_SELECTORS['distribution_tbodys'])[AVG_HR_HRS_PER_WEEK_DISTRIBUTION_TBODY_INDEX]
    counts = [get_int(count.text) for count in tbody.select(CSS_SELECTORS['distribution_tbody_counts'])]
    response_count = sum(counts)
    if response_count == 0:
        return 0, 0
    three_or_fewer, four_to_seven, eight_to_eleven, twelve_to_fifteen, sixteen_to_nineteen, twenty_or_more = counts
    mean = (
        (
            (three_or_fewer * 1.75) +
            (four_to_seven * 5.5) +
            (eight_to_eleven * 9.5) +
            (twelve_to_fifteen * 13.5) +
            (sixteen_to_nineteen * 17.5) +
            (twenty_or_more * 21.25)
        ) / response_count
    )
    return response_count, mean

# def get_student_opinions(soup):
#     return set(student_opinion.text for student_opinion in soup.select(CSS_SELECTORS['student_opinions']))

# def get_school_data(soup):
#     tbody = soup.select(CSS_SELECTORS['distribution_tbodys'])[SCHOOL_DISTRIBUTION_TBODY_INDEX]
#     counts = [int(count.text) for count in tbody.select(CSS_SELECTORS['distribution_tbody_counts'])]
#     sesp = counts[0]
#     comm = counts[1]
#     mccormick = counts[4]
#     medill = counts[5]
#     bienen = counts[6]
#     weinberg = counts[9]
#     school_distribution_td_counts = [int(school_distribution_td_count.text) for school_distribution_td_count in soup.select(CSS_SELECTORS['distribution_tbodys'])[1].select(CSS_SELECTORS['distribution_td_counts'])]
#     return school_distribution_td_counts[9], school_distribution_td_counts[4], school_distribution_td_counts[5], school_distribution_td_counts[1], school_distribution_td_counts[0], school_distribution_td_counts[6]

# def get_year_data(soup):
#     return [int(year_distribution_td_count.text) for year_distribution_td_count in soup.select(CSS_SELECTORS['distribution_tbodys'])[2].select(CSS_SELECTORS['distribution_td_counts'])[:4]]

def extract_data_from_ctec(ctec_path):

    # print(ctec_path)

    with open(ctec_path, 'r', encoding='utf-8') as f:
        ctec = f.read()
    
    soup = BeautifulSoup(ctec, "lxml")

    course_rating_response_count, course_rating_mean = get_course_rating_data(soup)
    # print(f"course_rating_response_count: {course_rating_response_count} ({type(course_rating_response_count)})")
    # print(f"course_rating_mean: {course_rating_mean} ({type(course_rating_mean)})")

    avg_hw_hrs_per_week_response_count, avg_hw_hrs_per_week_mean = get_avg_hw_hrs_per_week_data(soup)
    # print(f"avg_hw_hrs_per_week_response_count: {avg_hw_hrs_per_week_response_count} ({type(avg_hw_hrs_per_week_response_count)})")
    # print(f"avg_hw_hrs_per_week_mean: {avg_hw_hrs_per_week_mean} ({type(avg_hw_hrs_per_week_mean)})")

    # student_opinions = get_student_opinions(soup)
    # print(f"student_opinions: {student_opinions} ({type(student_opinions)})")

    # weinberg_students, mccormick_students, medill_students, comm_students, sesp_students, bienen_students = get_school_data(soup)
    # print(f"weinberg_students: {weinberg_students} ({type(weinberg_students)})")
    # print(f"mccormick_students: {mccormick_students} ({type(mccormick_students)})")
    # print(f"medill_students: {medill_students} ({type(medill_students)})")
    # print(f"comm_students: {comm_students} ({type(comm_students)})")
    # print(f"sesp_students: {sesp_students} ({type(sesp_students)})")
    # print(f"bienen_students: {bienen_students} ({type(bienen_students)})")

    # freshmen, sophomores, juniors, seniors = get_year_data(soup)
    # print(f"freshmen: {freshmen} ({type(freshmen)})")
    # print(f"sophomores: {sophomores} ({type(sophomores)})")
    # print(f"juniors: {juniors} ({type(juniors)})")
    # print(f"seniors: {seniors} ({type(seniors)})")

    return course_rating_response_count, course_rating_mean, avg_hw_hrs_per_week_response_count, avg_hw_hrs_per_week_mean

# client = OpenAI(api_key=OPENAI_API_KEY)
# def get_ai_generated_aggregate_student_opinion(student_opinions):
#     return client.chat.completions.create(
#         model = 'gpt-4o-mini',
#         messages = [
#             {
#                 'role': 'user',
#                 'content': f'Provide only a one-sentence summary (that doesn\'t mention the professor) of these opinions that were written about a course by students who completed the course: {student_opinions}'
#             }
#         ]
#     ).choices[0].message.content

def stop(): # for debugging
    sleep(1e6)

def parse_ctec_path(ctec_path):
    split = ctec_path.split('%')
    academic_subject = split[1]
    course_number = split[2]
    quarter = split[3].replace('$', ' ')
    return academic_subject, course_number, quarter

def get_ctecs_paths():
    res = sorted(os.listdir(PATH_TO_RAW_DATA_FOLDER))
    for i in range(len(res)):
        res[i] = f"{PATH_TO_RAW_DATA_FOLDER}/{res[i]}"
    return res

data = {}
    
ctecs_paths = get_ctecs_paths()

for ctec_path in tqdm(ctecs_paths, "Extracting data from ctecs"):

    academic_subject, course_number, quarter = parse_ctec_path(ctec_path)

    course_rating_response_count, course_rating_mean, avg_hw_hrs_per_week_response_count, avg_hw_hrs_per_week_mean = extract_data_from_ctec(ctec_path)

    # (
    #     course_rating, course_rating_votes, 
    #     avg_hw_hrs_per_week, avg_hw_hrs_per_week_votes, 
    #     student_opinions, 
    #     weinberg_students, mccormick_students, medill_students, comm_students, sesp_students, bienen_students, 
    #     freshmen, sophomores, juniors, seniors
    # ) = extract_data_from_ctec(ctec_path)

    ctec_data = {
        'course_rating_response_count': course_rating_response_count,
        'course_rating_mean': course_rating_mean,
        'avg_hw_hrs_per_week_response_count': avg_hw_hrs_per_week_response_count,
        'avg_hw_hrs_per_week_mean': avg_hw_hrs_per_week_mean
    }

    if academic_subject not in data:
        data[academic_subject] = {}
    if course_number not in data[academic_subject]:
        data[academic_subject][course_number] = {}
    if quarter not in data[academic_subject][course_number]:
        data[academic_subject][course_number][quarter] = []
    data[academic_subject][course_number][quarter].append(ctec_data)


for academic_subject in tqdm(data):

    for course_number in data[academic_subject]:

        for quarter in MOST_RECENT_QUARTERS_WITH_CTECS_PUBLISHED:
            
            if quarter in data[academic_subject][course_number]:

                course_rating_response_count_total = sum(ctec_data["course_rating_response_count"] for ctec_data in data[academic_subject][course_number][quarter])
                avg_hw_hrs_per_week_response_count_total = sum(ctec_data["avg_hw_hrs_per_week_response_count"] for ctec_data in data[academic_subject][course_number][quarter])

                data[academic_subject][course_number] = {
                    "course_rating": round(sum(ctec_data["course_rating_mean"] * ctec_data["course_rating_response_count"] for ctec_data in data[academic_subject][course_number][quarter]) / course_rating_response_count_total, 2) if course_rating_response_count_total != 0 else "N/A",
                    "avg_hw_hrs_per_week": round(sum(ctec_data["avg_hw_hrs_per_week_mean"] * ctec_data["avg_hw_hrs_per_week_response_count"] for ctec_data in data[academic_subject][course_number][quarter]) / avg_hw_hrs_per_week_response_count_total, 1) if avg_hw_hrs_per_week_response_count_total != 0 else "N/A"
                }

                break

    #     for quarter in data[academic_subject][course_number]:

    #         data[academic_subject][course_number][quarter] = {
    #             "course_rating": ,
    #             "avg_hw_hrs_per_week": 
    #         }

    # for latest_quarter in LATEST_QUARTERS_WITH_CTECS_PUBLISHED.values():

    #     if latest_quarter in data[course]:

    #         latest_course_rating = sum(CTEC_data['course_rating'] * CTEC_data['course_rating_votes'] for CTEC_data in data[course][latest_quarter]) / sum(CTEC_data['course_rating_votes'] for CTEC_data in data[course][latest_quarter])

    #         latest_avg_hw_hrs_per_week = sum(CTEC_data['avg_hw_hrs_per_week'] * CTEC_data['avg_hw_hrs_per_week_votes'] for CTEC_data in data[course][latest_quarter]) / sum(CTEC_data['avg_hw_hrs_per_week_votes'] for CTEC_data in data[course][latest_quarter])

    #         # ai_generated_aggregate_latest_student_opinion = get_ai_generated_aggregate_student_opinion(reduce(lambda x, y: x | y, [CTEC_data['student_opinions'] for CTEC_data in data[course][latest_quarter]]))
    #         ai_generated_aggregate_latest_student_opinion = 'Coming soon'

    #         break

    # for quarter in data[course]:
        
    #     total_weinberg_students = sum([CTEC_data['weinberg_students'] for CTEC_data in data[course][quarter]])
    #     total_mccormick_students = sum([CTEC_data['mccormick_students'] for CTEC_data in data[course][quarter]])
    #     total_medill_students = sum([CTEC_data['medill_students'] for CTEC_data in data[course][quarter]])
    #     total_comm_students = sum([CTEC_data['comm_students'] for CTEC_data in data[course][quarter]])
    #     total_sesp_students = sum([CTEC_data['sesp_students'] for CTEC_data in data[course][quarter]])
    #     total_bienen_students = sum([CTEC_data['bienen_students'] for CTEC_data in data[course][quarter]])
    #     total_school_students = total_weinberg_students + total_mccormick_students + total_medill_students + total_comm_students + total_sesp_students + total_bienen_students
    #     if total_school_students:
    #         weinberg_students = total_weinberg_students / total_school_students
    #         mccormick_students = total_mccormick_students / total_school_students
    #         medill_students = total_medill_students / total_school_students
    #         comm_students = total_comm_students / total_school_students
    #         sesp_students = total_sesp_students / total_school_students
    #         bienen_students = total_bienen_students / total_school_students
    #     else:
    #         weinberg_students = 'N/A'
    #         mccormick_students = 'N/A'
    #         medill_students = 'N/A'
    #         comm_students = 'N/A'
    #         sesp_students = 'N/A'
    #         bienen_students = 'N/A'

    #     total_freshmen = sum([CTEC_data['freshmen'] for CTEC_data in data[course][quarter]])
    #     total_sophomores = sum([CTEC_data['sophomores'] for CTEC_data in data[course][quarter]])
    #     total_juniors = sum([CTEC_data['juniors'] for CTEC_data in data[course][quarter]])
    #     total_seniors = sum([CTEC_data['seniors'] for CTEC_data in data[course][quarter]])
    #     total_year_students = total_freshmen + total_sophomores + total_juniors + total_seniors
    #     if total_year_students:
    #         freshmen = total_freshmen / total_year_students
    #         sophomores = total_sophomores / total_year_students
    #         juniors = total_juniors / total_year_students
    #         seniors = total_seniors / total_year_students
    #     else:
    #         freshmen = 'N/A'
    #         sophomores = 'N/A'
    #         juniors = 'N/A'
    #         seniors = 'N/A'
        
    #     data[course][quarter] = {
    #         'weinberg_students': weinberg_students,
    #         'mccormick_students': mccormick_students,
    #         'medill_students': medill_students,
    #         'comm_students': comm_students,
    #         'sesp_students': sesp_students,
    #         'bienen_students': bienen_students,
    #         'freshmen': freshmen,
    #         'sophomores': sophomores,
    #         'juniors': juniors,
    #         'seniors': seniors
    #     }
    
    # data[course]['latest_course_rating'] = latest_course_rating
    # data[course]['latest_avg_hw_hrs_per_week'] = latest_avg_hw_hrs_per_week
    # data[course]['ai_generated_aggregate_latest_student_opinion'] = ai_generated_aggregate_latest_student_opinion

data = dict(sorted(data.items())) # sort the data

with open('data/processed/data_processed.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=4)
