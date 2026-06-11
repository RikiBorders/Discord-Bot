from secrets import choice

import discord
from discord.ext import commands
import json
from datetime import date
from client.rift_watcher_client import RiftWatcherClient
from logger_config.logger import get_logger

from client.supabase_client import SupabaseClient
from exception.no_channel_found_exception import NoChannelFoundException
from typing import Optional
from helper.guild_configuration_manager_helper import RULES_KEY, GuildConfigurationManagerHelper
from text.embed_strings import BIRTHDAY_TITLES
from util.embed_utils import build_birthday_embed, build_welcome_embed, build_announcement_embed, build_rules_embed
from constant.Constants import ANNOUNCEMENT_CHANNEL_TYPE

logger = get_logger(__name__)


class Bot():

    def __init__(self):
        self.client = self.create_client()
        self.supabase_client = SupabaseClient()
        self.guild_configuration_manager_helper = GuildConfigurationManagerHelper(supabase_client=self.supabase_client)
        self.rift_watcher_client = RiftWatcherClient()
        self.introTimer = {
            'active': False, 
            'current_time': 0
        }
        logger.info("Bot initialized successfully")

    def create_client(self):
        intents = discord.Intents.default()
        intents.members = True
        intents.message_content = True
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
    
    def get_image_urls_for_birthday_embed(self, configuration_data) -> list[str]:
        return configuration_data['image_urls']['birthday_image_urls']
    
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
        # TODO: Fix number tranlsations (1th, 2th, 3th) via a new input sanitation util function
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

    async def announce_birthday(self, birthday_object: dict):
        announcement_channel_id = birthday_object.get("announcement_channel_id")
        guild_id = birthday_object.get("guild_id")
        if not announcement_channel_id:
            logger.warning(
                "Skipping birthday announcement because announcement_channel_id is missing: %s",
                birthday_object
            )
            return

        try:
            channel = await self.client.fetch_channel(announcement_channel_id)
        except Exception as e:
            logger.warning(
                "Could not fetch announcement channel %s for guild %s: %s",
                announcement_channel_id,
                guild_id,
                e
            )
            return

        if channel.guild is None or channel.guild.id != guild_id:
            logger.warning(
                "Announcement channel %s does not belong to guild %s",
                announcement_channel_id,
                guild_id
            )
            return

        config_data = self.guild_configuration_manager_helper.get_configuration(guild_id)
        image_urls = self.get_image_urls_for_birthday_embed(config_data)
        user_id = birthday_object.get("user_id")
        title = choice(BIRTHDAY_TITLES)
        description = f"Everyone, wish <@{user_id}> a very happy birthday!"

        try:
            await channel.send(
                embed=build_birthday_embed(title, description, image_urls).to_discord_embed()
            )
            logger.info(
                "Sent birthday announcement for user_id %s in guild %s to channel %s",
                user_id,
                guild_id,
                announcement_channel_id
            )
        except Exception as e:
            logger.error(
                "Error sending birthday announcement to channel %s: %s",
                announcement_channel_id,
                e
            )

    async def send_rules_message(self, interaction: discord.Interaction, channel: discord.TextChannel):
        guild_id = self.get_guild_id_from_interaction(interaction)
        config_data = self.guild_configuration_manager_helper.get_configuration(guild_id)
        rules = config_data.get(RULES_KEY, [])

        await channel.send(
            embed=build_rules_embed(rules).to_discord_embed()
        )
        await interaction.response.send_message(
            content=f'Rules shared in {channel.mention}.',
            ephemeral=True
        )
            
    async def get_player_overview(self, game_name: str, tag_line: str, region: str):
        rift_watcher_response = await self.rift_watcher_client.get_player_overview(
            game_name=game_name,
            tag_line=tag_line,
            region=region
        )
        print(f"Rift watcher response for {game_name}#{tag_line} in region {region}: {rift_watcher_response}")

        puuid = rift_watcher_response["puuid"]
        display_name = rift_watcher_response["display_name"]
        region = rift_watcher_response["region"]
        rank = rift_watcher_response["rank"]
        ranked_tier = rift_watcher_response["ranked_tier"]
        ranked_division = rift_watcher_response["ranked_division"]
        flex_rank = rift_watcher_response["flex_rank"]
        flex_ranked_division = rift_watcher_response["flex_ranked_division"]

        solo_rank = rank
        if ranked_tier or ranked_division:
            tier_division = " ".join(filter(None, [ranked_tier, ranked_division]))
            solo_rank = f"{tier_division} ({rank})" if rank else tier_division

        flex_rank_display = flex_rank
        if flex_ranked_division:
            flex_rank_display = f"{flex_ranked_division} ({flex_rank})" if flex_rank else flex_ranked_division

        return {
            "puuid": puuid,
            "display_name": display_name,
            "region": region,
            "solo_rank": solo_rank,
            "flex_rank_display": flex_rank_display
        }
    
    async def get_current_user_birthdays(self):
        '''
        Get the birthdays for the current day for a given guild.
        '''
        current_date = date.today().isoformat()

        birthdays = self.supabase_client.get_current_birthdays(date=current_date)
        logger.info(f"Birthdays fetched for date {current_date}: {birthdays}")

        if isinstance(birthdays, dict) and "data" in birthdays:
            birthdays = birthdays["data"]

        parsed_birthdays = []
        for record in birthdays or []:
            guild_id = record.get("guild_id")
            user_id = record.get("user_id")

            announcement_config = record.get("guild_birthday_configurations")
            announcement_channel_id = None
            if isinstance(announcement_config, list) and announcement_config:
                announcement_channel_id = announcement_config[0].get("announcement_channel_id")
            elif isinstance(announcement_config, dict):
                announcement_channel_id = announcement_config.get("announcement_channel_id")

            if guild_id is None or user_id is None or announcement_channel_id is None:
                logger.warning(
                    "Skipping invalid birthday record from Supabase: %s",
                    record
                )
                continue

            parsed_birthdays.append({
                "guild_id": guild_id,
                "user_id": user_id,
                "announcement_channel_id": announcement_channel_id
            })
        logger.info(f"Parsed birthdays for date {current_date}: {parsed_birthdays}")
        return parsed_birthdays
