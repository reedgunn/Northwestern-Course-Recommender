from openai import OpenAI
from confidential import MY_OPENAI_API_KEY
import json
from tqdm import tqdm

client = OpenAI(api_key=MY_OPENAI_API_KEY)

def clean_up_student_opinion(student_opinion):
    res = student_opinion.replace('<br><br>', ' ')
    res = res.replace('<br>', ' ')
    res.replace('"', "'")
    i = 1
    while i < len(res):
        if res[i] == ' ' and res[i - 1] == ' ':
            res = res[:i] + res[i + 1:]
        else:
            i += 1
    return res

def get_average_student_opinion(student_opinions):
    return client.chat.completions.create(
        model = 'gpt-4o-mini',
        messages = [
            {
                'role': 'system',
                'content': 'You receive a set of strings and output only a one-sentence "average" (by linguistic meaning) of the strings.'
            },
            {
                'role': 'user',
                'content': f'"{'", "'.join([clean_up_student_opinion(student_opinion) for student_opinion in student_opinions])}"'
            }
        ]
    ).choices[0].message.content

def process_data():
    with open('data/data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    data_processed = {}
    for course in data.values():
        data_processed.update(course)

    for course in tqdm(data_processed):
        course_rating = round(sum(data_processed[course][term]['course_rating']['average'] * data_processed[course][term]['course_rating']['student_count'] for term in data_processed[course]) / sum(data_processed[course][term]['course_rating']['student_count'] for term in data_processed[course]), 2)

        student_opinion = get_average_student_opinion([student_opinion for term in data_processed[course].values() for student_opinion in term['student_opinions'].values()])

        for term in data_processed[course]:
            data_processed[course][term].pop('course_rating')
            data_processed[course][term].pop('student_opinions')
            school_demographics_total = sum(data_processed[course][term]['school_demographics'].values())
            for school_deographic in data_processed[course][term]['school_demographics']:
                data_processed[course][term]['school_demographics'][school_deographic] = round(data_processed[course][term]['school_demographics'][school_deographic] / school_demographics_total, 2)
            class_demographics_total = sum(data_processed[course][term]['class_demographics'].values())
            for class_deographic in data_processed[course][term]['class_demographics']:
                data_processed[course][term]['class_demographics'][class_deographic] = round(data_processed[course][term]['class_demographics'][class_deographic] / class_demographics_total, 2)
        data_processed[course]['course_rating'] = course_rating
        data_processed[course]['student_opinion'] = student_opinion

    with open('data/data_processed.json', 'w', encoding='utf-8') as f:
        json.dump(data_processed, f, ensure_ascii=False, indent=4)

process_data()
