pipeline {
    agent any
    triggers {
        githubPush()
    }

    environment {
        DOCKER_REGISTRY = 'edupath'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        stage('Build & Tag Docker Images') {
            steps {
                script {
                    def services = [
                        'api-gateway': 'microservices/api-gateway',
                        'lms-connector': 'microservices/lms-connector',
                        'student-profiler': 'microservices/student-profiler',
                        'student-coach-api': 'microservices/student-coach-api',
                        'path-predictor': 'microservices/path-predictor',
                        'prepa-data': 'microservices/prepa-data',
                        'recco-builder': 'microservices/recco-builder',
                        'teacher-console-api': 'microservices/teacher-console-api',
                        'teacher-console': 'microservices/TeacherConsole'
                    ]

                    def stages = [:]

                    services.each { name, path ->
                        stages["Build ${name}"] = {
                            dir(path) {
                                echo "Building Docker image for ${name}"
                                bat "docker build -t ${DOCKER_REGISTRY}/${name}:${env.BUILD_NUMBER} -t ${DOCKER_REGISTRY}/${name}:latest ."
                            }
                        }
                    }

                    parallel stages
                }
            }
        }

        stage('Verification') {
            steps {
                echo "Pipeline execution completed successfully."
                bat 'docker images | findstr edupath'
            }
        }

        stage('Deploy') {
            steps {
                script {
                    echo "=== Starting Automatic Deployment ==="
                    // Use a fixed project name to avoid conflicts with fluctuating workspace folder names
                    // Stop and remove existing containers, networks, and orphan services
                    // Command commented out to avoid stopping containers during deployment in this environment
                    // bat "docker-compose -p edupath-ms down --remove-orphans || true"

                    echo "=== Deploying New Version ==="
                    // Start services in detached mode with orphan removal
                    bat "docker-compose -p edupath-ms up -d --remove-orphans"
                    
                    echo "=== Deployment Successful ==="
                }
            }
        }
    }

    post {
        always {
            echo '=== Pipeline Finished: Cleaning Up ==='
            script {
                // Remove containers and networks to avoid conflicts with future commits/runs
                // Commented out to prevent automatic stopping/removal during CI runs in this environment
                // bat "docker-compose -p edupath-ms down --remove-orphans || true"
            }
        }
        success {
            echo 'Build, Dockerization, and Deployment verification successful!'
        }
        failure {
            echo 'Pipeline failed. Please check the logs for errors during build or deployment.'
        }
    }
}
