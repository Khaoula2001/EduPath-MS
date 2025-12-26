pipeline {
    agent any
    triggers {
        githubPush()
    }

    environment {
        DOCKER_REGISTRY = 'edupath'
        // Assumes SonarQube is running from docker-compose
        SONAR_HOST_URL = 'http://localhost:9000' 
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
                    echo "=== Starting Base Infrastructure ==="
                    // Start PostgreSQL, RabbitMQ, MLFlow, Elasticsearch, MinIO, MoodleDB, LMSDB, and SonarQube
                    bat "docker-compose -p edupath-ms up -d postgres rabbitmq mlflow elasticsearch minio moodledb lmsdb sonarqube"
                    
                    // Wait for SonarQube to be ready (rudimentary check)
                    echo "Waiting for SonarQube to start..."
                    sleep 30
                }
            }
        }

        stage('Microservices & Frontend') {
            parallel {
                
                stage('Eureka Server') {
                    stages {
                        stage('Analysis Eureka') {
                            steps {
                                dir('microservices/eureka-server') {
                                    script {
                                        echo "Running SonarQube Analysis for Eureka Server..."
                                        // Java project uses Maven
                                        bat "mvn clean verify -DskipTests"
                                    }
                                }
                            }
                        }
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
                        stage('Analysis Gateway') {
                            steps {
                                dir('microservices/api-gateway') {
                                    script {
                                        echo "Running Analysis for API Gateway..."
                                        // Node.js project - using Dockerized Scanner
                                        // Note: We use host networking or point to host IP if needed.
                                        // For simplicity, assuming Jenkins runs on host and 'localhost' in container points to host if we use --network host (Linux) 
                                        // OR we use the service name if we attach to the network.
                                        // Let's attach to the network 'edupath-ms_default' (created by compose)
                                        // Network name is projectname_default -> edupath-ms_default
                                        bat "docker run --rm --network edupath-ms_default -v %CD%:/usr/src -w /usr/src sonarsource/sonar-scanner-cli -Dsonar.projectKey=api-gateway -Dsonar.sources=. -Dsonar.host.url=http://sonarqube:9000 -Dsonar.login=admin -Dsonar.password=admin"
                                    }
                                }
                            }
                        }
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
                        stage('Analysis LMS') {
                            steps {
                                dir('microservices/lms-connector') {
                                    script {
                                        echo "Running Analysis for LMS Connector..."
                                        bat "docker run --rm --network edupath-ms_default -v %CD%:/usr/src -w /usr/src sonarsource/sonar-scanner-cli -Dsonar.projectKey=lms-connector -Dsonar.sources=. -Dsonar.host.url=http://sonarqube:9000 -Dsonar.login=admin -Dsonar.password=admin"
                                    }
                                }
                            }
                        }
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
                        stage('Analysis Profiler') {
                            steps {
                                dir('microservices/student-profiler') {
                                    script {
                                        echo "Running Analysis for Student Profiler..."
                                        bat "docker run --rm --network edupath-ms_default -v %CD%:/usr/src -w /usr/src sonarsource/sonar-scanner-cli -Dsonar.projectKey=student-profiler -Dsonar.sources=. -Dsonar.host.url=http://sonarqube:9000 -Dsonar.login=admin -Dsonar.password=admin"
                                    }
                                }
                            }
                        }
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
                        stage('Analysis Coach') {
                            steps {
                                dir('microservices/student-coach-api') {
                                    script {
                                        echo "Running Analysis for Student Coach API..."
                                        bat "docker run --rm --network edupath-ms_default -v %CD%:/usr/src -w /usr/src sonarsource/sonar-scanner-cli -Dsonar.projectKey=student-coach-api -Dsonar.sources=. -Dsonar.host.url=http://sonarqube:9000 -Dsonar.login=admin -Dsonar.password=admin"
                                    }
                                }
                            }
                        }
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
                        stage('Analysis Predictor') {
                            steps {
                                dir('microservices/path-predictor') {
                                    script {
                                        echo "Running Analysis for Path Predictor..."
                                        bat "docker run --rm --network edupath-ms_default -v %CD%:/usr/src -w /usr/src sonarsource/sonar-scanner-cli -Dsonar.projectKey=path-predictor -Dsonar.sources=. -Dsonar.host.url=http://sonarqube:9000 -Dsonar.login=admin -Dsonar.password=admin"
                                    }
                                }
                            }
                        }
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
                        stage('Analysis PrepaData') {
                            steps {
                                dir('microservices/prepa-data') {
                                    script {
                                        echo "Running Analysis for Prepa Data..."
                                        bat "docker run --rm --network edupath-ms_default -v %CD%:/usr/src -w /usr/src sonarsource/sonar-scanner-cli -Dsonar.projectKey=prepa-data -Dsonar.sources=. -Dsonar.host.url=http://sonarqube:9000 -Dsonar.login=admin -Dsonar.password=admin"
                                    }
                                }
                            }
                        }
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
                        stage('Analysis Reco') {
                            steps {
                                dir('microservices/reco-builder') {
                                    script {
                                        echo "Running Analysis for Reco Builder..."
                                        bat "docker run --rm --network edupath-ms_default -v %CD%:/usr/src -w /usr/src sonarsource/sonar-scanner-cli -Dsonar.projectKey=reco-builder -Dsonar.sources=. -Dsonar.host.url=http://sonarqube:9000 -Dsonar.login=admin -Dsonar.password=admin"
                                    }
                                }
                            }
                        }
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
                        stage('Analysis TC API') {
                            steps {
                                dir('microservices/teacher-console-api') {
                                    script {
                                        echo "Running Analysis for Teacher Console API..."
                                        bat "docker run --rm --network edupath-ms_default -v %CD%:/usr/src -w /usr/src sonarsource/sonar-scanner-cli -Dsonar.projectKey=teacher-console-api -Dsonar.sources=. -Dsonar.host.url=http://sonarqube:9000 -Dsonar.login=admin -Dsonar.password=admin"
                                    }
                                }
                            }
                        }
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

                stage('Teacher Console (Web)') {
                    stages {
                        stage('Analysis TC Web') {
                            steps {
                                dir('microservices/TeacherConsole') {
                                    script {
                                        echo "Running Analysis for Teacher Console Web..."
                                        bat "docker run --rm --network edupath-ms_default -v %CD%:/usr/src -w /usr/src sonarsource/sonar-scanner-cli -Dsonar.projectKey=teacher-console-web -Dsonar.sources=. -Dsonar.host.url=http://sonarqube:9000 -Dsonar.login=admin -Dsonar.password=admin"
                                    }
                                }
                            }
                        }
                        stage('Build TC Web') {
                            steps {
                                dir('microservices/TeacherConsole') {
                                    script {
                                        echo "Building TeacherConsole (Frontend)..."
                                        bat "docker build -t ${DOCKER_REGISTRY}/teacher-console:${env.BUILD_NUMBER} -t ${DOCKER_REGISTRY}/teacher-console:latest ."
                                    }
                                }
                            }
                        }
                        stage('Deploy TC Web') {
                            steps {
                                script {
                                    echo "Deploying TeacherConsole (Frontend)..."
                                    bat "docker-compose -p edupath-ms up -d --no-deps --force-recreate teacher-console"
                                }
                            }
                        }
                    }
                }

                stage('Mobile Front') {
                    stages {
                        stage('Build APK') {
                            steps {
                                dir('microservices/student_coach/android') {
                                    script {
                                        echo "Building Android APK..."
                                        bat "docker run --rm -v %CD%:/project -w /project cimg/android:2024.01 bash -c \"gradle assembleDebug\""
                                    }
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
        }
        failure {
            echo 'FAILURE: One or more stages failed.'
        }
    }
}
