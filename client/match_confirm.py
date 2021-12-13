import logging
from discord.embeds import Embed
from discord_components.component import Button
from object_models import *
from new_match import match_description


#############################
# process message from user #
#############################

async def match_confirm(state, cmd : SimpleNamespace):
    logging.info(f"{cmd}")    
    
    if cmd.result != None:
        return Return.cmd(state, result = { "user1": state.userid })
    
    cmd = state.current.options[cmd.input]
    logging.info(f"{cmd}")

    state.push(MatchConfirm(state.current))
    
    embed = Embed(title = "Match confirmation", description = f"{match_description(state)}**Confirm match (your user id will be added to the match data)**")
    
    components = [
        [
            Button(emoji='🆗', custom_id = MatchConfirm.cmd(state, confirm = "CONFIRM" )),
            Button(emoji='🔼', custom_id = Home.cmd(state))
        ]
    ]
    
    await state.current.respond(embed = embed, components = components)    