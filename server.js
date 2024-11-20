// server.js

const express = require('express');
const path = require('path');
const fs = require('fs');
const cors = require('cors');

const app = express();
const PORT = process.env.PORT || 3000;

// Enable CORS
app.use(cors());

// Serve static files from the 'public' directory
app.use(express.static(path.join(__dirname, 'public')));

// API endpoint to get all courses
app.get('/api/courses', (req, res) => {
    const dataPath = path.join(__dirname, 'data', 'data_processed.json');
    fs.readFile(dataPath, 'utf8', (err, data) => {
        if (err) {
            console.error('Error reading data_processed.json:', err);
            return res.status(500).json({ error: 'Failed to read course data.' });
        }
        try {
            const courses = JSON.parse(data);
            res.json(courses);
        } catch (parseError) {
            console.error('Error parsing data_processed.json:', parseError);
            res.status(500).json({ error: 'Invalid course data format.' });
        }
    });
});

// Fallback to index.html for SPA (Single Page Application) routing
app.get('*', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// Start the server
app.listen(PORT, () => {
    console.log(`Server is running on http://localhost:${PORT}`);
});
