const { initMoodlePool } = require('../db');
const crypto = require('crypto');

// Utility to create a delay/timestamp relative to now
const daysAgo = (days) => Math.floor(Date.now() / 1000) - (days * 86400);

async function seedMoodle() {
  const pool = await initMoodlePool();
  console.log('--- Starting Multi-Course Seeding ---');

  const CATEGORY_IT = 2; // Catégorie IT existante
  const CAT_CONTEXT_ID = 18;

  const coursesToCreate = [
    {
      fullname: 'Architecture et Maintenance Informatique',
      shortname: 'ARCH-BASE',
      description: 'Comprendre les composants physiques et le fonctionnement des ordinateurs.',
      activities: [
        { name: 'PDF : Les composants d’un ordinateur – Guide illustré', type: 'resource' },
        { name: 'Vidéo : Comprendre CPU, RAM, stockage en 10 minutes', type: 'url' },
        { name: 'Infographie : Modèle OSI simplifié', type: 'resource' },
        { name: 'Article externe : Qu’est-ce qu’un système d’exploitation ?', type: 'url' },
        { name: 'Quiz Moodle : 20 questions sur le matériel et les logiciels', type: 'quiz' },
        { name: 'Activité pratique : Identifier les composants d’un PC réel ou virtuel', type: 'assign' }
      ]
    },
    {
      fullname: 'Algorithmique et Logique de Programmation',
      shortname: 'ALGO-LOGIC',
      description: 'Bases fondamentales de la programmation et de la logique.',
      activities: [
        { name: 'PDF : Les bases du pseudo-code (IF, FOR, WHILE…)', type: 'resource' },
        { name: 'Vidéo : Algorithmes expliqués simplement avec des exemples', type: 'url' },
        { name: 'TP Moodle : écrire un algorithme pour trier une liste', type: 'assign' },
        { name: 'Quiz : variables, conditions, boucles', type: 'quiz' },
        { name: 'Exercices interactifs (H5P) : Fibonacci et nombres pairs', type: 'url' },
        { name: 'Fichier téléchargeable : modèles de diagrammes de flux', type: 'resource' }
      ]
    },
    {
      fullname: 'Développement Web – HTML / CSS / JavaScript',
      shortname: 'Web-Front',
      description: 'Formation complète pour comprendre la structure d’une page web, le style visuel et la logique.',
      activities: [
        { name: 'ZIP : fichiers d’exemple HTML/CSS/JS', type: 'resource' },
        { name: 'Vidéo tutorielle : Créer sa première page web', type: 'url' },
        { name: 'PDF : Les balises HTML indispensables', type: 'resource' },
        { name: 'Quiz HTML, CSS, JavaScript', type: 'quiz' },
        { name: 'TP : créer une page portfolio simple', type: 'assign' },
        { name: 'Lien externe : MDN Web Docs (Mozilla)', type: 'url' }
      ]
    },
    {
      fullname: 'Introduction aux Réseaux Informatique – CCNA Niveau 1',
      shortname: 'Réseaux-Base',
      description: 'Bases des réseaux : IPv4/IPv6, OSI, routage, VLAN et sécurité.',
      activities: [
        { name: 'PDF : Introduction au modèle OSI et TCP/IP', type: 'resource' },
        { name: 'Vidéo : Adresse IP et sous-réseaux', type: 'url' },
        { name: 'TP Packet Tracer : configuration d’un petit réseau local', type: 'assign' },
        { name: 'Quiz : OSI, IPv4, équipements réseaux', type: 'quiz' },
        { name: 'Image HD : schéma de topologie réseau simple', type: 'resource' }
      ]
    }
  ];

  try {
    const [modRows] = await pool.query("SELECT id, name FROM mdl_modules");
    const modules = modRows.reduce((acc, mod) => { acc[mod.name] = mod.id; return acc; }, {});

    for (const cData of coursesToCreate) {
      console.log(`Processing course: ${cData.fullname}`);

      const [existing] = await pool.query('SELECT id FROM mdl_course WHERE shortname = ?', [cData.shortname]);
      let courseId;
      if (existing.length === 0) {
        const [result] = await pool.query(
          'INSERT INTO mdl_course (fullname, shortname, category, summary, summaryformat, format, showgrades, newsitems, startdate, maxbytes, showreports, visible, timecreated, timemodified) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
          [cData.fullname, cData.shortname, CATEGORY_IT, `<p>${cData.description}</p>`, 1, 'topics', 1, 5, daysAgo(30), 2097152, 1, 1, daysAgo(30), daysAgo(30)]
        );
        courseId = result.insertId;
        console.log(`Created course ${cData.shortname} ID: ${courseId}`);

        // Course Context
        const [ctxRes] = await pool.query('INSERT INTO mdl_context (contextlevel, instanceid, depth) VALUES (?, ?, ?)', [50, courseId, 4]);
        const ctxId = ctxRes.insertId;
        await pool.query('UPDATE mdl_context SET path = ? WHERE id = ?', [`/1/3/${CAT_CONTEXT_ID}/${ctxId}`, ctxId]);

        // Create Sections
        for (let s = 0; s <= 2; s++) {
          await pool.query(
            'INSERT INTO mdl_course_sections (course, section, name, summary, summaryformat, sequence, visible) VALUES (?, ?, ?, ?, ?, ?, ?)',
            [courseId, s, s === 0 ? '' : `Module ${s}`, `<p>Contenu du module ${s}</p>`, 1, '', 1]
          );
        }
      } else {
        courseId = existing[0].id;
      }

      // Add Activities
      for (let i = 0; i < cData.activities.length; i++) {
        const act = cData.activities[i];
        const sectionNum = (i % 2) + 1; // Distribuer entre section 1 et 2
        await addActivity(pool, courseId, act, modules[act.type] || modules['assign'], sectionNum);
      }

      // Enrol existing students
      const studentsData = [
        { email: 'john@example.com' },
        { email: 'jane@example.com' },
        { email: 'bob@example.com' },
        { email: 'alice@example.com' }
      ];

      const [enrol] = await pool.query('SELECT id FROM mdl_enrol WHERE courseid = ? AND enrol = ?', [courseId, 'manual']);
      let enrolId = enrol.length > 0 ? enrol[0].id : null;
      if (!enrolId) {
        const [enRes] = await pool.query('INSERT INTO mdl_enrol (enrol, status, courseid, sortorder, timemodified) VALUES (?, ?, ?, ?, ?)', ['manual', 0, courseId, 0, daysAgo(30)]);
        enrolId = enRes.insertId;
      }

      for (const student of studentsData) {
        let [user] = await pool.query('SELECT id FROM mdl_user WHERE email = ?', [student.email]);
        let userId;

        if (user.length === 0) {
          const firstname = student.email.split('@')[0];
          const username = firstname.toLowerCase();
          const [uRes] = await pool.query(
            'INSERT INTO mdl_user (username, password, firstname, lastname, email, city, country, confirmed, mnethostid, timecreated, timemodified) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
            [username, 'not_a_hashed_password', firstname, 'Student', student.email, 'Marrakech', 'MA', 1, 1, daysAgo(30), daysAgo(30)]
          );
          userId = uRes.insertId;
          console.log(`  + Created User: ${student.email} (ID: ${userId})`);

          // User Context
          await pool.query('INSERT INTO mdl_context (contextlevel, instanceid, depth, path) VALUES (?, ?, ?, ?)', [30, userId, 2, `/1/${userId}`]);
        } else {
          userId = user[0].id;
        }

        const [ue] = await pool.query('SELECT id FROM mdl_user_enrolments WHERE enrolid = ? AND userid = ?', [enrolId, userId]);
        if (ue.length === 0) {
          await pool.query('INSERT INTO mdl_user_enrolments (status, enrolid, userid, timemodified, timecreated) VALUES (?, ?, ?, ?, ?)', [0, enrolId, userId, daysAgo(30), daysAgo(30)]);
          console.log(`  + Enrolled ${student.email} in course ${courseId}`);
        }

        // Add some activity logs for this student in this course
        await addActivityLogs(pool, userId, courseId);
        // Add some grades for this student
        await addGrades(pool, userId, courseId);
      }
    }

    console.log('--- All Courses Seeded Successfully ---');
  } catch (err) {
    console.error('Error during multi-course seeding:', err);
  } finally {
    process.exit(0);
  }
}

