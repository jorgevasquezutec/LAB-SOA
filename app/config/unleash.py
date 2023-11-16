from app.config.settings import api_settings
from UnleashClient import UnleashClient

class UnleashClientManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(UnleashClientManager, cls).__new__(cls)
            cls._instance._unleash_client = UnleashClient(
                url=api_settings.UNLEASH_URL,
                app_name=api_settings.TITLE,
                custom_headers={"Authorization": api_settings.UNLEASH_TOKEN},
            )
            cls._instance._unleash_client.initialize_client()
        return cls._instance

    @property
    def unleash_client(self):
        return self._instance._unleash_client

# Uso
unleash_manager = UnleashClientManager()
unleash_client = unleash_manager.unleash_client