const express = require('express');
const http = require('http');
const socketIo = require('socket.io');
const amqp = require('amqplib');
const cors = require('cors');
const jwt = require('jsonwebtoken');
const { createProxyMiddleware } = require('http-proxy-middleware');
const morgan = require('morgan');
require('dotenv').config();

const app = express();
const server = http.createServer(app);
const io = socketIo(server, {
  cors: {
    origin: "*",
    methods: ["GET", "POST"]
  }
});

const PORT = process.env.PORT || 4000;
const SECRET_KEY = process.env.JWT_SECRET || 'supersecretkey';
const RABBITMQ_URL = process.env.RABBITMQ_URL || 'amqp://edupath:edupath@rabbitmq:5672';

// Middleware
app.use(cors());
app.use(morgan('dev'));

// RabbitMQ Consumer for Real-time Updates
async function startRabbitMQ() {
  try {
    const connection = await amqp.connect(RABBITMQ_URL);
    const channel = await connection.createChannel();
    const queue = 'profile_updated';

    await channel.assertQueue(queue, { durable: true });
    console.log(`[*] Waiting for messages in ${queue}. To exit press CTRL+C`);

    channel.consume(queue, (msg) => {
      if (msg !== null) {
        const content = JSON.parse(msg.content.toString());
        console.log(" [x] Received profile update:", content);

        // Broadcast to all connected clients
        io.emit('profile_alert', content);

        channel.ack(msg);
      }
    });

    connection.on('error', (err) => {
      console.error("[RabbitMQ] connection error", err);
      setTimeout(startRabbitMQ, 5000);
    });

    connection.on('close', () => {
      console.error("[RabbitMQ] connection closed, reconnecting...");
      setTimeout(startRabbitMQ, 5000);
    });

  } catch (error) {
    console.error("[RabbitMQ] Error:", error.message);
    setTimeout(startRabbitMQ, 5000);
  }
}

startRabbitMQ();

// Socket.io Events
io.on('connection', (socket) => {
  console.log('New client connected:', socket.id);
  socket.on('disconnect', () => {
    console.log('Client disconnected:', socket.id);
  });
});

// Login Route (REST) - MUST be before general proxy but needs body parser
app.post('/api/login', express.json(), (req, res) => {
  const { username } = req.body;

  // mapping usernames to actual IDs for demonstration
  const userMap = {
    'john': 6,
    'jane': 7,
    'bob': 8,
    'alice': 9
  };

  if (username) {
    const resolvedId = userMap[username.toLowerCase()] || 1;
    const userPayload = {
      id: resolvedId,
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
  res.json({ status: 'OK', service: 'API Gateway', socketStatus: 'Enabled' });
});

// Proxy Target URLs - Updated for Docker service names
const PROFILER_URL = process.env.PROFILER_URL || 'http://student_profiler:8000';
const RECCO_URL = process.env.RECCO_URL || 'http://recco_builder:8003';
const COACH_API_URL = process.env.COACH_API_URL || 'http://student_coach_api:8005';

console.log(`[Config] Profiler: ${PROFILER_URL}`);
console.log(`[Config] Recco: ${RECCO_URL}`);
console.log(`[Config] Coach: ${COACH_API_URL}`);

// Proxy for Student Profiler
app.use(['/api/profiler', '/api/profiling'], createProxyMiddleware({
  target: PROFILER_URL,
  changeOrigin: true,
  pathRewrite: {
    '^/api/profiler': '',
    '^/api/profiling': ''
  },
  onProxyReq: (proxyReq, req, res) => {
    console.log(`[Proxy] Profiler: ${req.method} ${req.url} -> ${PROFILER_URL}${proxyReq.path}`);
  },
  onError: (err, req, res) => {
    console.error(`[Proxy Error] Profiler:`, err.message);
    res.status(502).json({ error: 'Profiler service unreachable', details: err.message });
  }
}));

// Proxy for Recommendation Builder
app.use(['/api/recco', '/api/recommendations'], createProxyMiddleware({
  target: RECCO_URL,
  changeOrigin: true,
  pathRewrite: {
    '^/api/recco': '',
    '^/api/recommendations': ''
  },
  onProxyReq: (proxyReq, req, res) => {
    console.log(`[Proxy] Recco: ${req.method} ${req.url} -> ${RECCO_URL}${proxyReq.path}`);
  },
  onError: (err, req, res) => {
    console.error(`[Proxy Error] Recco:`, err.message);
    res.status(502).json({ error: 'Recommendation service unreachable', details: err.message });
  }
}));

// Proxy for Coach API (Fallback)
app.use(['/api/coach', '/api/student', '/api'], createProxyMiddleware({
  target: COACH_API_URL,
  changeOrigin: true,
  pathRewrite: {
    '^/api/coach': '',
    '^/api/student': '',
    '^/api': ''
  },
  onProxyReq: (proxyReq, req, res) => {
    console.log(`[Proxy] Coach: ${req.method} ${req.url} -> ${COACH_API_URL}${proxyReq.path}`);
  },
  onError: (err, req, res) => {
    console.error(`[Proxy Error] Coach:`, err.message);
    res.status(502).json({ error: 'Coach service unreachable', details: err.message });
  }
}));

// Default 404 handler
app.use((req, res) => {
  console.log(`404: ${req.method} ${req.url}`);
  res.status(404).json({ error: 'Route not found in API Gateway', path: req.url });
});

server.listen(PORT, () => {
  console.log(`API Gateway with WebSockets running on http://localhost:${PORT}`);
  console.log(`Gateway accepting requests at http://localhost:${PORT}/api`);
});
