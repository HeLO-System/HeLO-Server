import logging
from discord.embeds import Embed
from discord_components.component import Button
from object_models import *
from data import *
from new_match import match_description


async def select_map(state, cmd : SimpleNamespace):
    logging.info(f"{cmd}")    
    
    if cmd.result != None:
        return Return.cmd(state, result = { "map": cmd.result })    
    
    state.push(MatchResult(state.current))
    
    embed = Embed(title = "Map", description = f"{match_description(state)}**Select map**")
    
    components = [
        [            
            Button(label = maps[0], custom_id = SelectMap.cmd( state, map = maps[0] ) ),
            Button(label = maps[1], custom_id = SelectMap.cmd( state, map = maps[1] ) ),
            Button(label = maps[2], custom_id = SelectMap.cmd( state, map = maps[2] ) ),
        ], [            
            Button(label = maps[3], custom_id = SelectMap.cmd( state, map = maps[3] ) ),
            Button(label = maps[4], custom_id = SelectMap.cmd( state, map = maps[4] ) ),
            Button(label = maps[5], custom_id = SelectMap.cmd( state, map = maps[5] ) ),
        ], [            
            Button(label = maps[6], custom_id = SelectMap.cmd( state, map = maps[6] ) ),
            Button(label = maps[7], custom_id = SelectMap.cmd( state, map = maps[7] ) ),
            Button(label = maps[8], custom_id = SelectMap.cmd( state, map = maps[8] ) ),
        ], [            
            Button(label = maps[9], custom_id = SelectMap.cmd( state, map = maps[9] ) ),
            Button(label = maps[10], custom_id = SelectMap.cmd( state, map = maps[10] ) ),
            Button(emoji='🔼', custom_id = Home.cmd(state))
        ]        
    ]
    
    await state.current.respond(embed = embed, components = components)    