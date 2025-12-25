const express = require('express');
const { createProxyMiddleware } = require('http-proxy-middleware');
const cors = require('cors');
const morgan = require('morgan');
const jwt = require('jsonwebtoken');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 4000;
const JWT_SECRET = process.env.JWT_SECRET || 'edupath_secret_key';

// Middleware
app.use(cors());
app.use(morgan('dev')); // Logging des requêtes
app.use(express.json());

// --- AUTHENTICATION MIDDLEWARE ---
const authenticateToken = (req, res, next) => {
  // Optionnel : On peut désactiver l'auth avec une variable d'env pour le dev
  if (process.env.DISABLE_AUTH === 'true') {
    return next();
  }

  const authHeader = req.headers['authorization'];
  const token = authHeader && authHeader.split(' ')[1];

  if (!token) return res.status(401).json({ error: 'Access Token Required' });

  jwt.verify(token, JWT_SECRET, (err, user) => {
    if (err) return res.status(403).json({ error: 'Invalid or Expired Token' });
    req.user = user;
    next();
  });
};

// --- ROUTES PUBLIQUES ---
app.get('/health', (req, res) => {
  res.json({
    status: 'UP',
    gateway: 'API Gateway',
    timestamp: new Date().toISOString()
  });
});

// Endpoint pour obtenir un token (Login)
app.post('/login', (req, res) => {
  const { username, password } = req.body;

  // Simulation de validation (à connecter à une DB plus tard)
  if (username && password) {
    const user = { name: username, role: username === 'admin' ? 'admin' : 'teacher' };
    const accessToken = jwt.sign(user, JWT_SECRET, { expiresIn: '24h' });
    return res.json({ accessToken, user });
  }

  res.status(400).json({ error: 'Username and password required' });
});

// --- SERVICES ROUTES (PROXIES) ---
const routes = {
  '/api/lms': 'http://lms-connector:3000',
  '/api/profiler': 'http://student-profiler:8000',
  '/api/predictor': 'http://path-predictor:8002',
  '/api/recommendations': 'http://reco-builder:8003',
  '/api/teacher': 'http://teacher-console-api:8004',
  '/api/student': 'http://student-coach-api:8005',
  '/api/prepadata': 'http://prepadata:8001'
};

// Configuration du Proxy
const proxyOptions = {
  changeOrigin: true,
  pathRewrite: (path, req) => {
    // Supprime le préfixe /api/xxx pour envoyer au microservice
    return path.replace(/^\/api\/[^\/]+/, '');
  },
  onError: (err, req, res) => {
    console.error('Proxy Error:', err);
    res.status(502).json({ error: 'Service Unavailable', details: err.message });
  }
};

// Montage des routes
for (const [path, target] of Object.entries(routes)) {
  // Pour le moment en dev, on ne protège pas les routes pour aider Omar et Nisrine
  // On pourra réactiver authenticateToken plus tard
  app.use(path, createProxyMiddleware({ ...proxyOptions, target }));
}

// Error handling pour les routes non trouvées
app.use((req, res) => {
  res.status(404).json({ error: 'Route not found in API Gateway' });
});

app.listen(PORT, () => {
  console.log(`
  ╔════════════════════════════════════════════════════════╗
  ║                                                        ║
  ║   🚀  EDUPATH-MS API GATEWAY                           ║
  ║   📡  Listening on port: ${PORT}                        ║
  ║   🔗  URL: http://localhost:${PORT}                      ║
  ║                                                        ║
  ╚════════════════════════════════════════════════════════╝
  `);
});
