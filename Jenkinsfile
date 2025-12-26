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
            parallel {
                stage('api-gateway') {
                    steps {
                        dir('microservices/api-gateway') {
                            echo "Building Docker image for api-gateway"
                            bat "docker build -t ${DOCKER_REGISTRY}/api-gateway:${env.BUILD_NUMBER} -t ${DOCKER_REGISTRY}/api-gateway:latest ."
                        }
                    }
                }
                stage('lms-connector') {
                    steps {
                        dir('microservices/lms-connector') {
                            echo "Building Docker image for lms-connector"
                            bat "docker build -t ${DOCKER_REGISTRY}/lms-connector:${env.BUILD_NUMBER} -t ${DOCKER_REGISTRY}/lms-connector:latest ."
                        }
                    }
                }
                stage('student-profiler') {
                    steps {
                        dir('microservices/student-profiler') {
                            echo "Building Docker image for student-profiler"
                            bat "docker build -t ${DOCKER_REGISTRY}/student-profiler:${env.BUILD_NUMBER} -t ${DOCKER_REGISTRY}/student-profiler:latest ."
                        }
                    }
                }
                stage('student-coach-api') {
                    steps {
                        dir('microservices/student-coach-api') {
                            echo "Building Docker image for student-coach-api"
                            bat "docker build -t ${DOCKER_REGISTRY}/student-coach-api:${env.BUILD_NUMBER} -t ${DOCKER_REGISTRY}/student-coach-api:latest ."
                        }
                    }
                }
                stage('path-predictor') {
                    steps {
                        dir('microservices/path-predictor') {
                            echo "Building Docker image for path-predictor"
                            bat "docker build -t ${DOCKER_REGISTRY}/path-predictor:${env.BUILD_NUMBER} -t ${DOCKER_REGISTRY}/path-predictor:latest ."
                        }
                    }
                }
                stage('prepa-data') {
                    steps {
                        dir('microservices/prepa-data') {
                            echo "Building Docker image for prepa-data"
                            bat "docker build -t ${DOCKER_REGISTRY}/prepa-data:${env.BUILD_NUMBER} -t ${DOCKER_REGISTRY}/prepa-data:latest ."
                        }
                    }
                }
                stage('recco-builder') {
                    steps {
                        dir('microservices/recco-builder') {
                            echo "Building Docker image for recco-builder"
                            bat "docker build -t ${DOCKER_REGISTRY}/recco-builder:${env.BUILD_NUMBER} -t ${DOCKER_REGISTRY}/recco-builder:latest ."
                        }
                    }
                }
                stage('teacher-console-api') {
                    steps {
                        dir('microservices/teacher-console-api') {
                            echo "Building Docker image for teacher-console-api"
                            bat "docker build -t ${DOCKER_REGISTRY}/teacher-console-api:${env.BUILD_NUMBER} -t ${DOCKER_REGISTRY}/teacher-console-api:latest ."
                        }
                    }
                }
                stage('TeacherConsole') {
                    steps {
                        dir('microservices/TeacherConsole') {
                            echo "Building Docker image for TeacherConsole"
                            bat "docker build -t ${DOCKER_REGISTRY}/TeacherConsole:${env.BUILD_NUMBER} -t ${DOCKER_REGISTRY}/TeacherConsole:latest ."
                        }
                    }
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
            // Remove containers and networks to avoid conflicts with future commits/runs
            // Commented out to prevent automatic stopping/removal during CI runs in this environment
            // bat "docker-compose -p edupath-ms down --remove-orphans || true"

        }
        success {
            echo 'Build, Dockerization, and Deployment verification successful!'
        }
        failure {
            echo 'Pipeline failed. Please check the logs for errors during build or deployment.'
        }
    }
}
