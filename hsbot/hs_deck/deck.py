# deck/deck.py
from base64 import b64decode
from io import BytesIO
from operator import itemgetter

import discord

from .card_data import *

class Deck:

    def __init__(self, deck_string):
        self.string = deck_string
        self.cards = []
        self.heroes = []
        self.format, self.heroes, self.cards = self.decode_list(deck_string)
        self.cost = 0
        self.readable_deck = self.make_readable()
        self.zodiac = get_zodiac(self.readable_deck)
        for dbfID, count in self.cards:
            self.cost += rarities[card_info_id[str(dbfID)]['rarity']] * count

    def decode_list(self, deck_list):
        decoded_list = b64decode(deck_list)
        stream = BytesIO(decoded_list)

        if stream.read(1) != b"\0":
            raise ValueError("Invalid hs_deck string")

        version = self._read_varint(stream)
        if version != 1:
            raise ValueError("Invalid hs_deck string")

        _format = self._read_varint(stream)

        no_of_heroes = self._read_varint(stream)
        heroes = [str(self._read_varint(stream)) for i in range(no_of_heroes)]

        no_one_ofs = self._read_varint(stream)
        cards = [(str(self._read_varint(stream)), 1) for i in range(no_one_ofs)]

        no_two_ofs = self._read_varint(stream)
        cards += [(str(self._read_varint(stream)), 2) for i in range(no_two_ofs)]

        no_x_ofs = self._read_varint(stream)
        cards += [(str(self._read_varint(stream)), "x") for i in range(no_x_ofs)]

        return _format, heroes, cards

    def make_readable(self):
        deck = []
        for dbfID, count in self.cards:
            deck.append((card_info_id[dbfID]['name'], card_info_id[dbfID]['cost'], count, card_info_id[dbfID]['set']))
        readable_deck = sorted(deck, key=itemgetter(1))
        return readable_deck

    def make_embed(self):

        card_class = card_info_id[str(self.heroes[0])]['cardClass']
        readable = self.make_readable()

        embed = discord.Embed(title="Class: {}".format(card_class.title()),
                              url="https://hsreplay.net/decks/#playerClasses={}".format(card_class),
                              color=discord.Colour.from_rgb(embed_visuals[card_class]['colour'][0],
                                                            embed_visuals[card_class]['colour'][1],
                                                            embed_visuals[card_class]['colour'][2]))

        content = ""
        for card in readable:
            content += "({}) - {}x {}\n".format(card[1], card[2], card[0])
        if formats[self.format] == "Standard":
            embed.add_field(name="{}: Year of the {}".format(formats[self.format], self.zodiac), value=content)
        else:
            embed.add_field(name="{} <:wild:422105249076215818>".format(formats[self.format]), value=content)
        embed.set_footer(icon_url="https://cdn.discordapp.com/emojis/421803677666377739.png?v=1",
                         text="Costs: {}".format(self.cost))
        return embed

    def _read_varint(self, stream):
        shift = 0
        result = 0
        while True:
            c = stream.read(1)
            if c == "":
                raise EOFError("Unexpected EOF while reading varint")
            i = ord(c)
            result |= (i & 0x7f) << shift
            shift += 7
            if not (i & 0x80):
                break

        return result