async function addActivityLogs(pool, userId, courseId) {
  const actions = ['viewed', 'submitted', 'started'];
  const targets = ['course', 'assign', 'quiz', 'module'];

  // Create 10-20 random logs
  const logCount = 10 + Math.floor(Math.random() * 10);
  for (let i = 0; i < logCount; i++) {
    const time = daysAgo(Math.floor(Math.random() * 20));
    await pool.query(
      'INSERT INTO mdl_logstore_standard_log (eventname, component, action, target, objecttable, objectid, crud, edulevel, contextid, contextlevel, contextinstanceid, userid, courseid, relateduserid, anonymous, other, timecreated, ip, realuserid) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
      ['\\core\\event\\course_viewed', 'core', actions[i % 3], targets[i % 4], 'course', courseId, 'r', 1, 1, 50, courseId, userId, courseId, null, 0, '[]', time, '127.0.0.1', null]
    );
  }
}

async function addGrades(pool, userId, courseId) {
  // Get grade items for this course
  const [items] = await pool.query('SELECT id FROM mdl_grade_items WHERE courseid = ?', [courseId]);

  for (const item of items) {
    const rawgrade = 50 + Math.floor(Math.random() * 50);
    const [existing] = await pool.query('SELECT id FROM mdl_grade_grades WHERE itemid = ? AND userid = ?', [item.id, userId]);

    if (existing.length === 0) {
      await pool.query(
        'INSERT INTO mdl_grade_grades (itemid, userid, rawgrade, finalgrade, timecreated, timemodified) VALUES (?, ?, ?, ?, ?, ?)',
        [item.id, userId, rawgrade, rawgrade, daysAgo(5), daysAgo(5)]
      );
    }
  }
}

