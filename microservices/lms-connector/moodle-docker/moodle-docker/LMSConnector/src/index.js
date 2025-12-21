const express = require('express');
const { testConnections } = require('./db');
const SyncOrchestratorService = require('./services/sync-orchestrator.service');
const StudentFeaturesRepository = require('./repositories/student-features.repository');

const app = express();
app.use(express.json());

const orchestrator = new SyncOrchestratorService();
const repo = new StudentFeaturesRepository();

app.get('/health', async (req, res) => {
  await testConnections();
  res.json({ status: 'ok' });
});

// Sync routes
app.post('/api/sync/full', async (req, res) => {
  try {
    const { courseId } = req.body || {};
    const result = await orchestrator.syncAllStudents(courseId);
    res.json({ ok: true, ...result });
  } catch (e) {
    res.status(500).json({ ok: false, error: e.message });
  }
});

app.post('/api/sync/student/:studentId/course/:courseId', async (req, res) => {
  try {
    const { studentId, courseId } = req.params;
    const result = await orchestrator.syncSingleStudent(Number(studentId), Number(courseId));
    res.json({ ok: true, result });
  } catch (e) {
    res.status(500).json({ ok: false, error: e.message });
  }
});

// Features routes
app.get('/api/features', async (req, res) => {
  try {
    const limit = Number(req.query.limit || 100);
    const offset = Number(req.query.offset || 0);
    const rows = await repo.getAllFeatures(limit, offset);
    res.json(rows);
  } catch (e) {
    res.status(500).json({ ok: false, error: e.message });
  }
});

app.get('/api/features/student/:studentId', async (req, res) => {
  try {
    const rows = await repo.getFeaturesByStudent(Number(req.params.studentId));
    res.json(rows);
  } catch (e) {
    res.status(500).json({ ok: false, error: e.message });
  }
});

app.get('/api/features/high-risk', async (req, res) => {
  try {
    const minSignal = Number(req.query.minSignal || 2);
    const rows = await repo.getHighRiskStudents(minSignal);
    res.json(rows);
  } catch (e) {
    res.status(500).json({ ok: false, error: e.message });
  }
});

app.get('/api/statistics', async (req, res) => {
  try {
    const stats = await repo.getStatistics();
    res.json(stats);
  } catch (e) {
    res.status(500).json({ ok: false, error: e.message });
  }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`LMSConnector lancé sur le port ${PORT}`);
});
