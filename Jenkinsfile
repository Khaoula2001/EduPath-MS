pipeline {
    agent any

    environment {
        DOCKER_REGISTRY = 'edupath'
        BUILD_NUMBER = "${env.BUILD_NUMBER}"
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build & Install Dependencies') {
            parallel {
                stage('Node.js services') {
                    steps {
                        dir('microservices/api-gateway') {
                            sh 'npm install'
                        }
                        dir('microservices/lms-connector') {
                            sh 'npm install'
                        }
                    }
                }
                stage('Python services') {
                    steps {
                        script {
                            def pythonServices = [
                                'microservices/student-profiler',
                                'microservices/student-coach-api',
                                'microservices/path-predictor',
                                'microservices/prepa-data',
                                'microservices/recco-builder',
                                'microservices/teacher-console-api'
                            ]
                            pythonServices.each { service ->
                                dir(service) {
                                    echo "Installing dependencies for ${service}"
                                    // sh 'python -m venv venv && . venv/bin/activate && pip install -r requirements.txt'
                                    // Alternative if venv is not desired in workspace:
                                    sh 'pip install -r requirements.txt'
                                }
                            }
                        }
                    }
                }
                stage('Angular Frontend') {
                    steps {
                        dir('microservices/TeacherConsole') {
                            sh 'npm install'
                            sh 'npm run build'
                        }
                    }
                }
            }
        }

        stage('Dockerize') {
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
                        'teacher-console-api': 'microservices/teacher-console-api'
                    ]

                    services.each { name, path ->
                        echo "Building Docker image for ${name}"
                        sh "docker build -t ${DOCKER_REGISTRY}/${name}:${BUILD_NUMBER} -t ${DOCKER_REGISTRY}/${name}:latest ${path}"
                    }
                }
            }
        }

        stage('Verification') {
            steps {
                echo "Pipeline execution completed successfully."
                sh 'docker images | grep edupath'
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
