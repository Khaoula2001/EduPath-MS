const MoodleExtractorService = require('./moodle-extractor.service');
const FeatureCalculatorService = require('./feature-calculator.service');
const StudentFeaturesRepository = require('../repositories/student-features.repository');

class SyncOrchestratorService {
  constructor() {
    this.extractor = new MoodleExtractorService();
    this.calculator = new FeatureCalculatorService();
    this.repo = new StudentFeaturesRepository();
  }

  async syncAllStudents(courseId) {
    // If courseId provided, sync for that course; otherwise attempt all users via enrolments of all courses
    let students = [];
    if (courseId) {
      students = await this.extractor.getEnrolledUsers(courseId);
    } else {
      // Fallback: get all active users
      students = await this._getAllActiveUsers();
    }

    const results = [];
    for (const s of students) {
      const r = await this.syncStudent(s.id_student || s.id, courseId);
      results.push(r);
    }
    return { synced: results.length, results };
  }

  async syncStudent(studentId, courseId) {
    // Gather data
    const [logs, grades, submissions, profile, courseModules] = await Promise.all([
      this.extractor.getStudentLogs(studentId, courseId),
      this.extractor.getStudentGrades(studentId, courseId),
      this.extractor.getAssignmentSubmissions(studentId, courseId),
      this.extractor.getUserProfile(studentId),
      this.extractor.getCourseModules(courseId),
    ]);

    // Calculate features
    const engagementMetrics = this.calculator.calculateEngagementMetrics(logs);
    const gradeMetrics = this.calculator.calculateGradeMetrics(grades);
    const dropoutRiskSignal = this.calculator.calculateDropoutRisk(engagementMetrics, gradeMetrics);
    const engagementDropRate = this.calculator.calculateEngagementDropRate(logs);
    const ageBand = this.calculator.calculateAgeBand(profile);
    const progressRate = this.calculator.calculateProgressRate(submissions, courseModules);

    const features = {
      id_student: studentId,
      code_module: String(courseId || 'UNKNOWN'),
      code_presentation: 'DEFAULT',
      gender: profile?.gender || null,
      region: profile?.region || null,
      age_band: ageBand,
      highest_education: null,
      disability: false,
      ...engagementMetrics,
      ...gradeMetrics,
      assessment_submissions_count: submissions.length,
      progress_rate: progressRate,
      unregistered: false,
      dropout_risk_signal: dropoutRiskSignal,
      engagement_drop_rate: engagementDropRate,
    };

    await this.repo.saveStudentFeatures(features);
    return features;
  }

  async syncSingleStudent(studentId, courseId) {
    return this.syncStudent(studentId, courseId);
  }

  async _getAllActiveUsers() {
    // Fallback query when no courseId provided
    const pool = await this.extractor.poolPromise;
    const sql = 'SELECT id AS id_student, firstname, lastname, email FROM mdl_user WHERE deleted = ?';
    const [rows] = await pool.query(sql, [0]);
    return rows;
  }
}

module.exports = SyncOrchestratorService;
