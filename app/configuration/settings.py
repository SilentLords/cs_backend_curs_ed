import celery
from pydantic import  Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    db_name: str = Field(..., env='DB_NAME')
    db_username: str = Field(..., env='DB_USERNAME')
    db_password : str = Field(..., env='DB_PASSWORD')
    db_port : str = Field(..., env='DB_PORT')
    celery_backend_url : str = Field(..., env='CELERY_BACKEND_URL')
    # JWT
    # jwt_secret_key: str = "9f63d3214da92c45a40d3866a5fb93e998afca753a557fee0de7ba8d6551767c"
    # jwt_algorithm: str = 'HS256'
    # access_token_expire_minutes: int = 1000


settings = Settings()
