const { initPgPool } = require('../db');

class StudentFeaturesRepository {
  constructor() {
    this.poolPromise = initPgPool();
  }

  async saveStudentFeatures(f) {
    const pool = await this.poolPromise;
    const sql = `
      INSERT INTO student_features (
        id_student, code_module, code_presentation,
        gender, region, age_band, highest_education, disability,
        total_clicks, activity_count, avg_clicks_per_activity, click_std,
        first_activity_day, last_activity_day, active_days, days_without_activity,
        regularity_index, engagement_intensity, mean_score, score_std,
        assessment_submissions_count, latest_assessment_score, study_duration,
        progress_rate, unregistered, dropout_risk_signal, engagement_drop_rate, synced_at
      ) VALUES (
        $1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,$13,$14,$15,$16,$17,$18,$19,$20,$21,$22,$23,$24,$25,$26,$27, NOW()
      )
      ON CONFLICT (id_student, code_module, code_presentation)
      DO UPDATE SET
        gender = EXCLUDED.gender,
        region = EXCLUDED.region,
        age_band = EXCLUDED.age_band,
        highest_education = EXCLUDED.highest_education,
        disability = EXCLUDED.disability,
        total_clicks = EXCLUDED.total_clicks,
        activity_count = EXCLUDED.activity_count,
        avg_clicks_per_activity = EXCLUDED.avg_clicks_per_activity,
        click_std = EXCLUDED.click_std,
        first_activity_day = EXCLUDED.first_activity_day,
        last_activity_day = EXCLUDED.last_activity_day,
        active_days = EXCLUDED.active_days,
        days_without_activity = EXCLUDED.days_without_activity,
        regularity_index = EXCLUDED.regularity_index,
        engagement_intensity = EXCLUDED.engagement_intensity,
        mean_score = EXCLUDED.mean_score,
        score_std = EXCLUDED.score_std,
        assessment_submissions_count = EXCLUDED.assessment_submissions_count,
        latest_assessment_score = EXCLUDED.latest_assessment_score,
        study_duration = EXCLUDED.study_duration,
        progress_rate = EXCLUDED.progress_rate,
        unregistered = EXCLUDED.unregistered,
        dropout_risk_signal = EXCLUDED.dropout_risk_signal,
        engagement_drop_rate = EXCLUDED.engagement_drop_rate,
        synced_at = NOW();
    `;

    const params = [
      f.id_student,
      f.code_module,
      f.code_presentation,
      f.gender,
      f.region,
      f.age_band,
      f.highest_education,
      !!f.disability,
      f.total_clicks || 0,
      f.activity_count || 0,
      f.avg_clicks_per_activity || 0,
      f.click_std || 0,
      f.first_activity_day,
      f.last_activity_day,
      f.active_days || 0,
      f.days_without_activity || 0,
      f.regularity_index || 0,
      f.engagement_intensity || 0,
      f.mean_score,
      f.score_std,
      f.assessment_submissions_count || 0,
      f.latest_assessment_score,
      f.study_duration || 0,
      f.progress_rate || 0,
      !!f.unregistered,
      f.dropout_risk_signal || 0,
      f.engagement_drop_rate || 0,
    ];

    await pool.query(sql, params);
  }

  async getAllFeatures(limit = 100, offset = 0) {
    const pool = await this.poolPromise;
    const { rows } = await pool.query('SELECT * FROM student_features ORDER BY synced_at DESC LIMIT $1 OFFSET $2', [limit, offset]);
    return rows;
  }

  async getFeaturesByStudent(studentId) {
    const pool = await this.poolPromise;
    const { rows } = await pool.query('SELECT * FROM student_features WHERE id_student = $1 ORDER BY synced_at DESC', [studentId]);
    return rows;
  }

  async getHighRiskStudents(minSignal = 2) {
    const pool = await this.poolPromise;
    const { rows } = await pool.query('SELECT * FROM student_features WHERE dropout_risk_signal >= $1 ORDER BY dropout_risk_signal DESC', [minSignal]);
    return rows;
  }

  async getStatistics() {
    const pool = await this.poolPromise;
    const { rows } = await pool.query(`
      SELECT
        COUNT(*) AS total_records,
        AVG(mean_score) AS avg_score,
        AVG(engagement_intensity) AS avg_engagement,
        AVG(progress_rate) AS avg_progress,
        SUM(CASE WHEN dropout_risk_signal >= 2 THEN 1 ELSE 0 END) AS high_risk_count
      FROM student_features
    `);
    return rows[0] || {};
  }
}

module.exports = StudentFeaturesRepository;
