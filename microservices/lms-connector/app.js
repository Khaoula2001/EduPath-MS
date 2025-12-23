// microservices/lms-connector/app.js
const express = require('express');
const { Pool } = require('pg');
const axios = require('axios');

const app = express();
app.use(express.json());

const pool = new Pool({
  user: process.env.DB_USER || 'prepadata',
  host: process.env.DB_HOST || 'postgres',
  database: process.env.DB_NAME || 'analytics',
  password: process.env.DB_PASSWORD || 'prepadata_pwd',
  port: process.env.DB_PORT || 5432,
});

/**
 * Normalise et insère les données dans la table raw_learning_data
 */
async function saveRawData(source, dataType, rawJson) {
  const query = `
    INSERT INTO raw_learning_data (source, data_type, raw_json, processed)
    VALUES ($1, $2, $3, false)
  `;
  await pool.query(query, [source, dataType, JSON.stringify(rawJson)]);
}

// Endpoint pour synchroniser les données Moodle
app.post('/sync/moodle', async (req, res) => {
  const { moodle_url, token } = req.body;
  const targetUrl = moodle_url || process.env.MOODLE_API_URL;
  const targetToken = token || process.env.MOODLE_TOKEN;

  if (!targetUrl || !targetToken) {
    return res.status(400).json({ error: 'Moodle URL and Token are required' });
  }

  try {
    // 1. Récupérer les notes (grades)
    const gradesResponse = await axios.get(targetUrl, {
      params: {
        wstoken: targetToken,
        wsfunction: 'core_grades_get_grades',
        moodlewsrestformat: 'json'
      }
    });
    await saveRawData('MOODLE', 'student_assessment', gradesResponse.data);

    // 2. Récupérer les infos utilisateurs
    const usersResponse = await axios.get(targetUrl, {
      params: {
        wstoken: targetToken,
        wsfunction: 'core_enrol_get_enrolled_users',
        courseid: req.body.courseid || 1, // Exemple: nécessite un ID de cours
        moodlewsrestformat: 'json'
      }
    });
    await saveRawData('MOODLE', 'student_info', usersResponse.data);

    res.json({ 
      message: 'Données synchronisées avec succès',
      details: {
        assessments: gradesResponse.data ? 'OK' : 'Empty',
        users: usersResponse.data ? 'OK' : 'Empty'
      }
    });
  } catch (error) {
    console.error('Sync Error:', error.message);
    res.status(500).json({ error: error.message });
  }
});

app.get('/health', (req, res) => {
  res.json({ status: 'UP', service: 'LMS Connector' });
});

app.listen(3000, () => {
  console.log('LMS Connector démarré sur le port 3000');
});
