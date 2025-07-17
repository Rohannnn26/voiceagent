import boto3
from botocore.exceptions import ClientError
import json
from monitoring.logger.logger import Logger
log = Logger()


def get_secret(env) :

    log.info(f"Fetching secrets for environment: {env}")
    secret_name = f"{env}/chatbot/secrets"  #modify dev and uat using environment variables
    region_name = "ap-south-1"

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        # For a list of exceptions thrown, see
        # https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
        raise e

    secret = get_secret_value_response['SecretString']
    
    return json.loads(secret)