import spotipy
from spotipy.oauth2 import SpotifyClientCredentials


class SpotifyMusicEntry:
    title = ""
    artist = ""
    genre = ""
    _type = ""
    link = ""

    def __str__(self):
        return self.type + ": " + self.title + " - " + self.artist


class SpotifyParser:
    client_id = "01fb1a0794954cff8c27fd01e66beb9f"
    client_secret = "98e9f96d1b1940aa828efc6db1f2f893"

    client_credentials_manager = None
    sp = None

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
                album = self.sp.album(link)
                entry = SpotifyMusicEntry()
                entry.title = album["name"]
                entry.artist = album["artists"][0]["name"]
                if len(album["genres"]) > 0:
                    entry.genre = album["genres"][0]
                else:
                    entry.genre = ""
                entry._type = "album"
                entry.link = link
                return entry

            elif _type == "track":
                track = self.sp.track(link)
                entry = SpotifyMusicEntry()
                entry.title = track["name"]
                entry.artist = track["artists"][0]["name"]
                entry.genre = ""
                entry._type = "song"
                entry.link = link
                return entry

            elif _type == "playlist":
                playlist = self.sp.playlist(link)
                entry = SpotifyMusicEntry()
                entry.title = playlist["name"]
                entry.artist = "Various Artists"
                entry.genre = ""
                entry._type = "mix"
                entry.link = link
                return entry

        except spotipy.exceptions.SpotifyException as e:
            return None


if __name__ == "__main__":
    parser = SpotifyParser()
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
