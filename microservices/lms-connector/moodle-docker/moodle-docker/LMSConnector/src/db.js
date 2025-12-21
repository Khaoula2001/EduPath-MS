const { Pool } = require('pg');
const mysql = require('mysql2/promise');
const { pgConfig, mysqlConfig } = require('./config/database.config');

let pgPool;
let moodlePool;

async function initPgPool() {
  if (!pgPool) {
    pgPool = new Pool(pgConfig);
    pgPool.on('error', (err) => {
      console.error('[PostgreSQL] Pool error:', err);
    });
    console.log('[PostgreSQL] Pool initialized');
  }
  return pgPool;
}

async function initMoodlePool() {
  if (!moodlePool) {
    moodlePool = await mysql.createPool(mysqlConfig);
    console.log('[MySQL Moodle] Pool initialized');
  }
  return moodlePool;
}

async function getPgClient() {
  const pool = await initPgPool();
  return pool.connect();
}

async function testConnections() {
  try {
    const pg = await initPgPool();
    const res = await pg.query('SELECT 1');
    console.log('[PostgreSQL] Test OK:', res.rows[0]);
  } catch (e) {
    console.error('[PostgreSQL] Connection test failed:', e.message);
  }

  try {
    const mysqlPool = await initMoodlePool();
    const [rows] = await mysqlPool.query('SELECT 1 AS ok');
    console.log('[MySQL Moodle] Test OK:', rows[0]);
  } catch (e) {
    console.error('[MySQL Moodle] Connection test failed:', e.message);
  }
}

module.exports = {
  initPgPool,
  initMoodlePool,
  getPgClient,
  testConnections,
};
