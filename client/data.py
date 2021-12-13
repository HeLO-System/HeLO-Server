from types import SimpleNamespace

#########################################################################################
# until the database is integrated, use this as sample data source                      #
#########################################################################################

users = {
    "407302122921656340": SimpleNamespace(**{
        "pin": "",
        "clan": "StDb",
        "role": "admin"
    })
}

clan = SimpleNamespace(**{
    "tag": "StDb",
    "flag": ":flag_de:",
    "invite": "https://discord.gg/ShZ49NVbqZ"
})

match_to_confirm = {
    "clan1": "StDb",
    "coop1": "91.",
    "clan2": "CoRe",
    "coop2": None,
    "date": "30.11.21",
    "map": "Stalingrad",
    "score1": 5,
    "score2": 0,
    "side1": "Axis",
    "side2": "Allies",
    "user1": ""
}

maps = ["SMDM", "Foy", "Carentan",
        "SME", "PHL", "Omaha",
        "Utah", "Stalingrad", "Kursk",
        "Hürtgen", "Hill 400" ]

clans = {
    1: SimpleNamespace(**{ "tag": "StDb",    "flag": ":flag_de:",    "invite": "https://discord.gg/ShZ49NVbqZ"     }),
    2: SimpleNamespace(**{ "tag": "91.",     "flag": ":flag_de:",    "invite": "https://discord.gg/FYnSdnw"        })
}

clan_list = [
    "CoRe",
    "38.",
    "WTH",
    "116.",
    "TL",
    "501.ES",
    "82AD",
    "HTD",
    "LetLoosers",
    "DC",
    "BST2",
    "BR1",
    "Five",
    "StDb",
    "TC",
    "CNUT",
    "BWR",
    "2.Fjg",
    "NPA",
    "BDSQ",
    "OP",
    "DKB",
    "LostLegion",
    "HLY",
    "KRT",
    "OC",
    "GR3",
    "BIA",
    "ARC",
    "LpF",
    "BHB",
    "BWCC",
    "HFKT",
    "ESPT",
    "Cult",
    "UFr",
    "20th",
    "CFr",
    "GOF",
    "BIGD",
    "XIIIth",
    "ESP",
    "1CDO",
    "91.",
    "FLL",
    "PBS",
    "TBGC",
    "Phx",
    "CSP",
    "EXD",
    "WAR",
    "Tango",
    "SE:VH",
    "LwJg46",
    "PKKA"
]