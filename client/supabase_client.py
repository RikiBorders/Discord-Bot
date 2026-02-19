from dotenv import load_dotenv
import os
from supabase import create_client, Client
from logger_config.logger import get_logger

logger = get_logger(__name__)

class SupabaseClient:
    def __init__(self):
        load_dotenv()
        self.url = os.environ.get("SUPABASE_URL")
        self.key = os.environ.get("SUPABASE_KEY")
        self.password = os.environ.get("SUPABASE_PASSWORD")

        # Initialize connection to Supabase here
        self.client = create_client(self.url, self.key)
        logger.info("Supabase client initialized successfully")
    
    def get_server_data(self, guild_id: int) -> dict:
        response = (
            self.client
            .table("server_configurations")
            .select("*")
            .eq("guild_id", guild_id)
            .execute()
        )
        logger.info(f"Fetched server data for guild_id {guild_id} from Supabase: {response}")
        return response