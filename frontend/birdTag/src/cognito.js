
import { CognitoUserPool } from 'amazon-cognito-identity-js'

const poolData = {
  UserPoolId: 'us-east-1_nyFLr2L5V',
  ClientId: '4atsi0gdvl985s56h3kcg702nv',
}

const userPool = new CognitoUserPool(poolData)

export { userPool }