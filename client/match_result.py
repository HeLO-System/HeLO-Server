import logging
from discord.embeds import Embed
from discord_components.component import Button
from discord_components.interaction import Interaction
from object_models import *
from new_match import match_description


#############################
# process message from user #
#############################

async def match_result(state, cmd : SimpleNamespace):
    logging.info(f"match_result_process_message: {cmd}")    
    
    if cmd.result != None:
        input = cmd.result if type(cmd.result) == str else SimpleNamespace(**cmd.result) 
    
        if type(cmd.result) != str and input.score1 != None and input.side1 != None: # result has been selected
            return Return.cmd(state, result = { "score1": input.score1, "side1": input.side1 })
    
    state.push(MatchResult(state.current))
    
    embed = Embed(title = "Match result", description = f"{match_description(state)}**Select match result and side below**")
    
    components = [
        [            
            Button(label = "Allies", custom_id = MatchResult.cmd( state, side1 = "Allies1" ) ),
            Button(label = "5️⃣:0️⃣", custom_id = MatchResult.cmd( state, score1 = 5, side1 = "Allies" ) ),
            Button(label = "4️⃣:1️⃣", custom_id = MatchResult.cmd( state, score1 = 4, side1 = "Allies" ) ),
            Button(label = "3️⃣:2️⃣", custom_id = MatchResult.cmd( state, score1 = 3, side1 = "Allies" ) )
        ], [            
            Button(label = "Allies", custom_id = MatchResult.cmd( state, side1 = "Allies2" ) ),
            Button(label = "2️⃣:3️⃣", custom_id = MatchResult.cmd( state, score1 = 2, side1 = "Allies" ) ),
            Button(label = "1️⃣:4️⃣", custom_id = MatchResult.cmd( state, score1 = 1, side1 = "Allies" ) ),
            Button(label = "0️⃣:5️⃣", custom_id = MatchResult.cmd( state, score1 = 0, side1 = "Allies" ) )
        ], [            
            Button(label = "Axis", custom_id = MatchResult.cmd( state, side1 = "Axis1" ) ),
            Button(label = "5️⃣:0️⃣", custom_id = MatchResult.cmd( state, score1 = 5, side1 = "Axis" ) ),
            Button(label = "4️⃣:1️⃣", custom_id = MatchResult.cmd( state, score1 = 4, side1 = "Axis" ) ),
            Button(label = "3️⃣:2️⃣", custom_id = MatchResult.cmd( state, score1 = 3, side1 = "Axis" ) )
        ], [            
            Button(label = "Axis", custom_id = MatchResult.cmd( state, side1 = "Axis2" ) ),
            Button(label = "2️⃣:3️⃣", custom_id = MatchResult.cmd( state, score1 = 2, side1 = "Axis" ) ),
            Button(label = "1️⃣:4️⃣", custom_id = MatchResult.cmd( state, score1 = 1, side1 = "Axis" ) ),
            Button(label = "0️⃣:5️⃣", custom_id = MatchResult.cmd( state, score1 = 0, side1 = "Axis" ) )
        ], [
            Button(emoji='🔼', custom_id = Home.cmd(state))            
        ]
    ]
    
    if type(state.current.interaction) == Interaction:
        await state.current.respond(embed = embed, components = components)    
    else:
        await state.parent.interaction.message.delete()
        await state.current.interaction.author.send(content = "", embed = embed, components = components)    