# Jenkins CI/CD Configuration

## Vue d'ensemble

Ce projet utilise Jenkins pour l'intégration continue et le déploiement continu (CI/CD) de tous les microservices EduPath-MS.

## Configuration Jenkins

### 1. Accès à Jenkins

- **URL** : http://localhost:8080
- **Port Agent** : 50000

### 2. Premier Démarrage

Lors du premier démarrage, récupérez le mot de passe initial :

```bash
docker exec jenkins_server cat /var/jenkins_home/secrets/initialAdminPassword
```

### 3. Plugins Requis

Installez les plugins suivants via Jenkins UI :

- **Docker Pipeline** : Pour les commandes Docker dans le pipeline
- **Docker Compose Build Step** : Pour docker-compose
- **Git** : Pour le contrôle de version
- **Pipeline** : Pour les Jenkinsfiles
- **Blue Ocean** : Interface moderne (optionnel)
- **Slack Notification** : Notifications (optionnel)
- **Email Extension** : Notifications email (optionnel)

### 4. Credentials

Configurez les credentials dans Jenkins :

1. Allez dans **Manage Jenkins** → **Manage Credentials**
2. Ajoutez les credentials suivants :

   - **dockerhub-credentials** : Username/Password pour Docker Hub
   - **github-token** : Token GitHub pour accès au repository
   - **postgres-credentials** : Credentials PostgreSQL (si nécessaire)

## Pipeline Stages

Le pipeline Jenkins comprend les étapes suivantes :

### 1. **Checkout**
- Clone le repository Git
- Récupère le code source

### 2. **Environment Setup**
- Vérifie les versions Docker et Docker Compose
- Prépare l'environnement de build

### 3. **Build Services**
- Build tous les microservices en parallèle
- Crée les images Docker

### 4. **Run Tests**
- Exécute les tests unitaires pour chaque microservice :
  - LMS Connector (Node.js)
  - PrepaData (Python)
  - StudentProfiler (Python)
  - PathPredictor (Python)
  - RecoBuilder (Python)

### 5. **Code Quality Analysis**
- Analyse statique du code (Pylint, ESLint)
- Vérification des standards de code

### 6. **Security Scan**
- Scan des images Docker pour les vulnérabilités
- Analyse de sécurité

### 7. **Deploy to Staging** (branche `develop`)
- Déploiement automatique en staging
- Vérification de la santé des services

### 8. **Integration Tests** (branche `develop`)
- Tests d'intégration end-to-end
- Vérification des endpoints API

### 9. **Tag and Push Images** (branche `main`)
- Tag des images avec le numéro de build
- Push vers le registry Docker

### 10. **Deploy to Production** (branche `main`)
- Déploiement en production avec validation manuelle
- Nécessite une approbation

## Branches Strategy

- **`main`** : Production - Déploiement automatique après approbation
- **`develop`** : Staging - Déploiement automatique
- **`feature/*`** : Build et tests uniquement

## Variables d'Environnement

Les variables suivantes sont configurées dans le Jenkinsfile :

```groovy
DOCKER_COMPOSE_VERSION = '1.29.2'
PROJECT_NAME = 'edupath-ms'
REGISTRY = 'docker.io'
REGISTRY_CREDENTIAL = 'dockerhub-credentials'
```

## Création d'un Job Jenkins

### Via Blue Ocean (Recommandé)

1. Ouvrez Jenkins : http://localhost:8080
2. Cliquez sur **Open Blue Ocean**
3. Cliquez sur **New Pipeline**
4. Sélectionnez **Git**
5. Entrez l'URL du repository : `https://github.com/NisrineLachguer/EduPath-MS.git`
6. Sélectionnez le Jenkinsfile
7. Cliquez sur **Create Pipeline**

### Via Interface Classique

1. Allez dans **New Item**
2. Entrez le nom : `EduPath-MS-Pipeline`
3. Sélectionnez **Pipeline**
4. Dans **Pipeline** → **Definition**, sélectionnez **Pipeline script from SCM**
5. **SCM** : Git
6. **Repository URL** : `https://github.com/NisrineLachguer/EduPath-MS.git`
7. **Script Path** : `Jenkinsfile`
8. Sauvegardez

## Webhooks GitHub

Pour déclencher automatiquement le pipeline lors des commits :

1. Allez dans les paramètres du repository GitHub
2. **Settings** → **Webhooks** → **Add webhook**
3. **Payload URL** : `http://your-jenkins-url:8080/github-webhook/`
4. **Content type** : `application/json`
5. **Events** : Just the push event
6. Sauvegardez

## Notifications

### Slack

Ajoutez dans le Jenkinsfile (section `post`) :

```groovy
success {
    slackSend(
        color: 'good',
        message: "Build #${BUILD_NUMBER} succeeded for ${JOB_NAME}"
    )
}
failure {
    slackSend(
        color: 'danger',
        message: "Build #${BUILD_NUMBER} failed for ${JOB_NAME}"
    )
}
```

### Email

Configurez SMTP dans **Manage Jenkins** → **Configure System** → **Extended E-mail Notification**

## Monitoring

### Logs

Consultez les logs du pipeline :

```bash
# Logs Jenkins
docker logs jenkins_server

# Logs du dernier build
docker exec jenkins_server cat /var/jenkins_home/jobs/EduPath-MS-Pipeline/builds/lastBuild/log
```

### Artifacts

Les artifacts sont archivés automatiquement :
- `docker-compose-logs.txt` : Logs de tous les services

## Troubleshooting

### Problème : Docker socket permission denied

**Solution** :
```bash
docker exec -u root jenkins_server chmod 666 /var/run/docker.sock
```

### Problème : Build timeout

**Solution** : Augmentez le timeout dans le Jenkinsfile :
```groovy
options {
    timeout(time: 1, unit: 'HOURS')
}
```

### Problème : Out of memory

**Solution** : Augmentez la mémoire Java dans docker-compose.yml :
```yaml
environment:
  JAVA_OPTS: "-Xmx2048m -Xms512m"
```

## Commandes Utiles

```bash
# Démarrer Jenkins
docker-compose up -d jenkins

# Arrêter Jenkins
docker-compose stop jenkins

# Redémarrer Jenkins
docker-compose restart jenkins

# Voir les logs
docker logs -f jenkins_server

# Backup Jenkins
docker exec jenkins_server tar czf /tmp/jenkins_backup.tar.gz /var/jenkins_home
docker cp jenkins_server:/tmp/jenkins_backup.tar.gz ./jenkins_backup.tar.gz

# Restore Jenkins
docker cp ./jenkins_backup.tar.gz jenkins_server:/tmp/
docker exec jenkins_server tar xzf /tmp/jenkins_backup.tar.gz -C /
```

## Sécurité

### Bonnes Pratiques

1. **Changez le mot de passe admin** après la première connexion
2. **Activez HTTPS** pour la production
3. **Limitez les permissions** des utilisateurs
4. **Utilisez des credentials** pour les secrets
5. **Activez l'authentification** (LDAP, OAuth, etc.)
6. **Mettez à jour régulièrement** Jenkins et les plugins

### Configuration HTTPS (Production)

Utilisez un reverse proxy (Nginx) :

```nginx
server {
    listen 443 ssl;
    server_name jenkins.yourdomain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Ressources

- [Documentation Jenkins](https://www.jenkins.io/doc/)
- [Pipeline Syntax](https://www.jenkins.io/doc/book/pipeline/syntax/)
- [Docker Pipeline Plugin](https://plugins.jenkins.io/docker-workflow/)
- [Blue Ocean](https://www.jenkins.io/doc/book/blueocean/)
