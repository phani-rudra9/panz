pipeline {
  agent any
  triggers {
    pollSCM '* * * * *'
  }
  stages {
   stage('Docker build and push') {
      steps {
        sh '''
         whoami
         DOCKER_LOGIN_PASSWORD=$(aws ecr get-login-password  --region ap-south-1)
         docker login -u AWS -p $DOCKER_LOGIN_PASSWORD https://971076122335.dkr.ecr.ap-south-1.amazonaws.com
         docker build -t 971076122335.dkr.ecr.ap-south-1.amazonaws.com/demo:SAMPLE-PROJECT-${BUILD_NUMBER} .
         docker push 351836203514.dkr.ecr.ap-south-1.amazonaws.com/demo:SAMPLE-PROJECT-${BUILD_NUMBER}
          
	  '''
     }   
   }

    stage('Image Scan') {
      steps {
        sh '''
        chmod +x image_scan.sh
        bash image_scan.sh
          
	  '''
     }   
   }
    // stage('eks deploy') {
    //   steps {
	      
    //     sh '''
    //        aws eks update-kubeconfig --name demo --regio ap-south-1
    //        sed "s/buildNumber/${BUILD_NUMBER}/g" deploy.yml > deploy-new.yml
	//    kubectl apply -f deploy-new.yml
	//    kubectl apply -f svc.yml
	// '''
    //   }   
    // }
    stage('ecs deploy') {
      steps {
        sh '''
          chmod +x changebuildnumber.sh
          ./changebuildnumber.sh $BUILD_NUMBER
	  sh -x ecs-auto.sh
          '''
     }    
    }
}
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

}
