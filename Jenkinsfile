pipeline {
    agent any

    stages {

        stage('Git Clone') {
            steps {
                git branch: 'main',
                url: 'https://github.com/a250048-lang/Smart-PG-DevOps.git'
            }
        }

        stage('Build Docker Image') {
            steps {
                bat 'docker build -t smartpg .'
            }
        }

        stage('Deploy') {
            steps {
                bat 'docker rm -f smartpg-container'
                bat 'docker run -d --name smartpg-container -p 8000:8000 smartpg'
            }
        }
    }
}