import sqlite3
import requests

from discord.ext import commands

import hs_deck

# db = sqlite3.connect("hs.db")
# c = db.cursor()
bot = commands.Bot(command_prefix="hs_")

@bot.event
async def on_ready():
    print(bot.user.name)
    #\card = hs_deck.card_info_name["Angry Chicken"]

    #\response = requests.get("http://hearthapi.com/v1.0/cards/{}".format(card['id']))
    print("online")


@bot.event
async def on_message(message):
    for word in message.content.split():
        if word.startswith("AA"):
            try:
                deck = hs_deck.Deck(word)
                embed = deck.make_embed()
                await message.channel.send(embed=embed)
            except ValueError:
                pass


@bot.command(name="read")
async def deck_string_read(ctx, deck_string):
    try:
        deck = hs_deck.Deck(deck_string)
        embed = deck.make_embed()
        await ctx.send(embed=embed)

    except ValueError:
        await ctx.send("Invalid deckstring")




bot.run(token)

