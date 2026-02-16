import discord
from discord.ext import commands
import json
from logger_config.logger import get_logger

from client.supabase_client import SupabaseClient
from exception.record_not_found_exception import RecordNotFoundError
from typing import Optional
from helper.guild_configuration_manager_helper import RULES_KEY, GuildConfigurationManagerHelper
from util.embed_utils import build_welcome_embed, build_announcement_embed, build_rules_embed
from constant.Constants import ANNOUNCEMENT_CHANNEL_TYPE

logger = get_logger(__name__)


class Bot():

    def __init__(self):
        self.client = self.create_client()
        self.guild_configuration_manager_helper = GuildConfigurationManagerHelper()
        self.introTimer = {
            'active': False, 
            'current_time': 0
        }
        self.supabase_client = SupabaseClient()
        self.server_data = self.get_server_data_from_supabase()
        self.guild_id = self.set_guild_id()
        logger.info("Bot initialized successfully")

    def create_client(self):
        intents = discord.Intents.all()
        intents.voice_states = True
        client = commands.Bot(command_prefix='.', intents=intents)
        client.remove_command('help')

        return client
    
    def get_client(self):
        return self.client

    def create_kick_petition(self):
        pass
    
    def get_server_data_from_supabase(self) -> dict:
        '''
        TODO: need to find a way to get the guild id for different servers so we can pull server data. Alternatively, the database will need to be restructured to not rely on guild_id as the primary key for server data.
        '''
        response = self.supabase_client.get_server_data(367021007690792961) # We key server data off of guild id

        data = getattr(response, "data", None)
        if not data:
            raise RecordNotFoundError(f"Server data not found for guild_id {self.guild_id}")

        columns = data[0] if isinstance(data, list) else data
        return columns if isinstance(columns, dict) else {}
    
    def get_default_role(self) -> Optional[int]:
        return self.server_data['default_role']
    
    def get_image_urls_for_welcome_embed(self) -> list[str]:
        return self.server_data['image_urls']['welcome_image_urls']
    
    def get_image_urls_for_announcement_embed(self, configuration_data) -> list[str]:
        return configuration_data['image_urls']['announcement_image_urls']
    
    def get_guild_id(self) -> int:
        #TODO: This needs to be deprecated. We shoudlnt store the guild id since the bot serves all guilds
        return self.guild_id

    def get_guild_id_from_interaction(self, interaction: discord.Interaction) -> int:
        return interaction.guild_id

    def has_default_role(self) -> bool:
        default_role = self.server_data['default_role']
        return True if default_role else False

    def is_intro_timer_active(self):
        return self.introTimer['active']

    def set_guild_id(self) -> int:
        # For now, return a hardcoded guild ID. In the future, this could be dynamic.
        return self.server_data['guild_id']
    
    def set_intro_timer(self, status: bool, time_in_seconds: int):
        self.introTimer['active'] = status
        self.introTimer['timer'] = time_in_seconds

    def is_interaction_guild_equal_to_target_channel_id(self, interaction_guild_id: int, channel_id: int) -> bool:
        channel_guild_id = self.client.get_channel(channel_id).guild.id
        return interaction_guild_id == channel_guild_id

    async def set_role(self , role_name: str, member):
        role = discord.utils.get(member.guild.roles, name=role_name)
        if role:
            await member.add_roles(role)
            logger.info(f"Assigned default role {role.name} to new member {member.name}")

    async def send_on_member_join_messages(self, member):
        system_channel_id = member.guild.system_channel.id
        member_count = len([m for m in member.guild.members])
        channel = await self.client.fetch_channel(system_channel_id)

        await channel.send(f"{member.mention}")
        await channel.send(
            embed=build_welcome_embed(member_count, self.get_image_urls_for_welcome_embed()).to_discord_embed()
        )

    async def send_announcement_message(self, interaction: discord.Interaction, title: str, description: str):
        guild_id = self.get_guild_id_from_interaction(interaction)
        config_data = self.guild_configuration_manager_helper.get_configuration(guild_id)

        image_urls = self.get_image_urls_for_announcement_embed(config_data)
        announcement_channel_id = self.get_channel_id_by_channel_type(config_data, ANNOUNCEMENT_CHANNEL_TYPE)
        channel = await self.client.fetch_channel(announcement_channel_id)

        try:
            if self.is_interaction_guild_equal_to_target_channel_id(guild_id, announcement_channel_id):
                await channel.send("@everyone")
                await channel.send(
                    embed=build_announcement_embed(title, description, image_urls).to_discord_embed()
                )
                await interaction.response.send_message(
                    ephemeral=True,
                    content="Announcement sent successfully."
                )
        except Exception as e:
            await interaction.response.send_message(
                ephemeral=True,
                content=f"Error sending announcement: {str(e)}"
            )

    async def send_rules_message(self, interaction: discord.Interaction, channel_id: str, ):
        guild_id = self.get_guild_id_from_interaction(interaction)
        config_data = self.guild_configuration_manager_helper.get_configuration(guild_id)
        rules = config_data.get(RULES_KEY, [])
        try:
            channel = await self.client.fetch_channel(channel_id)
        except discord.InvalidData as e:
            await interaction.response.send_message(
                ephemeral=True,
                content=f"Error: Could not find channel with ID {channel_id}. Exception: {str(e)}"
            )
            return
        if self.is_interaction_guild_equal_to_target_channel_id(interaction.guild_id, channel_id):
            await channel.send(
                embed=build_rules_embed(rules).to_discord_embed()
        )

    async def send_vote_kick_notification(self, interaction: discord.Interaction, user: discord.Member):
        #TODO: re-enable
        # moderator_channel_id = self.channel_registry_helper.get_channel_id("moderator")
        # channel = await self.client.fetch_channel(moderator_channel_id)

        # await channel.send(
        #     f"A vote to kick {user.mention} has passed the threshold. Please review and confirm the kick."
        # )
        pass
    