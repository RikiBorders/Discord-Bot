REQUEST_HEADERS = {'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36'}
INTRO_TIMER_CHECK_TICK_IN_SECONDS = 1  # Keep this set to one second. This way, the timer is updated every second.
AUTO_DISCONNECT_TICK_IN_SECONDS = 3  # Keep this set to one second. This way, the timer is updated every second.

INTRO_FILE_PATH = 'media/audio/'
USER_ID_TO_INTRO_FILE_MAP = {
    937798657443512340: INTRO_FILE_PATH+'your_time_has_come_intro.wav',  # Nick
    257557061448105996: INTRO_FILE_PATH+'charlie_hustle_intro.wav',  # Rik
    257643785448718336: INTRO_FILE_PATH+'KOTH2_intro.wav',  # Conner
    251134467924688901: INTRO_FILE_PATH+'lizard_intro.wav',  # Matty
}
BOT_NAME = "Evil Knight" # Should be in parity with the  bot's discord username (not strictly necessary)

ANNOUNCEMENT_CHANNEL_TYPE = "announcement_channel_id"
MODERATOR_CHANNEL_TYPE = "moderator_channel_id"