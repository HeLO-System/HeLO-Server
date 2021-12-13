import logging
from types import SimpleNamespace
from object_models import *
from discord import Embed
from discord_components import Button

async def select_flag(state, cmd : SimpleNamespace):
    logging.info(f"{cmd}")    
        

    if cmd.input != None:
        return Return.cmd(state, result = { "field": "SELECT_FLAG", "flag": cmd.input })    
    
    state.push(SelectFlag(state))
    
    embed = Embed(title = "Select Flag")

    nationalities = [
        "eu", "fi", "us", "cn", "rainbow",
        "de", "pl", "ca", "jp", "?3",
        "gb", "sk", "it", "au", "?4",
        "fr", "cz", "tr", "?1", "?5",
        "es", "ru", "br", "?2", "home"
    ]
      
    components = []
    row = []
    for n in nationalities:
        if n == "home": 
            row.append(Button(emoji = "🔼", custom_id = Home.cmd(state)))
        elif n == "rainbow": 
            row.append(Button(label = n, custom_id = SelectFlag.cmd(state, ":rainbow_flag:")))
        elif n.startswith("?"): 
            row.append(Button(label = n, custom_id = SelectFlag.cmd(state, f":pirate_flag: {n}")))
        else:
            row.append(Button(label = n, custom_id = SelectFlag.cmd(state, f":flag_{n}:")))

        if len(row) == 5:
            components.append(row)
            row = []
                
    await state.current.respond(embed = embed, components = components)    
    
