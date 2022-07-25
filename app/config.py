from pydantic import BaseSettings


class Settings(BaseSettings):
    database_username: str
    database_password: str
    database_address: str
    database_port: str
    database_name: str
    database_driver: str

    token_secret: str
    token_algorithm: str
    token_expire_seconds: int

    admin_username: str
    admin_password: str

    testing_admin_username: str = "admin"
    testing_admin_password: str = "admin"

    class Config:
        env_file = ".env"


settings = Settings()
