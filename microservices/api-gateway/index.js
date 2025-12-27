const express = require('express');
const http = require('http');
const socketIo = require('socket.io');
const amqp = require('amqplib');
const cors = require('cors');
const jwt = require('jsonwebtoken');
const { createProxyMiddleware } = require('http-proxy-middleware');
const morgan = require('morgan');
require('dotenv').config();
const Eureka = require('eureka-js-client').Eureka;

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

// Proxy Target URLs - Updated for Eureka Discovery
let PROFILER_URL = process.env.PROFILER_URL || 'http://student-profiler:8000';
let RECCO_URL = process.env.RECCO_URL || 'http://reco-builder:8003';
let COACH_API_URL = process.env.COACH_API_URL || 'http://student-coach-api:8005';

// Eureka Configuration
const eurekaClient = new Eureka({
  instance: {
    app: 'api-gateway',
    hostName: process.env.INSTANCE_HOST || 'api-gateway',
    ipAddr: '127.0.0.1',
    statusPageUrl: `http://${process.env.INSTANCE_HOST || 'api-gateway'}:4000/health`,
    port: {
      '$': 4000,
      '@enabled': 'true',
    },
    vipAddress: 'api-gateway',
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

eurekaClient.start((error) => {
  console.log(error || 'API Gateway registered with Eureka');
});

// Helper to get service URL from Eureka
function getServiceUrl(appName, fallback) {
  const instances = eurekaClient.getInstancesByAppId(appName);
  if (instances && instances.length > 0) {
    const instance = instances[0];
    return `http://${instance.hostName}:${instance.port.$}`;
  }
  return fallback;
}

// Update proxy targets dynamically if needed (or just use the helper in middleware)
const getProfilerUrl = () => getServiceUrl('student-profiler', PROFILER_URL);
const getReccoUrl = () => getServiceUrl('reco-builder', RECCO_URL);
const getCoachUrl = () => getServiceUrl('student-coach-api', COACH_API_URL);

console.log(`[Config] Profiler: ${PROFILER_URL}`);
console.log(`[Config] Recco: ${RECCO_URL}`);
console.log(`[Config] Coach: ${COACH_API_URL}`);

// Proxy for Student Profiler
app.use(['/api/profiler', '/api/profiling'], (req, res, next) => {
  createProxyMiddleware({
    target: getProfilerUrl(),
    changeOrigin: true,
    pathRewrite: {
      '^/api/profiler': '',
      '^/api/profiling': ''
    },
    onProxyReq: (proxyReq, req, res) => {
      console.log(`[Proxy] Profiler: ${req.method} ${req.url} -> ${getProfilerUrl()}${proxyReq.path}`);
    },
    onError: (err, req, res) => {
      console.error(`[Proxy Error] Profiler:`, err.message);
      res.status(502).json({ error: 'Profiler service unreachable', details: err.message });
    }
  })(req, res, next);
});

// Proxy for Recommendation Builder
app.use(['/api/recco', '/api/recommendations'], (req, res, next) => {
  createProxyMiddleware({
    target: getReccoUrl(),
    changeOrigin: true,
    pathRewrite: {
      '^/api/recco': '',
      '^/api/recommendations': ''
    },
    onProxyReq: (proxyReq, req, res) => {
      console.log(`[Proxy] Recco: ${req.method} ${req.url} -> ${getReccoUrl()}${proxyReq.path}`);
    },
    onError: (err, req, res) => {
      console.error(`[Proxy Error] Recco:`, err.message);
      res.status(502).json({ error: 'Recommendation service unreachable', details: err.message });
    }
  })(req, res, next);
});

// Proxy for Coach API (Fallback)
app.use(['/api/coach', '/api/student', '/api'], (req, res, next) => {
  createProxyMiddleware({
    target: getCoachUrl(),
    changeOrigin: true,
    pathRewrite: {
      '^/api/coach': '',
      '^/api/student': '',
      '^/api': ''
    },
    onProxyReq: (proxyReq, req, res) => {
      console.log(`[Proxy] Coach: ${req.method} ${req.url} -> ${getCoachUrl()}${proxyReq.path}`);
    },
    onError: (err, req, res) => {
      console.error(`[Proxy Error] Coach:`, err.message);
      res.status(502).json({ error: 'Coach service unreachable', details: err.message });
    }
  })(req, res, next);
});

// Proxy for Teacher Console API
let TEACHER_API_URL = process.env.TEACHER_API_URL || 'http://teacher-console-api:8004';
const getTeacherUrl = () => getServiceUrl('teacher-console-api', TEACHER_API_URL);
console.log(`[Config] Teacher: ${TEACHER_API_URL}`);

app.use(['/teacher', '/api/teacher'], (req, res, next) => {
  createProxyMiddleware({
    target: getTeacherUrl(),
    changeOrigin: true,
    pathRewrite: {
      '^/teacher': '',
      '^/api/teacher': ''
    },
    onProxyReq: (proxyReq, req, res) => {
      console.log(`[Proxy] Teacher: ${req.method} ${req.url} -> ${getTeacherUrl()}${proxyReq.path}`);
    },
    onError: (err, req, res) => {
      console.error(`[Proxy Error] Teacher:`, err.message);
      res.status(502).json({ error: 'Teacher service unreachable', details: err.message });
    }
  })(req, res, next);
});

// Default 404 handler
app.use((req, res) => {
  console.log(`404: ${req.method} ${req.url}`);
  res.status(404).json({ error: 'Route not found in API Gateway', path: req.url });
});

server.listen(PORT, () => {
  console.log(`API Gateway with WebSockets running on http://localhost:${PORT}`);
  console.log(`Gateway accepting requests at http://localhost:${PORT}/api`);
});
