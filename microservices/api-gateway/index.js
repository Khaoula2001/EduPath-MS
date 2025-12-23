const express = require('express');
const { createProxyMiddleware } = require('http-proxy-middleware');
const cors = require('cors');
const jwt = require('jsonwebtoken');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 4000;
const JWT_SECRET = process.env.JWT_SECRET || 'edupath_secret_key';

app.use(cors());
app.use(express.json());

// Middleware d'authentification OAuth2 (Simulation JWT)
const authenticateToken = (req, res, next) => {
  const authHeader = req.headers['authorization'];
  const token = authHeader && authHeader.split(' ')[1];

  if (!token) return res.status(401).json({ error: 'Access Token Required' });

  jwt.verify(token, JWT_SECRET, (err, user) => {
    if (err) return res.status(403).json({ error: 'Invalid or Expired Token' });
    req.user = user;
    next();
  });
};

// Endpoint pour obtenir un token (Simulation Login)
app.post('/login', (req, res) => {
  const { username } = req.body;
  const user = { name: username, role: 'teacher' }; // Simple simulation
  const accessToken = jwt.sign(user, JWT_SECRET, { expiresIn: '1h' });
  res.json({ accessToken });
});

// Routes de proxy vers les microservices
const routes = {
  '/lms': 'http://lms-connector:3000',
  '/profiler': 'http://student-profiler:8000',
  '/predictor': 'http://path-predictor:8002',
  '/reco': 'http://reco-builder:8003',
  '/teacher': 'http://teacher-console-api:8004',
  '/student': 'http://student-coach-api:8005',
  '/prepadata': 'http://prepadata:8001'
};

for (const [path, target] of Object.entries(routes)) {
  // On protège tous les services sauf le health check et le login
  app.use(path, authenticateToken, createProxyMiddleware({
    target,
    changeOrigin: true,
    pathRewrite: {
      [`^${path}`]: '',
    },
  }));
}

app.get('/health', (req, res) => {
  res.json({ status: 'UP', gateway: 'API Gateway' });
});

app.listen(PORT, () => {
  console.log(`🚀 API Gateway running on port ${PORT}`);
});
