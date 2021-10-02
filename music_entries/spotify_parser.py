import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

import environ

env = environ.Env()

environ.Env.read_env()

#
# Used to get info about song from spotify api
#

class SpotifyMusicEntry:
    title = ""
    artist = ""
    genre = ""
    type = ""
    link = ""

    def __str__(self):
        return self.type + ": " + self.title + " - " + self.artist


class SpotifyParser:
    # TODO: put this in .env

    client_id = env("spotify_id")
    client_secret = env("spotify_secret")

    client_credentials_manager : SpotifyClientCredentials
    sp : spotipy.Spotify

    def __init__(self):
        self.client_credentials_manager = SpotifyClientCredentials(
            self.client_id, self.client_secret
        )
        self.sp = spotipy.Spotify(
            client_credentials_manager=self.client_credentials_manager
        )

    def parse(self, link):
        ls = link.split("/")

        _type = ls[-2]

        try:
            if _type == "album":
                # Get album info from spotify
                album = self.sp.album(link)

                # Parse it to SpotifyMusicEntry
                entry = SpotifyMusicEntry()
                entry.title = album["name"]
                entry.artist = album["artists"][0]["name"]
                if len(album["genres"]) > 0:
                    entry.genre = album["genres"][0]
                else:
                    entry.genre = ""
                entry.type = "album"
                entry.link = link
                return entry

            elif _type == "track":
                # Get track info from spotify
                track = self.sp.track(link)

                # Parse it to SpotifyMusicEntry
                entry = SpotifyMusicEntry()
                entry.title = track["name"]
                entry.artist = track["artists"][0]["name"]
                entry.genre = ""
                entry.type = "song"
                entry.link = link
                return entry

            elif _type == "playlist":
                # Get track info from spotify
                playlist = self.sp.playlist(link)

                # Parse it to SpotifyMusicEntry
                entry = SpotifyMusicEntry()
                entry.title = playlist["name"]
                entry.artist = "Various Artists"
                entry.genre = ""
                entry.type = "mix"
                entry.link = link
                return entry

        except spotipy.exceptions.SpotifyException as e:
            return None


if __name__ == "__main__":
    parser = SpotifyParser()
    # TODO: refactor this to a proper test
    print(
        parser.parse(
            "https://open.spotify.com/album/4Carzsnpd6yvuHZ49I0oz8?si=pZf1mDwDSquIvToPTbVi1Q"
        )
    )
    print(
        parser.parse(
            "https://open.spotify.com/track/3rBOkpPCniY6AxOIavGGsg?si=kx3FPr_XRpqiZbg7tRSrHQ"
        )
    )
    print(
        parser.parse(
            "https://open.spotify.com/user/spotify/playlist/37i9dQZF1DX5OepaGriAIm?si=JtDxFk07RYG8mOAeWudMgQ"
        )
    )
