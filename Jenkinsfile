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
                    echo "Starting deployment..."
                    bat "docker-compose down || true"
                    bat "docker-compose up -d --remove-orphans"
                    echo "Deployment completed successfully."
                }
            }
        }
    }

    post {
        always {
            echo 'Pipeline finished.'
        }
        success {
            echo 'Build and Dockerization successful!'
        }
        failure {
            echo 'Pipeline failed. Please check the logs.'
        }
    }
}

