from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    cle_secrete: str = "cle_de_secours_uniquement_pour_les_tests_locaux_32_chars"
    origins_autorisees: str = "*"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
