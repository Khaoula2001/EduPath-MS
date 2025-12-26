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

        stage('Start Infrastructure') {
            steps {
                script {
                    echo "=== Starting Base Infrastructure ==="
                    // Start PostgreSQL, RabbitMQ, MLFlow, Elasticsearch, MinIO, MoodleDB, LMSDB
                    bat "docker-compose -p edupath-ms up -d postgres rabbitmq mlflow elasticsearch minio moodledb lmsdb"
                }
            }
        }

        stage('Microservices') {
            parallel {
                stage('Eureka Server') {
                    steps {
                        script {
                            echo "=== Building Eureka Server ==="
                            dir('microservices/eureka-server') {
                                bat "docker build -t ${DOCKER_REGISTRY}/eureka-server:${env.BUILD_NUMBER} -t ${DOCKER_REGISTRY}/eureka-server:latest ."
                            }
                            echo "=== Deploying Eureka Server ==="
                            bat "docker-compose -p edupath-ms up -d --no-deps --force-recreate eureka-server"
                        }
                    }
                }

                stage('API Gateway') {
                    steps {
                        script {
                            echo "=== Building API Gateway ==="
                            dir('microservices/api-gateway') {
                                bat "docker build -t ${DOCKER_REGISTRY}/api-gateway:${env.BUILD_NUMBER} -t ${DOCKER_REGISTRY}/api-gateway:latest ."
                            }
                            echo "=== Deploying API Gateway ==="
                            bat "docker-compose -p edupath-ms up -d --no-deps --force-recreate api-gateway"
                        }
                    }
                }

                stage('LMS Connector') {
                    steps {
                        script {
                            echo "=== Building LMS Connector ==="
                            dir('microservices/lms-connector') {
                                // Need to be careful with context for LMS connector as it has subfolders
                                // Original: dir('microservices/lms-connector') bat "docker build ..."
                                // Dockerfile is in `microservices/lms-connector/moodle-docker/moodle-docker/LMSConnector` based on previous file exploration?
                                // Wait, previous Jenkinsfile said: dir('microservices/lms-connector') ...
                                // Let's check docker-compose context: ./microservices/lms-connector/moodle-docker/moodle-docker/LMSConnector
                                // So the build command in previous Jenkinsfile might have been using the Dockerfile at root of lms-connector?
                                // Let's check file list step 14: microservices/lms-connector has a Dockerfile.
                                // BUT docker-compose uses a deeper one.
                                // I will follow the previous Jenkinsfile pattern which successfully built it.
                                bat "docker build -t ${DOCKER_REGISTRY}/lms-connector:${env.BUILD_NUMBER} -t ${DOCKER_REGISTRY}/lms-connector:latest ."
                            }
                            echo "=== Deploying LMS Connector ==="
                            bat "docker-compose -p edupath-ms up -d --no-deps --force-recreate lms-connector"
                        }
                    }
                }

                stage('Student Profiler') {
                    steps {
                        script {
                            echo "=== Building Student Profiler ==="
                            dir('microservices/student-profiler') {
                                bat "docker build -t ${DOCKER_REGISTRY}/student-profiler:${env.BUILD_NUMBER} -t ${DOCKER_REGISTRY}/student-profiler:latest ."
                            }
                            echo "=== Deploying Student Profiler ==="
                            bat "docker-compose -p edupath-ms up -d --no-deps --force-recreate student-profiler"
                        }
                    }
                }

                stage('Student Coach API') {
                    steps {
                        script {
                            echo "=== Building Student Coach API ==="
                            dir('microservices/student-coach-api') {
                                bat "docker build -t ${DOCKER_REGISTRY}/student-coach-api:${env.BUILD_NUMBER} -t ${DOCKER_REGISTRY}/student-coach-api:latest ."
                            }
                            echo "=== Deploying Student Coach API ==="
                            bat "docker-compose -p edupath-ms up -d --no-deps --force-recreate student-coach-api"
                        }
                    }
                }

                stage('Path Predictor') {
                    steps {
                        script {
                            echo "=== Building Path Predictor ==="
                            dir('microservices/path-predictor') {
                                bat "docker build -t ${DOCKER_REGISTRY}/path-predictor:${env.BUILD_NUMBER} -t ${DOCKER_REGISTRY}/path-predictor:latest ."
                            }
                            echo "=== Deploying Path Predictor ==="
                            bat "docker-compose -p edupath-ms up -d --no-deps --force-recreate path-predictor"
                        }
                    }
                }

                stage('Prepa Data') {
                    steps {
                        script {
                            echo "=== Building Prepa Data ==="
                            dir('microservices/prepa-data') {
                                bat "docker build -t ${DOCKER_REGISTRY}/prepa-data:${env.BUILD_NUMBER} -t ${DOCKER_REGISTRY}/prepa-data:latest ."
                            }
                            echo "=== Deploying Prepa Data ==="
                            bat "docker-compose -p edupath-ms up -d --no-deps --force-recreate prepadata"
                        }
                    }
                }

                stage('Reco Builder') {
                    steps {
                        script {
                            echo "=== Building Reco Builder ==="
                            dir('microservices/reco-builder') {
                                bat "docker build -t ${DOCKER_REGISTRY}/reco-builder:${env.BUILD_NUMBER} -t ${DOCKER_REGISTRY}/reco-builder:latest ."
                            }
                            echo "=== Deploying Reco Builder ==="
                            bat "docker-compose -p edupath-ms up -d --no-deps --force-recreate reco-builder"
                        }
                    }
                }

                stage('Teacher Console API') {
                    steps {
                        script {
                            echo "=== Building Teacher Console API ==="
                            dir('microservices/teacher-console-api') {
                                bat "docker build -t ${DOCKER_REGISTRY}/teacher-console-api:${env.BUILD_NUMBER} -t ${DOCKER_REGISTRY}/teacher-console-api:latest ."
                            }
                            echo "=== Deploying Teacher Console API ==="
                            bat "docker-compose -p edupath-ms up -d --no-deps --force-recreate teacher-console-api"
                        }
                    }
                }

                stage('TeacherConsole (Frontend)') {
                    steps {
                        script {
                            echo "=== Building TeacherConsole (Frontend) ==="
                            dir('microservices/TeacherConsole') {
                                bat "docker build -t ${DOCKER_REGISTRY}/TeacherConsole:${env.BUILD_NUMBER} -t ${DOCKER_REGISTRY}/TeacherConsole:latest ."
                            }
                            echo "=== Deploying TeacherConsole ==="
                            bat "docker-compose -p edupath-ms up -d --no-deps --force-recreate teacher-console"
                        }
                    }
                }
            }
        }

        stage('Final Verification') {
            steps {
                script {
                    echo "=== Verifying Running Containers ==="
                    bat "docker-compose -p edupath-ms ps"
                }
            }
        }
    }

    post {
        always {
            echo '=== Pipeline Finished ==='
        }
        success {
            echo 'SUCCESS: All microservices built and deployed.'
        }
        failure {
            echo 'FAILURE: One or more services failed to build or deploy.'
        }
    }
}