async function addActivity(pool, courseId, act, moduleId, sectionNum) {
  // Simplification : on n'ajoute que l'entrée dans mdl_course_modules et la table spécifique si nécessaire
  // Pour la démo, on simule l'existence dans les tables de modules
  let instanceId = 1; // Instance bidon pour simplifier

  const tableName = `mdl_${act.type === 'url' ? 'url' : act.type === 'resource' ? 'resource' : act.type === 'quiz' ? 'quiz' : 'assign'}`;

  try {
    const [existing] = await pool.query(`SELECT id FROM ${tableName} WHERE course = ? AND name = ?`, [courseId, act.name]);
    if (existing.length === 0) {
      const [res] = await pool.query(
        `INSERT INTO ${tableName} (course, name, intro, introformat, timemodified) VALUES (?, ?, ?, ?, ?)`,
        [courseId, act.name, `Contenu pour ${act.name}`, 1, daysAgo(30)]
      );
      instanceId = res.insertId;

      const [cmRes] = await pool.query(
        'INSERT INTO mdl_course_modules (course, module, instance, added, score, indent, visible, visibleoncoursepage, completion) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
        [courseId, moduleId, instanceId, daysAgo(30), 0, 0, 1, 1, 0]
      );
      const cmId = cmRes.insertId;

      const [sections] = await pool.query('SELECT id, sequence FROM mdl_course_sections WHERE course = ? AND section = ?', [courseId, sectionNum]);
      let seq = sections[0].sequence ? sections[0].sequence.split(',') : [];
      seq.push(cmId);
      await pool.query('UPDATE mdl_course_sections SET sequence = ? WHERE id = ?', [seq.join(','), sections[0].id]);

      console.log(`  + Added Activity: ${act.name} (${act.type})`);
    }
  } catch (e) {
    console.warn(`  ! Could not add activity ${act.name}: ${e.message}`);
  }
}

seedMoodle();
