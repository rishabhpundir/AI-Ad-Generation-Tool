pipeline {
    agent any

    environment {
        DEPLOY_DIR = "/home/stillbloom/HyrosAdTool"
        VENV_DIR = "/home/stillbloom/venv"
    }

    stages {
        stage('Cleanup') {
            steps {
                script {
                    echo "Running Cleanup..."
                    sh '''
                    sudo bash scripts/cleanup.sh || exit 1
                    '''
                }
            }
        }

        stage('Debug Workspace') {
            steps {
                sh '''
                echo "Workspace directory: $WORKSPACE"
                ls -la $WORKSPACE
                '''
            }
        }

        stage('Copy Workspace to /home/stillbloom') {
            steps {
                script {
                    echo "Copying workspace to $DEPLOY_DIR..."
                    sh '''
                    sudo mkdir -p /home/stillbloom
                    sudo rsync -av --delete $WORKSPACE/ $DEPLOY_DIR/
                    sudo chown -R jenkins:jenkins /home/stillbloom
                    sudo chmod -R 2775 /home/stillbloom
                    '''
                }
            }
        }

        stage('Deployment') {
            steps {
                script {
                    echo "Starting Deployment..."
                    sh '''
                    sudo bash scripts/deploy.sh || exit 1
                    '''
                }
            }
        }
    }

    post {
        always {
            echo 'Pipeline execution finished!'
        }
        success {
            echo 'Deployment successful!'
        }
        failure {
            echo 'Deployment failed!'
        }
    }
}
