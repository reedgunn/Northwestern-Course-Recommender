import os
from bs4 import BeautifulSoup
import json
from tqdm import tqdm

# from scrape import PATH_TO_RAW_DATA_FOLDER
PATH_TO_RAW_DATA_FOLDER = "data/raw"

CSS_SELECTORS = {
    "rating_tbodys": "[id^='BlockLayoutController'][id*='_BaseReportBlockUCPreview_TableStat_'] > tbody",
    "rating_tbody_response_count": "tr.CondensedTabularOddRows > td",
    "rating_tbody_mean": "tr.CondensedTabularEvenRows > td",
    "distribution_tbodys": "[id^='BlockLayoutController'][id*='_BaseReportBlockUCPreview_TableFrequency_'] > tbody",
    "distribution_tbody_counts": "tr > td:nth-child(2)"
}

COURSE_RATING_RATING_TBODYS_INDEX = 1

AVG_HR_HRS_PER_WEEK_DISTRIBUTION_TBODY_INDEX = 0

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


def extract_data_from_ctec(ctec_path):

    print(ctec_path)

    with open(ctec_path, 'r', encoding="utf-8") as f:
        ctec = f.read()
    
    soup = BeautifulSoup(ctec, "lxml")

    course_rating_response_count, course_rating_mean = get_course_rating_data(soup)
    # print(f"course_rating_response_count: {course_rating_response_count} ({type(course_rating_response_count)})")
    # print(f"course_rating_mean: {course_rating_mean} ({type(course_rating_mean)})")

    avg_hw_hrs_per_week_response_count, avg_hw_hrs_per_week_mean = get_avg_hw_hrs_per_week_data(soup)
    # print(f"avg_hw_hrs_per_week_response_count: {avg_hw_hrs_per_week_response_count} ({type(avg_hw_hrs_per_week_response_count)})")
    # print(f"avg_hw_hrs_per_week_mean: {avg_hw_hrs_per_week_mean} ({type(avg_hw_hrs_per_week_mean)})")

    return course_rating_response_count, course_rating_mean, avg_hw_hrs_per_week_response_count, avg_hw_hrs_per_week_mean

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

    
ctecs_paths = get_ctecs_paths()

data = {}

for ctec_path in tqdm(ctecs_paths, "Extracting data from ctecs"):

    academic_subject, course_number, quarter = parse_ctec_path(ctec_path)

    course_rating_response_count, course_rating_mean, avg_hw_hrs_per_week_response_count, avg_hw_hrs_per_week_mean = extract_data_from_ctec(ctec_path)

    ctec_data = {
        'course_rating_response_count': course_rating_response_count,
        'course_rating_mean': course_rating_mean,
        'avg_hw_hrs_per_week_response_count': avg_hw_hrs_per_week_response_count,
        'avg_hw_hrs_per_week_mean': avg_hw_hrs_per_week_mean
    }

    if academic_subject not in data:
        data[academic_subject] = {}
    if f"{course_number} ({quarter})" not in data[academic_subject]:
        data[academic_subject][f"{course_number} ({quarter})"] = []
    data[academic_subject][f"{course_number} ({quarter})"].append(ctec_data)


for academic_subject in tqdm(data):

    for course in data[academic_subject]:

        course_rating_response_count_total = sum(ctec_data["course_rating_response_count"] for ctec_data in data[academic_subject][course])
        avg_hw_hrs_per_week_response_count_total = sum(ctec_data["avg_hw_hrs_per_week_response_count"] for ctec_data in data[academic_subject][course])

        data[academic_subject][course] = {
            "course_rating": round(sum(ctec_data["course_rating_mean"] * ctec_data["course_rating_response_count"] for ctec_data in data[academic_subject][course]) / course_rating_response_count_total, 2) if course_rating_response_count_total != 0 else "N/A",
            "avg_hw_hrs_per_week": round(sum(ctec_data["avg_hw_hrs_per_week_mean"] * ctec_data["avg_hw_hrs_per_week_response_count"] for ctec_data in data[academic_subject][course]) / avg_hw_hrs_per_week_response_count_total, 1) if avg_hw_hrs_per_week_response_count_total != 0 else "N/A"
        }


data = dict(sorted(data.items())) # sort the data

with open("data/processed/data_processed.json", 'w', encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=4)
