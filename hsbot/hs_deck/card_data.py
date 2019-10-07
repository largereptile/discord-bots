import json
from datetime import datetime

embed_visuals = {"PALADIN": {"colour": (255, 255, 0),
                             "url": "https://images.disguisedtoast.com/uploads/card_class/cover/3/class-paladin_2x.png"},
                 "WARRIOR": {"colour": (204, 0, 0),
                             "url": "https://images.disguisedtoast.com/uploads/card_class/cover/4/class-warrior_2x.png"},
                 "MAGE": {"colour": (51, 153, 255),
                             "url": "https://images.disguisedtoast.com/uploads/card_class/cover/8/class-mage_2x.png"},
                 "DRUID": {"colour": (102, 51, 0),
                             "url": "https://images.disguisedtoast.com/uploads/card_class/cover/6/class-druid_2x.png"},
                 "HUNTER": {"colour": (0, 102, 0),
                             "url": "https://images.disguisedtoast.com/uploads/card_class/cover/5/class-hunter_2x.png"},
                 "WARLOCK": {"colour": (51, 0, 51),
                             "url": "https://images.disguisedtoast.com/uploads/card_class/cover/7/class-warlock_2x.png"},
                 "PRIEST": {"colour": (224, 224, 224),
                             "url": "https://images.disguisedtoast.com/uploads/card_class/cover/2/class-priest_2x.png"},
                 "ROGUE": {"colour": (32, 32, 32),
                             "url": "https://images.disguisedtoast.com/uploads/card_class/cover/9/class-rogue_2x.png"},
                "SHAMAN": {"colour": (0, 51, 102),
                             "url": "https://images.disguisedtoast.com/uploads/card_class/cover/1/class-shaman_2x.png"}}

formats = {1: "Wild",
           2: "Standard",
           0: "Not even Wild"}

rarities = {"FREE": 0,
            "COMMON": 40,
            "RARE": 100,
            "EPIC": 400,
            "LEGENDARY": 1600}

card_info_id = json.load(open("cards_by_id.json", "r"))
card_info_name = json.load(open("cards_by_name.json", "r"))

zodiacs_old = {
    "Invalid": {},
    "Pre-Standard": [["CORE", "EXPERT1", "REWARD", "PROMO", "NAXX", "GVG", "BRM", "TGT", "LOE"], datetime.fromtimestamp(0)],
    "Kraken": [["CORE", "EXPERT1", "BRM", "TGT", "LOE", "OG", "OG_RESERVE", "KARA", "KARA_RESERVE", "GANGS", "GANGS_RESERVE"], datetime(2016, 4, 26)],
    "Mammoth": [["CORE", "EXPERT1", "OG", "OG_RESERVE", "KARA", "KARA_RESERVE", "GANGS", "GANGS_RESERVE", "ICECROWN", "UNGORO", "LOOTAPALOOZA"], datetime(2017, 4, 7)],
    "Raven": [["CORE", "EXPERT1", "ICECROWN", "UNGORO", "LOOTAPALOOZA"], datetime(2018, 4,30)]
}

zodiacs = {
    -1: "Invalid",
    0: "`Pre-Standard`",
    1: "Kraken",
    2: "Mammoth",
    3: "Raven"
}

sets = {
    "CORE": [0, 1, 2, 3],
    "EXPERT1": [0, 1, 2, 3],
    "REWARD": [0],
    "PROMO": [0],
    "NAXX": [0],
    "GVG": [0],
    "BRM": [0, 1],
    "LOE": [0, 1],
    "TGT": [0, 1],
    "OG": [1, 2],
    "OG_RESERVE": [1, 2],
    "KARA": [1, 2],
    "KARA_RESERVE": [1, 2],
    "GANGS": [1, 2],
    "GANGS_RESERVE": [1, 2],
    "ICECROWN": [2, 3],
    "UNGORO": [2, 3],
    "LOOTAPALOOZA": [2, 3],
    "HOF": []

}

def get_zodiac(deck):
    years = []
    for card in deck:
        for year in sets[card[3]]:
            if not year in years and (not card[3] == "CORE" and not card[3] == "EXPERT1"):
                years.append(year)
    years = sorted(years)
    zod_year = sum(years)//len(years)
    return zodiacs[zod_year]