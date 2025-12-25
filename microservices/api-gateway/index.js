const express = require('express');
const cors = require('cors');
const jwt = require('jsonwebtoken');
const { createProxyMiddleware } = require('http-proxy-middleware');
const morgan = require('morgan');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 4000;
const SECRET_KEY = process.env.JWT_SECRET || 'supersecretkey';

// Middleware
app.use(cors());
app.use(express.json());
app.use(morgan('dev'));

// Login Route (REST)
app.post('/api/login', (req, res) => {
  const { username, password } = req.body;
  console.log(`[Auth] Login attempt: ${username}`);

  // TODO: Add real validation against DB or Auth Service
  if (username) {
    const userPayload = {
      id: 1,
      name: username,
      role: 'student'
    };
    const accessToken = jwt.sign(userPayload, SECRET_KEY, { expiresIn: '24h' });

    res.json({
      success: true,
      user: userPayload,
      accessToken,
    });
  } else {
    res.status(401).json({ success: false, message: 'Identifiants invalides' });
  }
});

// Health Check
app.get('/health', (req, res) => {
  res.json({ status: 'OK', service: 'API Gateway' });
});

// Proxy to Student Coach API (Python)
app.use('/api', createProxyMiddleware({
  target: 'http://localhost:8005', // Helper microservice
  changeOrigin: true,
  pathRewrite: {
    '^/api': '', // Strip /api prefix when forwarding
  },
  onError: (err, req, res) => {
    console.error('Proxy Error:', err);
    res.status(500).json({ message: 'Service unavailable' });
  }
}));

app.listen(PORT, () => {
  console.log(`API Gateway running on http://localhost:${PORT}`);
  console.log(`Gateway accepting requests at http://localhost:${PORT}/api`);
});
