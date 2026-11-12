import os
from pathlib import Path
from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field, SecretStr, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict, PydanticBaseSettingsSource, TomlConfigSettingsSource


class _ProviderBase(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    api_key: SecretStr

    @field_validator("api_key")
    @classmethod
    def key_long_enough(cls, value:SecretStr) -> SecretStr:
       if len(value.get_secret_value()) < 10:
           raise ValueError("API key must be at least 10 characters long")
       return value

class OpenAIProvider(_ProviderBase):
    kind: Literal["openai"]
    model: str

class AntrophicProvider(_ProviderBase):
    kind: Literal["anthropic"]
    model: str

class AzureProvider(_ProviderBase):
    kind: Literal["azure"]
    endpoint: str
    deployment: str
    api_version: str
    @field_validator("endpoint")
    @classmethod
    def endpoint_is_https(cls, value:str)-> str:
        if not value.startswith("https://"):
         raise ValueError("Azure endpoint must start with https://")
        return value

Provider = Annotated[
    OpenAIProvider | AntrophicProvider | AzureProvider,
    Field(discriminator="kind")
]

class Limit(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    max_retires: Annotated[int, Field(ge=0, le=10)] = 3
    timeout_seconds: Annotated[float, Field(gt=0,le=300)] = 30.0
    backoff_base_seconds: Annotated[float, Field(gt=0,le=60)] = 1.0
    backoff_max_seconds: Annotated[float, Field(gt=0,le=600)] = 30.0

    @model_validator(mode="after")
    def backoff_max_not_below_base(self) -> "Limit":
        if self.backoff_max_seconds < self.backoff_base_seconds:
            raise ValueError("backoff_max_seconds must be >= backoff_base_seconds")
        return self


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="APP_",
        env_nested_delimiter="__",
        extra="forbid",
        frozen=True,
    )
    provider: Provider
    limits: Limit = Field(default_factory=Limit)

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource | None,
        env_settings: PydanticBaseSettingsSource | None,
        file_secret_settings: PydanticBaseSettingsSource | None,
        dotenv_settings: PydanticBaseSettingsSource | None,
        ) -> tuple[PydanticBaseSettingsSource, ...]:
        toml_path = Path(os.environ.get("APPCONFIG_FILE", "config.toml"))
        return (
            init_settings,
            env_settings,
            TomlConfigSettingsSource(settings_cls,toml_file=toml_path),
        ) 