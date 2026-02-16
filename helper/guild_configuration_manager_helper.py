from cachetools import TTLCache
from logger_config.logger import get_logger

from client.supabase_client import SupabaseClient
from exception.guild_not_found_exception import GuildNotFoundException
from exception.record_not_found_exception import RecordNotFoundError

logger = get_logger(__name__)

RULES_KEY = 'rules'

class GuildConfigurationManagerHelper:

    def __init__(self):
        self.config_object_ttl_in_seconds = 43200  # 12 hours in seconds
        self.max_size = 128
        self.cache = TTLCache(maxsize=self.max_size, ttl=self.config_object_ttl_in_seconds)
        self.supabase_client = SupabaseClient()

    def get_configuration(self, guild_id: int):
        if guild_id in self.cache:
            return self.cache[guild_id]

        # Fetch guild configuration and cache
        try:
            response = self.supabase_client.get_server_data(guild_id)
        except Exception as e:
            raise GuildNotFoundException(f"Guild with ID {guild_id} not found. Exception: {str(e)}")
        
        data = getattr(response, "data", None)
        if not data:
            raise RecordNotFoundError(f"Server data not found for guild_id {guild_id}")

        columns = data[0] if isinstance(data, list) else data
        configuration = columns if isinstance(columns, dict) else {}
        
        self.cache[guild_id] = configuration

        return configuration