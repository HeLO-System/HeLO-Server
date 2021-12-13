from object_models import *
from login import login
from home import home
from select_clan import select_clan
from search_clan import search_clan, search_clan_callback
from manage_clans import manage_clans, edit_clan, delete_clan, delete_clan_confirm
from new_match import new_match
from match_result import match_result
from match_date import match_date
from select_map import select_map
from select_flag import select_flag
from match_confirm import match_confirm
from input_from_message import input_from_message, input_from_message_callback

actions = { 
    Login.name:             login,
    Home.name:              home,
    SelectClan.name:        select_clan,
    SearchClan.name:        search_clan,
    ManageClans.name:       manage_clans,
    AddClan.name:           edit_clan,
    EditClan.name:          edit_clan,
    DeleteClan.name:        delete_clan,
    DeleteClanConfirm.name: delete_clan_confirm,
    NewMatch.name:          new_match,
    MatchResult.name:       match_result,
    MatchDate.name:         match_date,
    SelectMap.name:         select_map,
    SelectFlag.name:        select_flag,
    MatchConfirm.name:      match_confirm,
    InputFromMessage.name:  input_from_message,
    Return.name:            Return.process_message
}
async def other_action(state, args): 
    logging.info(f"action not recognised: {state.interaction.custom_id}")
    await state.current.respond()

callbacks = {
    SearchClan.name:        search_clan_callback,
    InputFromMessage.name:  input_from_message_callback,
}