import discord
import asyncio
from constant.Constants import BIRTHDAY_CHECK_TICK_IN_SECONDS, INTRO_TIMER_CHECK_TICK_IN_SECONDS, AUTO_DISCONNECT_TICK_IN_SECONDS, USER_ID_TO_INTRO_FILE_MAP
from featureFlags.feature_flags import ENABLE_INTRO_SONGS

def createTasks(client, bot_instance):
    client.loop.create_task(check_intro_timer(client, bot_instance))
    client.loop.create_task(listen_for_voice_channel_join(client, bot_instance))
    client.loop.create_task(automatic_disconnect(client))
    client.loop.create_task(check_birthdays(bot_instance))
    
async def check_intro_timer(client, bot_instance):
    while True:
        if bot_instance.introTimer['active'] and bot_instance.introTimer['timer'] == 0:
            bot_instance.set_intro_timer(False, 0)

        elif bot_instance.introTimer['active'] and bot_instance.introTimer['timer'] > 0:
            bot_instance.introTimer['timer'] -= INTRO_TIMER_CHECK_TICK_IN_SECONDS
            
        await asyncio.sleep(INTRO_TIMER_CHECK_TICK_IN_SECONDS)


async def listen_for_voice_channel_join(client, bot_instance):
    @client.event
    async def on_voice_state_update(member, before, after):
        if (ENABLE_INTRO_SONGS):
            # Only act if a user joins a voice channel
            intro_timer_active = bot_instance.is_intro_timer_active()
            channel_state_valid = before.channel != after.channel and after.channel is not None
            has_intro_audio = USER_ID_TO_INTRO_FILE_MAP.get(member.id, None) is not None
            intro_audio_path = USER_ID_TO_INTRO_FILE_MAP.get(member.id, None)

            # Intro timer check 
            if has_intro_audio and channel_state_valid and not member.bot and not intro_timer_active:

                current_voice_client = discord.utils.get(client.voice_clients, guild=member.guild)

                # If bot is already in a different voice channel, leave it
                if current_voice_client and current_voice_client.channel != after.channel:
                    await current_voice_client.disconnect()

                # Join the new channel if not already there
                if not current_voice_client or current_voice_client.channel != after.channel:
                    await after.channel.connect()
                    bot_instance.set_intro_timer(True, 5)
                    source=discord.FFmpegPCMAudio(executable='ffmpeg', source=intro_audio_path)

                    new_voice_client = discord.utils.get(client.voice_clients, guild=member.guild)
                    new_voice_client.play(source)

async def automatic_disconnect(client):
    '''
    After 10 minutes of inactivity, disconnect from whatever channel the bot is in
    '''
    while True:
        voice_client = discord.utils.get(client.voice_clients)
        if voice_client and voice_client.is_connected() and not voice_client.is_playing():
            await voice_client.disconnect()

        await asyncio.sleep(AUTO_DISCONNECT_TICK_IN_SECONDS)

async def check_birthdays(bot_instance):
    while True:
        birthdays = await bot_instance.get_current_user_birthdays()
        for birthday_object in birthdays:
            await bot_instance.announce_birthday(birthday_object)

        await asyncio.sleep(BIRTHDAY_CHECK_TICK_IN_SECONDS)