import aiohttp

from constant.Constants import RIFT_WATCHER_ENDPOINT


class RiftWatcherClient:
    def __init__(self):
        self.server_url = RIFT_WATCHER_ENDPOINT

    async def get_player_overview(
        self,
        game_name: str,
        tag_line: str,
        region: str,
    ):
        async with aiohttp.ClientSession() as session:
            async with session.get(
                self.server_url + "/player/overview",
                params={
                    "game_name": game_name,
                    "tag_line": tag_line,
                    "region": region,
                },
            ) as response:
                response.raise_for_status()
                return await response.json()