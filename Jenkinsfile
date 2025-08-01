pipeline {
    agent any   
    environment {
        // These should be defined in Jenkins as environment variables or credentials
        OPENAI_API_KEY = "${env.OPENAI_API_KEY}"
        GRADIO_USERNAME = "${env.GRADIO_USERNAME}"
        GRADIO_PASSWORD = "${env.GRADIO_PASSWORD}"
    } 
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
            stage('Create Environment File') {
                steps {
                    sh '''
                    cat > .env <<ENV
                        OPENAI_API_KEY=${OPENAI_API_KEY}
                        GRADIO_USERNAME=${GRADIO_USERNAME}
                        GRADIO_PASSWORD=${GRADIO_PASSWORD}
                        ENV
                    '''
                }
            }
            stage('Deploy Container') {
                steps {
                    sh '''           
                    # Stop and remove existing container if running
                    if [ "$(docker ps -aq -f name=stock_agent)" ]; then
                        docker rm -f stock_agent
                    fi 
                    # Run new container        
                    docker run -d --env-file .env -p 7860:7860 --name stock_agent stock_agent
                    '''
                }
            }
        }
}