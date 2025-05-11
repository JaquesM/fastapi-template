import boto3

from app.core.config import settings


def get_aws_session():
    if settings.ENVIRONMENT == "local":
        return boto3.Session(profile_name='prod')
    
    else:
        return boto3.Session(region_name='us-east-1')


