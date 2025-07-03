pipeline {
    agent any   
        stages {
            stage('Clone Repository') {
                    /* Cloning the repository to our workspace */
                    steps {
                    checkout scm
                }
            }
            stage('Build Docker Image') {
                steps {
                    sh 'docker build -t stock_agent .'
                }
            }

            stage('Deploy Container') {
                steps {
                    sh '''
                    cat > .env <<ENV
    OPENAI_API_KEY=${OPENAI_API_KEY}
    GRADIO_USERNAME=${GRADIO_USERNAME}
    GRADIO_PASSWORD=${GRADIO_PASSWORD}
    ENV
                    docker run -d --env-file .env -p 7860:7860 --name stock_agent stock_agent
                    '''
                }
            }
        }
}