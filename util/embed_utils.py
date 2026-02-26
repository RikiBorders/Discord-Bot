from model.embed import Embed
from text.help_menu_strings import HELP_MENU_DESCRIPTION, HELP_MENU_COMMANDS
from text.embed_strings import WELCOME_EMBED_DESCRIPTIONS
from constant.Constants import BOT_NAME
from random import choice

def build_help_embed():

    embed = Embed(
        title=f"{BOT_NAME} Help Menu",
        description=HELP_MENU_DESCRIPTION,
        color=0xff0000
    )
    ### SUGGESTION FOR SCALE-ABLE-ish CMDS DISPLAY IMPLEMENTATION ###
    for cmd, desc in HELP_MENU_COMMANDS.items():
        embed.add_field(name=cmd, value=desc, inline=False)
    return embed

def build_welcome_embed(member_count: int, image_urls: list[str]):

    embed = Embed(
        title="A New Member has Arrived!",
        description=choice(WELCOME_EMBED_DESCRIPTIONS),
        image_url=choice(image_urls),
        footer = f"You are the {member_count}th member!", # update this to use 2nd, th, st, etc
        color=0xff0000,
    )
    return embed

def build_announcement_embed(title: str, description: str, image_urls: list[str]):

    embed = Embed(
        title=title,
        description=description,
        image_url=choice(image_urls),
        color=0xff0000 
    )
    return embed

def build_rules_embed(rules: list[str]):

    rules_description = "\n".join([f"{idx+1}. {rule}" for idx, rule in enumerate(rules)])

    embed = Embed(
        title="Server Rules",
        description=rules_description,
        color=0xff0000 
    )
    return embed