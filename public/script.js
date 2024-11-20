// script.js

document.addEventListener('DOMContentLoaded', () => {
    const coursesSelect = document.getElementById('courses');
    const courseForm = document.getElementById('course-form');
    const resultsDiv = document.getElementById('results');

    let courseData = {};

    // Fetch course data from the server
    fetch('/api/courses')
        .then(response => response.json())
        .then(data => {
            courseData = data;
            populateCoursesDropdown();
        })
        .catch(error => {
            console.error('Error fetching course data:', error);
            alert('Failed to load course data. Please try again later.');
        });

    // Populate courses dropdown
    function populateCoursesDropdown() {
        const courseNames = Object.keys(courseData);
        courseNames.forEach(course => {
            const option = document.createElement('option');
            option.value = course;
            option.textContent = course;
            coursesSelect.appendChild(option);
        });
    }

    // Handle form submission
    courseForm.addEventListener('submit', function(e) {
        e.preventDefault();

        // Get user inputs
        const selectedSchool = document.getElementById('school').value;
        const selectedClass = document.getElementById('class').value;
        const selectedQuarter = document.getElementById('quarter').value;
        const selectedCourses = Array.from(document.getElementById('courses').selectedOptions).map(option => option.value);

        // Validate selection
        if (selectedCourses.length === 0) {
            alert('Please select at least one course.');
            return;
        }

        // Process each selected course
        let rankedCourses = [];
        selectedCourses.forEach(course => {
            const courseInfo = courseData[course];
            // Check if the course is offered in the selected quarter
            if (courseInfo[selectedQuarter]) {
                const schoolDemographics = courseInfo[selectedQuarter].school_demographics;
                const classDemographics = courseInfo[selectedQuarter].class_demographics;

                const schoolMatch = schoolDemographics[selectedSchool];
                const classMatch = classDemographics[selectedClass];

                // Calculate a simple match score (you can adjust the weighting as needed)
                const matchScore = schoolMatch * classMatch;

                // const matchScore = courseInfo.course_rating;

                rankedCourses.push({
                    course: course,
                    matchScore: matchScore,
                    course_rating: courseInfo.course_rating,
                    student_opinion: courseInfo.student_opinion
                });
            } else {
                // If the course is not offered in the selected quarter, assign a low score
                rankedCourses.push({
                    course: course,
                    matchScore: 0,
                    course_rating: courseInfo.course_rating,
                    student_opinion: courseInfo.student_opinion,
                    notOffered: true
                });
            }
        });

        // rankedCourses.sort((a, b) => b.matchScore - a.matchScore);
        rankedCourses.sort((a, b) => b.course_rating - a.course_rating);
        // rankedCourses.sort((a, b) => b.course_rating * b.matchScore - a.course_rating * a.matchScore);

        // Display the results
        displayResults(rankedCourses, selectedQuarter);
    });

    // Function to display results
    function displayResults(rankedCourses, quarter) {
        resultsDiv.innerHTML = ''; // Clear previous results

        rankedCourses.forEach(course => {
            const courseDiv = document.createElement('div');
            courseDiv.classList.add('course');

            const courseTitle = document.createElement('h3');
            courseTitle.textContent = course.course;
            courseDiv.appendChild(courseTitle);

            if (course.notOffered) {
                const notOfferedMsg = document.createElement('p');
                notOfferedMsg.style.color = 'red';
                notOfferedMsg.textContent = `Not offered in ${quarter}.`;
                courseDiv.appendChild(notOfferedMsg);
                
                const ratingP = document.createElement('p');
                ratingP.textContent = `Course Rating: ${course.course_rating}`;
                courseDiv.appendChild(ratingP);

                const opinionP = document.createElement('p');
                opinionP.textContent = `Student Opinion: ${course.student_opinion}`;
                courseDiv.appendChild(opinionP);
            } else {
                const matchScoreP = document.createElement('p');
                matchScoreP.textContent = `Match Score: ${ (course.matchScore * 100).toFixed(2) }%`;
                courseDiv.appendChild(matchScoreP);

                const ratingP = document.createElement('p');
                ratingP.textContent = `Course Rating: ${course.course_rating}`;
                courseDiv.appendChild(ratingP);

                const opinionP = document.createElement('p');
                opinionP.textContent = `Student Opinion: ${course.student_opinion}`;
                courseDiv.appendChild(opinionP);
            }

            resultsDiv.appendChild(courseDiv);
        });
    }
});
