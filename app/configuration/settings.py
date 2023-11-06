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
    oauth_client_id: str = "cb0ff22f-2a68-4c58-97dc-fb2e50c06831"
    # oauth_client_secret: str = Field(..., env='OAUTH_CLIENT_SECRET')
    oauth_client_secret: str = "9ne2aL8JR1T8htrwMzKFmvt6FHnGTQPlHok6ytz4"
    # oauth_authorize_redirect_path: str = Field(..., env='OAUTH_AUTHORIZE_REDIRECT_PATH')
    oauth_authorize_redirect_path: str = "https://cs2-backend.evom.dev/api/v1/users/login/callback"
    faceit_api_key = "2a4e3640-5b2f-41a8-9be4-756476cfa0d6"
    leaderboard_id = "651da31af3e96d2044a35366"
    # JWT
    jwt_secret_key: str = "9f63d3214da92c45a40d3866a5fb93e998afca753a557fee0de7ba8d6551767c"
    jwt_algorithm: str = 'HS256'
    access_token_expire_minutes: int = 1000


settings = Settings()
