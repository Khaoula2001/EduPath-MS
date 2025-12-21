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

// Endpoint pour synchroniser les données Moodle
app.post('/sync/moodle', async (req, res) => {
  try {
    const response = await axios.get(`${process.env.MOODLE_API_URL}`, {
      params: {
        wstoken: process.env.MOODLE_TOKEN,
        wsfunction: 'core_grades_get_grades',
        moodlewsrestformat: 'json'
      }
    });
    
    // Traitement et insertion des données
    // ... implémentation de la logique de synchronisation
    
    res.json({ message: 'Données synchronisées avec succès' });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.listen(3000, () => {
  console.log('LMS Connector démarré sur le port 3000');
});
