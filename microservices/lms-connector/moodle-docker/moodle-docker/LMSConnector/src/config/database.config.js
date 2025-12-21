const dotenv = require('dotenv');
dotenv.config();

const pgConfig = {
  host: process.env.DB_HOST || 'lmsdb',
  port: parseInt(process.env.DB_PORT || '5432', 10),
  database: process.env.DB_NAME || 'lmsconnector',
  user: process.env.DB_USER || 'lms',
  password: process.env.DB_PASSWORD,
  max: parseInt(process.env.DB_POOL_MAX || '10', 10),
  idleTimeoutMillis: parseInt(process.env.DB_IDLE_TIMEOUT || '30000', 10),
};

const mysqlConfig = {
  host: process.env.MYSQL_HOST || process.env.MOODLE_DB_HOST || 'clouddb',
  port: parseInt(process.env.MYSQL_PORT || '3306', 10),
  database: process.env.MYSQL_DATABASE || process.env.MOODLE_DB_NAME || 'moodle',
  user: process.env.MYSQL_USER || process.env.MOODLE_DB_USER || 'root',
  password: process.env.MYSQL_PASSWORD || process.env.MOODLE_DB_PASSWORD || process.env.MYSQL_ROOT_PASSWORD,
  waitForConnections: true,
  connectionLimit: parseInt(process.env.MYSQL_POOL_MAX || '10', 10),
  queueLimit: 0,
};

module.exports = { pgConfig, mysqlConfig };
