const { initPgPool } = require('../db');

class RawDataRepository {
    constructor() {
        this.poolPromise = initPgPool();
    }

    async saveRawData(source, dataType, rawJson) {
        const pool = await this.poolPromise;
        const sql = `
      INSERT INTO raw_learning_data (source, data_type, raw_json, processed)
      VALUES ($1, $2, $3, false)
    `;
        // Ensure rawJson is stringified if it's an object, though pg usually handles jsonb
        // simpler to pass object for JSONB type
        await pool.query(sql, [source, dataType, rawJson]);
    }
}

module.exports = RawDataRepository;
