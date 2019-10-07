import discord
from discord.ext import commands
from bs4 import BeautifulSoup as bs4
from urllib.request import urlopen
import asyncio
from mutagen.easyid3 import EasyID3
import youtube_dl
import os

# mostly the same as butty's voice player except with slightly less control because it's a radio

song_paths = ['path/to/folders/with/songs']

stations = {'station_name': 'path/to/.m3u'}

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)


class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

if not discord.opus.is_loaded():
    discord.opus.load_opus('opus.dll')

default_album = ['no album']
default_artist = ['no artist']

description = '''Change the playlist on Lizard Radio'''
bot = commands.Bot(command_prefix="r!", description=description)

@bot.event
async def on_ready():
    print("logged on")

async def currently_playing_loop():
    await bot.wait_until_ready()
    while not bot.is_closed():
        site = urlopen("http://icecast2_main_page.example").read()
        soup = bs4(site, "xml")
        songtitle = "{}.mp3".format(soup.find_all("tr")[-1].contents[1].contents[0])
        for path in song_paths:
            try:
                song = EasyID3("{}{}".format(path, songtitle))
                await bot.change_presence(activity=discord.Game(name="Playing: {} | {} | {}".format(song.get('title', songtitle)[0], song.get('album', default_album)[0], song.get('artist', default_artist)[0])))
            except Exception as e:
                print(e)
        await asyncio.sleep(10)

@bot.command(name="play", aliases=['join', 'j', 'p'])
async def play(ctx):
    if not ctx.author.voice:
        await ctx.send("Join a voice channel")
        return
    if not ctx.author.voice.channel.permissions_for(ctx.me).connect:
        await ctx.send("I don't have permission to join that channel")
    await ctx.author.voice.channel.connect()
    player = await YTDLSource.from_url("https://suchaperfectspeci.men/meme/radio", loop=bot.loop, stream=True)
    ctx.voice_client.play(player, after=lambda e: print('Player error: %s' % e) if e else None)
    await ctx.send("Joined voice channel")
    
@bot.command(name="playing", aliases=['cp'])
async def playing(ctx):
    site = urlopen("http://icecast2_main_page.example").read()
    soup = bs4(site, "xml")
    songtitle = "{}.mp3".format(soup.find_all("tr")[-1].contents[1].contents[0])
    for path in song_paths:
        try:
            song = EasyID3("{}{}".format(path, songtitle))
            await ctx.send("Playing: `{} | {} | {}`".format(song.get('title', songtitle)[0], song.get('album', default_album)[0], song.get('artist', default_artist)[0]))
        except Exception as e:
            print(e)

@bot.command(name="invite")
async def invite(ctx):
    await ctx.send("https://discordapp.com/oauth2/authorize?client_id=484034736231284737&scope=bot&permissions=3271713")

@bot.command(name="leave", aliases=['l'])
async def leave(ctx):
    await ctx.voice_client.disconnect()
    await ctx.send("Left voice channel")

@bot.command(name="station", aliases=['s'])
async def station(ctx, station : str):
    if ctx.author.id == 135496683009081345:
        os.system("cp {} tmp.m3u".format(stations[station]))
        os.rename("tmp.m3u", "playlist.m3u")
        os.system("killall -SIGHUP ezstream")
        await ctx.send("Station changed to `{}`, will start after this song".format(stations[station]))

bot.loop.create_task(currently_playing_loop())
bot.run(token)
