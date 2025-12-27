// microservices/lms-connector/app.js
const express = require('express');
const { Pool } = require('pg');
const axios = require('axios');
const Eureka = require('eureka-js-client').Eureka;

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

  // Eureka Configuration
  const client = new Eureka({
    instance: {
      app: 'lms-connector',
      hostName: process.env.INSTANCE_HOST || 'lms-connector',
      ipAddr: '127.0.0.1',
      statusPageUrl: `http://${process.env.INSTANCE_HOST || 'lms-connector'}:3000/health`,
      port: {
        '$': 3000,
        '@enabled': 'true',
      },
      vipAddress: 'lms-connector',
      dataCenterInfo: {
        '@class': 'com.netflix.appinfo.InstanceInfo$DefaultDataCenterInfo',
        name: 'MyOwn',
      },
    },
    eureka: {
      host: process.env.EUREKA_HOST || 'eureka-server',
      port: process.env.EUREKA_PORT || 8761,
      servicePath: '/eureka/apps/',
    },
  });

  client.start((error) => {
    console.log(error || 'LMS Connector registered with Eureka');

    // Automatic Sync Loop (Every 5 minutes)
    setInterval(async () => {
      console.log('--- Auto-Sync Triggered ---');
      try {
        await axios.post('http://localhost:3000/sync/moodle', {});
        console.log('--- Auto-Sync Completed ---');
      } catch (err) {
        console.error('--- Auto-Sync Failed:', err.message);
      }
    }, 5 * 60 * 1000); // 5 minutes
  });
});
