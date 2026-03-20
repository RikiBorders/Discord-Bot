import discord
from discord import app_commands
from dotenv import load_dotenv
import os
import logging

from Bot import Bot
from util.embed_utils import *
from util.discord_task_utils import *
from logger_config.logger import configure_logging, get_logger

configure_logging()
logger = get_logger(__name__)

'''
The everlasting legacy of Wiz, Sayori, Tanaka, and Goose.
'''
botInstance = Bot()
client = botInstance.get_client()

@client.tree.command(
        name="help",
        description="Displays the bot help menu",
)
async def help(interaction: discord.Interaction):
    await interaction.response.send_message(
        ephemeral=True,
        embed=build_help_embed().to_discord_embed()
    )

@client.tree.command(
        name="sharerules",
        description="Sends a message containing the server rules",
)
@app_commands.checks.has_permissions(administrator=True)
@app_commands.describe(channel_id="channel_id")
async def sharerules(interaction: discord.Interaction, channel_id: str):
    await botInstance.send_rules_message(interaction, channel_id)

@client.tree.command(
        name="announce",
        description="Sends an announcement to the announcement channel.",
)
@app_commands.checks.has_permissions(administrator=True)
@app_commands.describe(description="announcement_description", title="announcement_title")
async def announce(interaction: discord.Interaction, title: str, description: str):
    await botInstance.send_announcement_message(interaction, title, description)

def bot_booter():
    load_dotenv()
    key = os.getenv("DISCORD_KEY")
    client.run(key)


@client.event
async def on_ready():
    logger.info(f'Logged in as {client.user}')
    createTasks(client, botInstance)


@client.event
async def on_member_join(member: discord.Member):
    # Set the default role for new members
    if botInstance.has_default_role(member.guild.id):
        default_role_name = botInstance.get_default_role(member.guild.id)
        await botInstance.set_role(default_role_name, member)

    await botInstance.send_on_member_join_messages(member)


# Test commands available only in the beta environment

# This command needs to be run to register the slash commands with Discord. It will sync commands to ALL server
@client.command()
async def sync_commands(ctx, *params):
    if os.getenv("STAGE") == "beta":
        await client.tree.sync()
        await ctx.send("Commands synced")

        
if __name__ == "__main__":
    bot_booter()
    