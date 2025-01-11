import json
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import sys, os
sys.path.append('scraping')

from scrape import LATEST_QUARTERS_WITH_CTECS_PUBLISHED


app = Flask(
    __name__,
    static_folder=os.path.abspath('website'),
    template_folder=os.path.abspath('website')
)
CORS(app)


with open('data/processed/data_processed.json', 'r') as file:
    data = json.load(file)


quarter_type_to_key = {
    'Spring': LATEST_QUARTERS_WITH_CTECS_PUBLISHED['Spring'],
    'Winter': LATEST_QUARTERS_WITH_CTECS_PUBLISHED['Winter'],
    'Fall': LATEST_QUARTERS_WITH_CTECS_PUBLISHED['Fall']
}

school_to_key = {
    'Weinberg': 'weinberg_students',
    'McCormick': 'mccormick_students',
    'Medill': 'medill_students',
    'Comm': 'comm_students',
    'SESP': 'sesp_students',
    'Bienen': 'bienen_students',
}

year_to_key = {
    'Freshman': 'freshmen',
    'Sophomore': 'sophomores',
    'Junior': 'juniors',
    'Senior': 'seniors'
}


def rank_courses(courses, quarter_type, school, year):

    res = {}

    for course in courses:

        if quarter_type_to_key[quarter_type] in data[course]:
            if data[course][quarter_type_to_key[quarter_type]][school_to_key[school]] == 'N/A' or data[course][quarter_type_to_key[quarter_type]][year_to_key[year]] == 'N/A':
                match_score = -1
                match_score_display = 'N/A'
            else:
                match_score = data[course][quarter_type_to_key[quarter_type]][school_to_key[school]] * data[course][quarter_type_to_key[quarter_type]][year_to_key[year]]
                match_score_display = str(round(match_score, 2))
        else:
            for quarter in LATEST_QUARTERS_WITH_CTECS_PUBLISHED.values():
                if quarter in data[course]:
                    if data[course][quarter][school_to_key[school]] == 'N/A' or data[course][quarter][year_to_key[year]] == 'N/A':
                        match_score = -1
                        match_score_display = 'N/A'
                    else:
                        match_score = data[course][quarter][school_to_key[school]] * data[course][quarter][year_to_key[year]]
                        match_score_display = f'{round(match_score, 2)} ({quarter})'
                    break

        latest_course_rating = data[course]['latest_course_rating']
        latest_course_rating_display = str(round(latest_course_rating, 2))

        latest_avg_hw_hrs_per_week = data[course]['latest_avg_hw_hrs_per_week']
        latest_avg_hw_hrs_per_week_display = str(round(latest_avg_hw_hrs_per_week, 1))

        ai_generated_aggregate_latest_student_opinion_display = data[course]['ai_generated_aggregate_latest_student_opinion']

        # overall_score = match_score * latest_course_rating / latest_avg_hw_hrs_per_week
        overall_score = match_score * latest_course_rating
        if match_score_display == 'N/A':
            overall_score_display = 'N/A'
        else:
            overall_score_display = str(round(overall_score, 2))

        res[course] = {
            'Match score': match_score_display,
            'Latest course rating': latest_course_rating_display,
            'Latest average homework hours per week': latest_avg_hw_hrs_per_week_display,
            'AI-generated aggregate latest student opinion': ai_generated_aggregate_latest_student_opinion_display,
            'Overall Score': overall_score_display,
            'overall_score': overall_score
        }

    # res = dict(sorted(res.items(), key=lambda item: -item[1]['overall_score']))

    # for course in res:
    #     del res[course]['overall_score']
    
    return res




@app.route('/api/rank_courses', methods=['POST'])
def rank_courses_endpoint():
    data_received = request.get_json()

    school = data_received.get('school')
    year = data_received.get('year')
    quarter = data_received.get('quarter')
    courses = data_received.get('courses', [])

    if not all([school, year, quarter, courses]):
        return jsonify({'error': 'Missing required parameters.'}), 400

    ranked = rank_courses(courses, quarter, school, year)

    return jsonify(ranked), 200



def get_courses():
    return list(data.keys())


@app.route('/api/get_courses', methods=['GET'])
def get_courses_endpoint():
    courses = get_courses()
    return jsonify({'courses': courses}), 200


@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)