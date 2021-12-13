import logging

from select_clan import *
from object_models import *


#############################
# process message from user #
#############################

async def new_match(state, cmd : SimpleNamespace):
    logging.info(f"{cmd}")    

    if cmd.result == None:
        cmd = state.current.options[cmd.input]
        state.push(NewMatch(state, cmd.clan1, cmd.next_step))
    else:
        result = SimpleNamespace(**cmd.result)

        if state.current.next_step == "CLAN1":
            logging.info(f"CLAN1: {result.selected}")    
            state.current.clan1 = result.selected            
            state.current.next_step = "COOP1" if not result.is_showing_coop else "CLAN2"

        elif state.current.next_step == "COOP1":
            logging.info(f"COOP1: {result.selected}")
            state.current.coop1 = result.selected
            state.current.next_step = "CLAN2"
            
        elif state.current.next_step == "CLAN2":
            logging.info(f"CLAN2: {result.selected}")
            state.current.clan2 = result.selected
            state.current.next_step = "COOP2" if not result.is_showing_coop else "RESULT"

        elif state.current.next_step == "COOP2":
            logging.info(f"COOP2: {result.selected}")
            state.current.coop2 = result.selected
            state.current.next_step = "RESULT"
            
        elif state.current.next_step == "RESULT":
            logging.info(f"RESULT: {result.side1} {result.score1}:{5 - result.score1}")
            state.current.score1 = result.score1
            state.current.score2 = 5 - result.score1
            state.current.side1 = result.side1
            state.current.side2 = "Axis" if result.side1 == "Allies" else "Allies"
            state.current.next_step = "DATE"

        elif state.current.next_step == "DATE":
            logging.info(f"DATE: {result.date}")
            state.current.date = result.date
            state.current.next_step = "MAP"
            
        elif state.current.next_step == "MAP":
            logging.info(f"MAP: {result.map}")
            state.current.map = result.map
            state.current.next_step = "CONFIRM"
            
        elif state.current.next_step == "CONFIRM":
            logging.info(f"CONFIRM")
            state.current.next_step = "DONE" # todo
            
    if state.current.next_step == "CLAN1": 
        return SearchClan.cmd(state, option = SearchClanOption( title = "Search 1. Clan", is_showing_coop = True ))
    
    if state.current.next_step == "COOP1": 
        return SearchClan.cmd(state, option = SearchClanOption( title = "Search 1. Clans Coop partner", is_showing_coop = False ))
    
    if state.current.next_step == "CLAN2":  
        return SearchClan.cmd(state, option = SearchClanOption( title = "Search 2. Clan", is_showing_coop = True ))    
    
    if state.current.next_step == "COOP2":  
        return SearchClan.cmd(state, option = SearchClanOption( title = "Search 2. Clans Coop partner", is_showing_coop = False ))
    
    if state.current.next_step == "RESULT": 
        return MatchResult.cmd(state)
    
    if state.current.next_step == "DATE": 
        return MatchDate.cmd(state)
    
    if state.current.next_step == "MAP": 
        return SelectMap.cmd(state)
    
    if state.current.next_step == "CONFIRM": 
        # todo - write to database            
        confirmed_option = MatchConfirmOption( 
            clan1 = state.current.clan1,
            coop1 = state.current.coop2,
            clan2 = state.current.clan2,
            coop2 = state.current.coop2,
            side1 = state.current.side1,
            side2 = state.current.side2,
            score1 = state.current.score1,
            score2 = state.current.score2,
            date = state.current.date,
            map = state.current.map,
            user1 = state.userid
        )
        logging.info(f"write to DB: {confirmed_option}")

        return MatchConfirm.cmd(state, option = confirmed_option)
    
    if state.current.next_step == "DONE":  
        return Home.cmd(state)


def match_description(state):
    state = state.find(NewMatch)
    if state == None: return ""
    
    flag1 = [c.flag for id, c in clans.items() if c.tag == state.clan1]
    flag1c = [c.flag for id, c in clans.items() if c.tag == state.coop1]
    flag2 = [c.flag for id, c in clans.items() if c.tag == state.clan2]
    flag2c = [c.flag for id, c in clans.items() if c.tag == state.coop2]
    
    s = "**New Match**\n"
    s += f"{flag1[0]} " if len(flag1) > 0 else ""
    s += state.clan1 if state.clan1 != None else "???"
    s += " & " if state.coop1 != None else ""
    s += f"{flag1c[0]} " if len(flag1c) > 0 else ""
    s += state.coop1 if state.coop1 != None else ""
    s += " vs. "
    s += f"{flag2[0]} " if len(flag2) > 0 else ""
    s += state.clan2 if state.clan2 != None else "???"
    s += " & " if state.coop2 != None else ""
    s += f"{flag2c[0]} " if len(flag2c) > 0 else ""
    s += state.coop2 if state.coop2 != None else ""
    s += "\n"
    s += state.date if state.date != None else "???"
    s += "\n"
    s += state.map if state.map != None else "???"
    s += "\n"
    s += state.side1 if state.side1 != None else "???"
    s += " "
    s += str(state.score1) if state.score1 != None else "?"
    s += ":"
    s += str(state.score2) if state.score2 != None else "?"
    s += " "
    s += state.side2 if state.side2 != None else "???"
    s += "\n\n"
    return s