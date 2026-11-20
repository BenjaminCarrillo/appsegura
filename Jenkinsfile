pipeline {
    agent any

    stages {
        stage('Build') {
            steps {
                echo 'Etapa Build: revisando los archivos del proyecto'
                sh 'ls -la'
            }
        }

        stage('Test') {
            steps {
                echo 'Etapa Test: verificando que existan los archivos necesarios'
                sh 'test -f app.py && echo "OK: app.py existe"'
                sh 'test -f requirements.txt && echo "OK: requirements.txt existe"'
                sh 'test -f Dockerfile && echo "OK: Dockerfile existe"'
            }
        }

        stage('Analyze') {
            steps {
                echo 'Etapa Analyze: revision basica de seguridad del codigo'
                sh '''
                    if grep -n "debug=True" app.py; then
                        echo "ALERTA: modo debug activado"; exit 1
                    else
                        echo "OK: el modo debug esta desactivado"
                    fi
                '''
                sh '''
                    if grep -niE "(password|secret|api_key) *= *['\\"]" app.py; then
                        echo "ALERTA: posible contrasena escrita en el codigo"; exit 1
                    else
                        echo "OK: no se encontraron contrasenas en el codigo"
                    fi
                '''
            }
        }

        stage('Deploy') {
            steps {
                echo 'Etapa Deploy: despliegue simulado de appsegura'
                echo 'En un entorno real aqui se ejecutaria: docker build -t appsegura . && docker run -d -p 5000:5000 appsegura'
            }
        }
    }

    post {
        success { echo 'Pipeline finalizado correctamente' }
        failure { echo 'El pipeline fallo: revisar las etapas' }
    }
}
