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
                script {
                    checkout([
                        $class: 'GitSCM',
                        branches: scm.branches,
                        doGenerateSubmoduleConfigurations: scm.doGenerateSubmoduleConfigurations,
                        extensions: scm.extensions + [
                            [$class: 'CloneOption', depth: 1, noTags: false, reference: '', shallow: true, timeout: 30],
                            [$class: 'WipeWorkspace']
                        ],
                        userRemoteConfigs: scm.userRemoteConfigs
                    ])
                }
            }
        }

        stage('Start Infrastructure') {
            steps {
                script {
                    // Start PostgreSQL, RabbitMQ, MLFlow, Elasticsearch, MinIO, MoodleDB, LMSDB, MoodleApp, and Airflow
                    bat "docker-compose -p edupath-ms up -d postgres rabbitmq mlflow elasticsearch minio moodledb lmsdb moodleapp airflow-init airflow-webserver airflow-scheduler"
                }
            }
        }

        stage('Backend Microservices') {
            parallel {
                
                stage('Eureka Server') {
                    stages {
                        stage('Build Eureka') {
                            steps {
                                dir('microservices/eureka-server') {
                                    script {
                                        echo "Building Eureka Server..."
                                        bat "docker build -t ${DOCKER_REGISTRY}/eureka-server:${env.BUILD_NUMBER} -t ${DOCKER_REGISTRY}/eureka-server:latest ."
                                    }
                                }
                            }
                        }
                        stage('Deploy Eureka') {
                            steps {
                                script {
                                    echo "Deploying Eureka Server..."
                                    bat "docker-compose -p edupath-ms up -d --no-deps --force-recreate eureka-server"
                                }
                            }
                        }
                    }
                }

                stage('API Gateway') {
                    stages {
                        stage('Build Gateway') {
                            steps {
                                dir('microservices/api-gateway') {
                                    script {
                                        echo "Building API Gateway..."
                                        bat "docker build -t ${DOCKER_REGISTRY}/api-gateway:${env.BUILD_NUMBER} -t ${DOCKER_REGISTRY}/api-gateway:latest ."
                                    }
                                }
                            }
                        }
                        stage('Deploy Gateway') {
                            steps {
                                script {
                                    echo "Deploying API Gateway..."
                                    bat "docker-compose -p edupath-ms up -d --no-deps --force-recreate api-gateway"
                                }
                            }
                        }
                    }
                }

                stage('LMS Connector') {
                    stages {
                        stage('Build LMS Connector') {
                            steps {
                                dir('microservices/lms-connector') {
                                    script {
                                        echo "Building LMS Connector..."
                                        bat "docker build -t ${DOCKER_REGISTRY}/lms-connector:${env.BUILD_NUMBER} -t ${DOCKER_REGISTRY}/lms-connector:latest ."
                                    }
                                }
                            }
                        }
                        stage('Deploy LMS Connector') {
                            steps {
                                script {
                                    echo "Deploying LMS Connector..."
                                    bat "docker-compose -p edupath-ms up -d --no-deps --force-recreate lms-connector"
                                }
                            }
                        }
                    }
                }

                stage('Student Profiler') {
                    stages {
                        stage('Build Profiler') {
                            steps {
                                dir('microservices/student-profiler') {
                                    script {
                                        echo "Building Student Profiler..."
                                        bat "docker build -t ${DOCKER_REGISTRY}/student-profiler:${env.BUILD_NUMBER} -t ${DOCKER_REGISTRY}/student-profiler:latest ."
                                    }
                                }
                            }
                        }
                        stage('Deploy Profiler') {
                            steps {
                                script {
                                    echo "Deploying Student Profiler..."
                                    bat "docker-compose -p edupath-ms up -d --no-deps --force-recreate student-profiler"
                                }
                            }
                        }
                    }
                }

                stage('Student Coach API') {
                    stages {
                        stage('Build Coach API') {
                            steps {
                                dir('microservices/student-coach-api') {
                                    script {
                                        echo "Building Student Coach API..."
                                        bat "docker build -t ${DOCKER_REGISTRY}/student-coach-api:${env.BUILD_NUMBER} -t ${DOCKER_REGISTRY}/student-coach-api:latest ."
                                    }
                                }
                            }
                        }
                        stage('Deploy Coach API') {
                            steps {
                                script {
                                    echo "Deploying Student Coach API..."
                                    bat "docker-compose -p edupath-ms up -d --no-deps --force-recreate student-coach-api"
                                }
                            }
                        }
                    }
                }

                stage('Path Predictor') {
                    stages {
                        stage('Build Predictor') {
                            steps {
                                dir('microservices/path-predictor') {
                                    script {
                                        echo "Building Path Predictor..."
                                        bat "docker build -t ${DOCKER_REGISTRY}/path-predictor:${env.BUILD_NUMBER} -t ${DOCKER_REGISTRY}/path-predictor:latest ."
                                    }
                                }
                            }
                        }
                        stage('Deploy Predictor') {
                            steps {
                                script {
                                    echo "Deploying Path Predictor..."
                                    bat "docker-compose -p edupath-ms up -d --no-deps --force-recreate path-predictor"
                                }
                            }
                        }
                    }
                }

                stage('Prepa Data') {
                    stages {
                        stage('Build PrepaData') {
                            steps {
                                dir('microservices/prepa-data') {
                                    script {
                                        echo "Building Prepa Data..."
                                        bat "docker build -t ${DOCKER_REGISTRY}/prepa-data:${env.BUILD_NUMBER} -t ${DOCKER_REGISTRY}/prepa-data:latest ."
                                    }
                                }
                            }
                        }
                        stage('Deploy PrepaData') {
                            steps {
                                script {
                                    echo "Deploying Prepa Data..."
                                    bat "docker-compose -p edupath-ms up -d --no-deps --force-recreate prepadata"
                                }
                            }
                        }
                    }
                }

                stage('Reco Builder') {
                    stages {
                        stage('Build Reco') {
                            steps {
                                dir('microservices/reco-builder') { 
                                    script {
                                        echo "Building Reco Builder..."
                                        bat "docker build -t ${DOCKER_REGISTRY}/reco-builder:${env.BUILD_NUMBER} -t ${DOCKER_REGISTRY}/reco-builder:latest ."
                                    }
                                }
                            }
                        }
                        stage('Deploy Reco') {
                            steps {
                                script {
                                    echo "Deploying Reco Builder..."
                                    bat "docker-compose -p edupath-ms up -d --no-deps --force-recreate reco-builder"
                                }
                            }
                        }
                    }
                }

                stage('Teacher Console API') {
                    stages {
                        stage('Build TC API') {
                            steps {
                                dir('microservices/teacher-console-api') {
                                    script {
                                        echo "Building Teacher Console API..."
                                        bat "docker build -t ${DOCKER_REGISTRY}/teacher-console-api:${env.BUILD_NUMBER} -t ${DOCKER_REGISTRY}/teacher-console-api:latest ."
                                    }
                                }
                            }
                        }
                        stage('Deploy TC API') {
                            steps {
                                script {
                                    echo "Deploying Teacher Console API..."
                                    bat "docker-compose -p edupath-ms up -d --no-deps --force-recreate teacher-console-api"
                                }
                            }
                        }
                    }
                }

            }
        }

        stage('Client Applications') {
            parallel {

                stage('Teacher Console') {
                    stages {
                        stage('Build Teacher Console') {
                            steps {
                                dir('microservices/TeacherConsole') {
                                    script {
                                        echo "Building TeacherConsole (Frontend)..."
                                        bat "docker build -t ${DOCKER_REGISTRY}/teacher-console:${env.BUILD_NUMBER} -t ${DOCKER_REGISTRY}/teacher-console:latest ."
                                    }
                                }
                            }
                        }
                        stage('Deploy Teacher Console') {
                            steps {
                                script {
                                    echo "Deploying TeacherConsole (Frontend)..."
                                    bat "docker-compose -p edupath-ms up -d --no-deps --force-recreate teacher-console"
                                }
                            }
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
            echo 'SUCCESS: All microservices and mobile front built.'
            echo '=== Access Links ==='
            echo 'Teacher Console: http://localhost:8088'
            echo 'Moodle: http://localhost'
            echo 'Eureka: http://localhost:8761'
            echo 'Airflow: http://localhost:8081'
            echo 'MLFlow: http://localhost:5001'
            echo 'MinIO: http://localhost:9002'
            echo 'App Gateway: http://localhost:4000'
        }
        failure {
            echo 'FAILURE: One or more stages failed.'
        }
    }
}
