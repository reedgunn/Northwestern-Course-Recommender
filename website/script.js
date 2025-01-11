document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('course-form');
    const resultsDiv = document.getElementById('results');
    const coursesSelect = document.getElementById('courses');

    // Function to fetch and populate courses
    async function fetchCourses() {
        try {
            const response = await fetch('/api/get_courses'); // Update the endpoint if necessary
            if (!response.ok) {
                throw new Error(`Failed to fetch courses: ${response.statusText}`);
            }
            const data = await response.json();
            const courses = data.courses;

            // Sort courses alphabetically for better usability
            courses.sort((a, b) => a.localeCompare(b));

            // Populate the multi-select dropdown
            courses.forEach(course => {
                const option = document.createElement('option');
                option.value = course;
                option.textContent = course;
                coursesSelect.appendChild(option);
            });
        } catch (error) {
            console.error('Error fetching courses:', error);
            resultsDiv.innerHTML = `<p class="error">Failed to load courses. Please try again later.</p>`;
        }
    }

    // Fetch courses on page load
    fetchCourses();

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        // Clear previous results
        resultsDiv.innerHTML = '';

        // Get form values
        const school = document.getElementById('school').value;
        const year = document.getElementById('year').value;
        const quarter = document.getElementById('quarter').value;
        const selectedOptions = Array.from(coursesSelect.selectedOptions);
        const courses = selectedOptions.map(option => option.value);

        // Validate courses selection
        if (courses.length === 0) {
            alert('Please select at least one course.');
            return;
        }

        // Prepare payload
        const payload = {
            school,
            year,
            quarter,
            courses
        };

        try {
            // Show loading message
            resultsDiv.innerHTML = '<p>Loading...</p>';

            // Make API request
            const response = await fetch('/api/rank_courses', { // Update the API endpoint as needed
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Server error');
            }

            const rankedCourses = await response.json();

            // Check if there are results
            if (Object.keys(rankedCourses).length === 0) {
                resultsDiv.innerHTML = '<p>No courses found matching the criteria.</p>';
                return;
            }

            // Convert the object to an array of [key, value] pairs
            const sortedCourses = Object.entries(rankedCourses).sort((a, b) => {
                return b[1]['overall_score'] - a[1]['overall_score'];
            });

            // Create results table
            let tableHTML = `
                <h2>Ranked Courses</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Course</th>
                            <th>Match Score</th>
                            <th>Latest Rating</th>
                            <th>Avg HW Hours/Week</th>
                            <th>Student Opinion</th>
                            <th>Overall Score</th>
                        </tr>
                    </thead>
                    <tbody>
            `;

            for (const [course, details] of sortedCourses) {
                tableHTML += `
                    <tr>
                        <td>${course}</td>
                        <td>${details['Match score']}</td>
                        <td>${details['Latest course rating']}</td>
                        <td>${details['Latest average homework hours per week']}</td>
                        <td>${details['AI-generated aggregate latest student opinion']}</td>
                        <td>${details['Overall Score']}</td>
                    </tr>
                `;
            }

            tableHTML += `
                    </tbody>
                </table>
            `;

            resultsDiv.innerHTML = tableHTML;

        } catch (error) {
            console.error('Error:', error);
            resultsDiv.innerHTML = `<p class="error">An error occurred: ${error.message}</p>`;
        }
    });
});
