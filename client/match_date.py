import logging
from datetime import date, timedelta
from discord.embeds import Embed
from discord_components.component import Button
from object_models import *
from new_match import match_description


#############################
# process message from user #
#############################

def d(days): return date.today() - timedelta(days = days)
def c(days): return d(days).strftime('%d.%m.%y')
def s(days): return d(days).strftime('%d %b')

async def match_date(state, cmd : SimpleNamespace):
    logging.info(f"match_date_process_message: {cmd}")    
    
    if cmd.result != None:
        return Return.cmd(state, result = { "date": cmd.result })    
    
    state.push(MatchResult(state.current))
    
    embed = Embed(title = "Match date", description = f"{match_description(state)}**Select match date**")
    
    components = [
        [            
            Button(label = s(0), custom_id = MatchDate.cmd( state, date = c(0) ) ),
            Button(label = s(1), custom_id = MatchDate.cmd( state, date = c(1) ) ),
            Button(label = s(2), custom_id = MatchDate.cmd( state, date = c(2) ) )
        ], [            
            Button(label = s(3), custom_id = MatchDate.cmd( state, date = c(3) ) ),
            Button(label = s(4), custom_id = MatchDate.cmd( state, date = c(4) ) ),
            Button(label = s(5), custom_id = MatchDate.cmd( state, date = c(5) ) )
        ], [            
            Button(label = s(6), custom_id = MatchDate.cmd( state, date = c(6) ) ),
            Button(label = s(7), custom_id = MatchDate.cmd( state, date = c(7) ) ),
            Button(label = s(8), custom_id = MatchDate.cmd( state, date = c(8) ) )
        ], [            
            Button(label = s(9), custom_id = MatchDate.cmd( state, date = c(9) ) ),
            Button(label = s(10), custom_id = MatchDate.cmd( state, date = c(10) ) ),
            Button(label = s(11), custom_id = MatchDate.cmd( state, date = c(11) ) )
        ], [            
            Button(label = s(12), custom_id = MatchDate.cmd( state, date = c(12) ) ),
            Button(label = s(13), custom_id = MatchDate.cmd( state, date = c(13) ) ),
            Button(emoji='🔼', custom_id = Home.cmd(state))
        ]        
    ]
    
    await state.current.respond(embed = embed, components = components)    