import re
import string
import sqlite3

import discord
from discord.ext import commands

import nltk
from nltk.corpus import cmudict

from num2words import num2words


"""It's like that reddit one except worse probably"""


dictionary = cmudict.dict()

db = sqlite3.connect('haikus.db')
c = db.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS haikus
                          (title, description, author, date)''')

def count_syllables(word):
    syllables = 0
    try:    ## dictionary tends to be more accurate so it'll try to find the dictionary version of the word first, and if that fails use the regex
        definition = dictionary[word.lower()]   ## thanks nltk
        for char in definition[0]:
            if any(letter.isdigit() for letter in char):
                syllables += 1
    except Exception as e:  ## TODO find what the actual exception is here
        pattern = r'(?:[^laeiouy]es|ed|[^laeiouy]e)$'   ## honestly what even is regex
        word = re.sub(pattern, "", word)
        word = re.sub(r'^y', "", word)
        pattern = r'[aeiouy]{1,2}'
        res = re.findall(pattern, word)
        syllables += len(res)
    return syllables


def make_haiku(message):
    haikuthing = []
    syll = 0
    omessage = message.split()
    newmessage = ''.join(ch for ch in
                         [ch if not ch.isdigit() else "{}".format(num2words(ch)).replace("point zero", "") for ch in message]
                         if ch not in set(string.punctuation)).split()
    past_haikuthing = 0
    flag1 = 0
    flag2 = 0
    for word in newmessage:
        syll += count_syllables(word)
        haikuthing.append(word)
        if syll == 5:
            past_haikuthing = len(haikuthing)   ## TODO try to make this look nicer and let it accept words that are 6 or 7 syllables in case it overlaps
            omessage.insert(past_haikuthing, "\n")
            haikuthing = []
            flag1 = 1
        elif syll == 12:
            past_haikuthing += len(haikuthing)
            omessage.insert(past_haikuthing + 1, "\n")
            flag2 = 1
    if syll == 17 and flag1 and flag2:
        return ' '.join(omessage)

description = '''HaikuBot, I detect Haikus'''
bot = commands.Bot(command_prefix="##", description=description)


@bot.event
async def on_ready():
    print("logged on")
    await bot.change_presence(activity=discord.Game(name='Counting Syllables'))

@bot.event
async def on_message(message):
    if message.author.id != bot.user.id:
        haiku = make_haiku(message.content)
        if haiku:
            embed = discord.Embed(title="A Haiku by {}".format(message.author), description="\"{}\"".format(haiku), colour=discord.Colour.purple())
            embed.set_thumbnail(url=message.author.avatar_url)
            c.execute("INSERT INTO haikus VALUES(?, ?, ?)", (haiku, "A Haiku by {}".format(message.author), message.author.id, message.timestamp))
            await message.channel.send(embed=embed)
    await bot.process_commands(message)

@bot.command(name="records")
async def records(ctx, guild_id=None):
    if not guild_id:
        guild_id = ctx.guild.id
    async for message in ctx.channel.history(limit=2000):
        if message.author.id == 352117035620106240 and message.embeds:
            for embed in message.embeds:
                print(embed.description)

@bot.command(name="syll")
async def syll(ctx, *sentence):
    """counts the number of syllables in a message"""
    syll = 0
    sentence = ' '.join(sentence)
    newmessage = ''.join(ch if not ch.isdigit() else "{}".format(num2words(ch)).replace("point zero", "") for ch in sentence)
    sentence = ''.join(ch for ch in newmessage if ch not in set(string.punctuation)).split()
    for word in sentence:
        syll += count_syllables(word)
    await ctx.send("That was {} syllables imo".format(syll))

@bot.command(name="invite")
async def invite(ctx):
    await ctx.send("https://discordapp.com/oauth2/authorize?client_id=352117035620106240&scope=bot&permissions=3072")


bot.run(token)
