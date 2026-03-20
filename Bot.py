import discord
from discord.ext import commands
import json
from logger_config.logger import get_logger

from client.supabase_client import SupabaseClient
from exception.no_channel_found_exception import NoChannelFoundException
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
    
    def get_default_role(self, guild_id: int) -> Optional[int]:
        guild_configuration = self.guild_configuration_manager_helper.get_configuration(guild_id)
        return guild_configuration.get('default_role', None)
    
    def get_image_urls_for_welcome_embed(self, configuration_data: dict) -> list[str]:
        return configuration_data['image_urls']['welcome_image_urls']
    
    def get_image_urls_for_announcement_embed(self, configuration_data) -> list[str]:
        return configuration_data['image_urls']['announcement_image_urls']
    
    def get_guild_id_from_interaction(self, interaction: discord.Interaction) -> int:
        return interaction.guild_id
    
    def get_channel_id_by_channel_type(self, configuration_data: dict, channel_type: str) -> Optional[int]:
        channels = configuration_data.get('channels', {})
        channel_id = channels.get(channel_type, None)
        if not channel_id:
            logger.warning(f"Channel ID for {channel_type} not found in configuration.")
            raise NoChannelFoundException(f"Channel ID for {channel_type} not found in configuration.")
        return channel_id

    def has_default_role(self, guild_id: int) -> bool:
        default_role = self.get_default_role(guild_id)
        return True if default_role else False

    def is_intro_timer_active(self):
        return self.introTimer['active']

    def set_intro_timer(self, status: bool, time_in_seconds: int):
        self.introTimer['active'] = status
        self.introTimer['timer'] = time_in_seconds

    def is_interaction_guild_equal_to_target_channel_id(self, interaction_guild_id: int, channel: discord.abc.GuildChannel) -> bool:
        return interaction_guild_id == channel.guild.id

    async def set_role(self , role_name: str, member):
        role = discord.utils.get(member.guild.roles, name=role_name)
        if role:
            await member.add_roles(role)
            logger.info(f"Assigned default role {role.name} to new member {member.name}")

    async def send_on_member_join_messages(self, member: discord.Member):
        system_channel_id = member.guild.system_channel.id
        member_count = len([m for m in member.guild.members])
        guild_config_data = self.guild_configuration_manager_helper.get_configuration(member.guild.id)
        channel = await self.client.fetch_channel(system_channel_id)

        await channel.send(f"{member.mention}")
        await channel.send(
            embed=build_welcome_embed(member_count, self.get_image_urls_for_welcome_embed(guild_config_data)).to_discord_embed()
        )

    async def send_announcement_message(self, interaction: discord.Interaction, title: str, description: str):
        guild_id = self.get_guild_id_from_interaction(interaction)
        config_data = self.guild_configuration_manager_helper.get_configuration(guild_id)

        image_urls = self.get_image_urls_for_announcement_embed(config_data)
        announcement_channel_id = self.get_channel_id_by_channel_type(config_data, ANNOUNCEMENT_CHANNEL_TYPE)
        channel = await self.client.fetch_channel(announcement_channel_id)

        try:
            if self.is_interaction_guild_equal_to_target_channel_id(guild_id, channel):
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
        if self.is_interaction_guild_equal_to_target_channel_id(interaction.guild_id, channel):
            await channel.send(
                embed=build_rules_embed(rules).to_discord_embed()
        )