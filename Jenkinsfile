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

        stage('Deploy using Ansible') {
    steps {
        bat 'ansible-playbook -i localhost, deploy.yml'
    }
}
    }
}