const { initMoodlePool } = require('../db');

class MoodleExtractorService {
  constructor() {
    this.poolPromise = initMoodlePool();
  }

  async getEnrolledUsers(courseId) {
    const pool = await this.poolPromise;
    const sql = `
      SELECT u.id AS id_student, u.firstname, u.lastname, u.email
      FROM mdl_user u
      INNER JOIN mdl_user_enrolments ue ON ue.userid = u.id
      INNER JOIN mdl_enrol e ON e.id = ue.enrolid
      WHERE e.courseid = ? AND u.deleted = 0;
    `;
    const [rows] = await pool.query(sql, [courseId]);
    return rows;
  }

  async getStudentLogs(studentId, courseId) {
    const pool = await this.poolPromise;
    const sql = `
      SELECT timecreated, action, target, courseid, userid
      FROM mdl_logstore_standard_log
      WHERE userid = ? AND courseid = ?
      ORDER BY timecreated ASC;
    `;
    const [rows] = await pool.query(sql, [studentId, courseId]);
    return rows;
  }

  async getStudentGrades(studentId, courseId) {
    const pool = await this.poolPromise;
    const sql = `
      SELECT gg.finalgrade, gg.rawgrade, gg.timemodified
      FROM mdl_grade_grades gg
      INNER JOIN mdl_grade_items gi ON gi.id = gg.itemid
      WHERE gg.userid = ? AND gi.courseid = ?;
    `;
    const [rows] = await pool.query(sql, [studentId, courseId]);
    return rows;
  }

  async getAssignmentSubmissions(studentId, courseId) {
    const pool = await this.poolPromise;
    const sql = `
      SELECT s.id, s.status, s.timemodified, a.name
      FROM mdl_assign_submission s
      INNER JOIN mdl_assign a ON a.id = s.assignment
      WHERE s.userid = ? AND a.course = ?;
    `;
    const [rows] = await pool.query(sql, [studentId, courseId]);
    return rows;
  }

  async getUserProfile(studentId) {
    const pool = await this.poolPromise;
    const sql = `
      SELECT id AS id_student, gender, country AS region, age FROM mdl_user WHERE id = ?;
    `;
    const [rows] = await pool.query(sql, [studentId]);
    return rows[0] || null;
  }

  async getCourseModules(courseId) {
    const pool = await this.poolPromise;
    const sql = `
      SELECT cm.id, cm.module, cm.instance
      FROM mdl_course_modules cm
      WHERE cm.course = ?;
    `;
    const [rows] = await pool.query(sql, [courseId]);
    return rows;
  }
}

module.exports = MoodleExtractorService;
