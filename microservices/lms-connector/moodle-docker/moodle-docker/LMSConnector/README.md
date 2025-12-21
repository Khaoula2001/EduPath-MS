# LMSConnector

Service Node.js pour extraction de données Moodle, calcul de features étudiants et synchronisation dans PostgreSQL.

## Installation

1. Configurer les variables d'environnement (via docker-compose):
   - DB_HOST, DB_NAME, DB_USER, DB_PASSWORD (PostgreSQL)
   - MYSQL_HOST, MYSQL_DATABASE, MYSQL_USER, MYSQL_PASSWORD (Moodle MySQL)
2. Lancer via Docker Compose.

## API Endpoints

- POST /api/sync/full `{ courseId?: number }`
- POST /api/sync/student/:studentId/course/:courseId
- GET /api/features
- GET /api/features/student/:studentId
- GET /api/features/high-risk `?minSignal=2`
- GET /api/statistics
- GET /health

## Configuration

Voir `src/config/database.config.js` et `docker-compose.yml`. Le service utilise le réseau Docker par défaut partagé avec Moodle.
