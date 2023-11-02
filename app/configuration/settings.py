import celery
from pydantic import Field
from pydantic_settings import BaseSettings
from authlib.integrations.starlette_client import OAuth

class Settings(BaseSettings):
    db_name: str = Field(..., env='DB_NAME')
    db_username: str = Field(..., env='DB_USERNAME')
    db_password: str = Field(..., env='DB_PASSWORD')
    db_port: str = Field(..., env='DB_PORT')
    celery_backend_url: str = Field(..., env='CELERY_BACKEND_URL')
    # oauth_client_id: str = Field(..., env='OAUTH_CLIENT_ID')
    oauth_client_id: str = "65a232fb-fc61-46a8-9818-aa3777269130"
    # oauth_client_secret: str = Field(..., env='OAUTH_CLIENT_SECRET')
    oauth_client_secret: str = "0h4ilhKtV8FVKBYX46Nd6112C8xpKVUWmH10piNJ"
    # oauth_authorize_redirect_path: str = Field(..., env='OAUTH_AUTHORIZE_REDIRECT_PATH')
    oauth_authorize_redirect_path: str = "https://cs2-backend.evom.dev/api/v1/users/login/callback"
    # JWT
    # jwt_secret_key: str = "9f63d3214da92c45a40d3866a5fb93e998afca753a557fee0de7ba8d6551767c"
    # jwt_algorithm: str = 'HS256'
    # access_token_expire_minutes: int = 1000


settings = Settings()
