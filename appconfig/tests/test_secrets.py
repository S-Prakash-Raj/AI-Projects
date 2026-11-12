from appconfig.loader import load_settings


SECRET = "sk-tes-asdasdsds2314234324324kjbcjaksbf"

def test_secret_not_in_repr_str_or_json(valid_config) -> None:
    settings = load_settings()
    for text in (repr(settings), str(settings), settings.model_dump_json()):
        assert SECRET not in text