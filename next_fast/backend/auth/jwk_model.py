import logging
import os

import requests
from fastapi import Depends, HTTPException
from starlette.status import HTTP_403_FORBIDDEN

from auth.JWTBearer import JWKS, JWTBearer, JWTAuthorizationCredentials
from auth.cognito import cognito_get_user_email

COGNITO_REGION = 'us-east-2'
COGNITO_POOL_ID = 'us-east-2_vpCRfIvXD'

logger = logging.getLogger("fastapi")

jwks = JWKS.parse_obj(
    requests.get(
        f"https://cognito-idp.{COGNITO_REGION}.amazonaws.com/"
        f"{COGNITO_POOL_ID}/.well-known/jwks.json"
    ).json()
)

authenticate = JWTBearer(jwks)


async def get_current_user(
    credentials: JWTAuthorizationCredentials = Depends(authenticate)
) -> str:
    try:
        # email = cognito_get_user_email(credentials.claims["email"])
        return credentials.claims["email"]
    except KeyError:
        HTTPException(status_code=HTTP_403_FORBIDDEN, detail="username missing")
