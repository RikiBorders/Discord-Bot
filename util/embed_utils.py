from model.embed import Embed
from text.help_menu_strings import HELP_MENU_DESCRIPTION
from text.embed_strings import WELCOME_EMBED_DESCRIPTIONS
from constant.Constants import BOT_NAME, EMOJI_MAP
from random import choice

def build_league_profile_embed(data: dict):
    description_lines = [
        f"Region: {data['region']}",
        f"Solo/Duo: {data['solo_rank']}",
        f"Flex: {data['flex_rank_display']}",
    ]
    solo_ranked_emoji = _get_rank_emoji(data['solo_rank'])
    flex_ranked_emoji = _get_rank_emoji(data['flex_rank_display'])
    if solo_ranked_emoji:
        description_lines[1] = f"Solo/Duo: {solo_ranked_emoji} {data['solo_rank']}"
    if flex_ranked_emoji:
        description_lines[2] = f"Flex: {flex_ranked_emoji} {data['flex_rank_display']}"

    embed = Embed(
        title=f"League of Legends Profile for {data['display_name']}",
        description="\n".join(description_lines),
        color=0xff0000
    )
    return embed

def build_help_embed():

    embed = Embed(
        title=f"{BOT_NAME} Help Menu",
        description=HELP_MENU_DESCRIPTION,
        color=0xff0000
    )
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

def build_birthday_embed(title: str, description: str, image_urls: list[str]):

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

def _get_rank_emoji(rank: str) -> str:
    rank_lower = rank.lower()
    emoji_markup = None
    emoji_key = None

    for key, value in EMOJI_MAP.items():
        if key in rank_lower:
            emoji_markup = value
            emoji_key = key
            break

    return emoji_markup