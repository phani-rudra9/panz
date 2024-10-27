pipeline {
  agent any
  // triggers {
  //   pollSCM '* * * * *'
  // }
  environment {
    BRANCH_NAME = "master"
    REPO_NAME = "panz"
    SONAR_PROJECT_KEY = "demo"
    IMAGE_TAG = "demo-project-${BUILD_NUMBER}"
    DOCKER_REPO_URL = "971076122335.dkr.ecr.us-east-2.amazonaws.com"
    DOCKER_REPO_NAME = "demo"
  }
  stages {
    stage('Git checkout') {
      steps {
        checkout([
            $class: 'GitSCM',
            branches: [[name: "*/${BRANCH_NAME}"]],
            userRemoteConfigs: [[credentialsId: 'git-creds', url: "https://github.com/phani-rudra9/${REPO_NAME}"]]
        ])       
     }   
   }
   stage('sonar scanner') {
      steps {
        sh '''
	dotnet tool install --global dotnet-sonarscanner --version 6.2.0
        export PATH="$PATH:/var/lib/jenkins/.dotnet/tools"
      	dotnet sonarscanner begin /k:"$SONAR_PROJECT_KEY" /d:sonar.host.url="$SONAR_HOST_URL" /d:sonar.login="$SONAR_TOKEN"
        dotnet build
        dotnet sonarscanner end /d:sonar.login="$SONAR_TOKEN"
  
	  '''
     }   
   }
   stage('Sonar Quality Gate Check') {
      steps {
        sh '''
	sleep 20
        chmod +x sonar_scan.sh
        bash sonar_scan.sh
          
	  '''
     }   
   }
   stage('Docker build and push') {
      steps {
        sh '''
         whoami
         DOCKER_LOGIN_PASSWORD=$(aws ecr get-login-password  --region us-east-2)
         docker login -u AWS -p $DOCKER_LOGIN_PASSWORD https://$DOCKER_REPO_URL
         docker build -t $DOCKER_REPO_URL/$DOCKER_REPO_NAME:$IMAGE_TAG .
         docker push $DOCKER_REPO_URL/$DOCKER_REPO_NAME:$IMAGE_TAG
	    '''
     }   
   }

    stage('Image Scan') {
      steps {
        sh '''
    	sleep 29
        chmod +x image_scan.sh
        bash image_scan.sh     
	  '''
     }   
   }
//      stage('argocd deploy') {
//       steps {
//         sh '''
//         aws eks update-kubeconfig --name demo --region us-east-2
//   	    sed "s/changebuildnumber/${BUILD_NUMBER}/g" kubernetes/deploy.yml
//             git clone https://github.com/mahigandham142/panz.git
// 	    git add kubernetes/deploy.yml
//             git commit "eks deployment"
// 	    git push -u origin master
  
//   	  '''
//      }   
//    }
	  
   stage('eks deploy') {
     steps {
       sh '''
            export AWS_ACCESS_KEY_ID=$Access_Key
	    export AWS_SECRET_ACCESS_KEY=$Secret_Key
	    export AWS_DEFAULT_REGION=us-east-2
            aws eks update-kubeconfig --name sample --region us-east-2
  	    sed "s/changebuildnumber/${BUILD_NUMBER}/g" deploy.yml
  	    kubectl apply -f deploy.yml
  	    // kubectl apply -f svc.yml
  
  	  '''
    }   
  }
}
}
//       stage('ecs deploy') {
//       steps {
//           sh '''
//           chmod +x changebuildnumber.sh
//             ./changebuildnumber.sh $BUILD_NUMBER
//	     sh -x ecs-auto.sh
//             '''
//        }    
//       }
// }
// post {
//     failure {
//         mail to: 'unsolveddevops@gmail.com',
//              subject: "Failed Pipeline: ${BUILD_NUMBER}",
//              body: "Something is wrong with ${env.BUILD_URL}"
//     }
//      success {
//         mail to: 'unsolveddevops@gmail.com',
//              subject: "successful Pipeline:  ${env.BUILD_NUMBER}",
//              body: "Your pipeline is success ${env.BUILD_URL}"
//     }
// }
