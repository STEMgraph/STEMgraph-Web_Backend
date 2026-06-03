import requests
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError

from config import KEYCLOAK_URL, REALM

security = HTTPBearer()


def get_jwks():
    url = f"{KEYCLOAK_URL}/realms/{REALM}/protocol/openid-connect/certs"
    response = requests.get(url)
    return response.json()


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        jwks = get_jwks()
        payload = jwt.decode(
            token,
            jwks,
            algorithms=["RS256"],
            options={"verify_aud": False}
        )
        return {
            "sub": payload.get("sub"),
            "roles": payload.get("realm_access", {}).get("roles", [])
        }
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


optional_security = HTTPBearer(auto_error=False)


def get_optional_user(credentials: HTTPAuthorizationCredentials = Depends(optional_security)):
    if not credentials:
        return {"sub": "0", "roles": []}
    try:
        jwks = get_jwks()
        payload = jwt.decode(
            credentials.credentials,
            jwks,
            algorithms=["RS256"],
            options={"verify_aud": False}
        )
        return {
            "sub": payload.get("sub"),
            "roles": payload.get("realm_access", {}).get("roles", [])
        }
    except JWTError:
        return {"sub": "0", "roles": []}
