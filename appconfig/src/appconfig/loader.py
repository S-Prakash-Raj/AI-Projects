from pydantic import ValidationError

from appconfig.models import AppSettings

class ConfigError(Exception):
    pass

def format_errors(exc: ValidationError) -> str:
        lines = []
        for err in exc.errors(include_url=False,include_input=False):
            field = ".".join(str(part) for part in err["loc"]) or "<root>"
            lines.append(f"{field}:{err['msg']}")
        return "\n".join(lines)

def load_settings() -> AppSettings:
        try:
            return AppSettings()
        except ValidationError as exc:
            raise ConfigError(format_errors(exc)) from None