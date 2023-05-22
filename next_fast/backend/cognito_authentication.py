from fastapi_cognito import CognitoAuth, CognitoSettings
from pydantic import BaseSettings


class Settings(BaseSettings):
    check_expiration = True
    jwt_header_prefix = "Bearer"
    jwt_header_name = "Authorization"
    userpools = {"us": {"region": "us-east-2", "userpool_id": "us-east-2_vpCRfIvXD",
        "app_client_id": "66fovpj4vcp9488lb9o7n3rv58"}}


settings = Settings()
cognito_us = CognitoAuth(settings=CognitoSettings.from_global_settings(settings), userpool_name="us")
