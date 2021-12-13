import logging
from discord.embeds import Embed
from discord_components.component import Button
from discord_components.interaction import Interaction
from object_models import *
from data import *
from user_state import UserState


async def manage_clans(state, cmd : SimpleNamespace):
    logging.info(f"{cmd}")    
    
    if cmd.result != None:
        return Return.cmd(state, result = cmd.result )

    states = state.pop_to(Home)
    logging.info(f"states = {states}")
    if state.current.name != ManageClans.name:
        state.push(ManageClans(state))   
    
    
    embed = Embed(title = "Manage Clans")
    
    components = [
        [            
            Button(emoji="🆕", custom_id = AddClan.cmd(state)),
            Button(emoji="✏️", custom_id = EditClan.cmd(state)),
            Button(emoji="🗑️", custom_id = DeleteClan.cmd(state)),
        ], [            
            Button(emoji='🔼', custom_id = Home.cmd(state))
        ]        
    ]
    
    await state.current.respond(embed = embed, components = components)    


async def edit_clan(state : UserState, cmd : SimpleNamespace):
    logging.info(f"{cmd}")
    error = None    
    
    if cmd.result == None:
        if cmd.action == EditClan.name:
            cmd = state.current.options[cmd.input]
            state.push(EditClan(state.current, cmd.next_step, "Edit Clan"))
        else:           
            cmd = EditClanOption(next_step=EditClan.name)
            state.push(EditClan(state.current, cmd.next_step, "Add Clan"))
            state.current.clan_id = max(clans) + 1
            state.current.clan = SimpleNamespace(**{ "tag": "", "flag": "", "invite": "" })
            
    else:       
        result = cmd.result if type(cmd.result) == str else SimpleNamespace(**cmd.result)

        if state.current.next_step == None: # first step: search for CLAN
            logging.info(f"CLAN: {result.selected}")    
            clan_id = None
            for id, clan in clans.items():
                if clan.tag == result.selected:
                    state.current.clan_id = id
                    state.current.clan = clan
                    state.current.next_step = EditClan.name
        
        elif result == "CONFIRM":
            clans[state.current.clan_id] = state.current.clan
            return ManageClans.cmd(state)
        
        elif result.field == "SELECT_TAG":
            # todo - check if clan tag already exists
            state.current.clan.tag = result.input
            
        elif result.field == "SELECT_FLAG":
            state.current.clan.flag = result.flag
      
        elif result.field == "SELECT_INVITE":
            if result.input.startswith("https://discord.gg/"):
                state.current.clan.invite = result.input
            else:
                error = "***Invalid input: discord invites have the form 'https://discord.gg/??????????'***"

    if state.current.next_step == None: # first step: search for CLAN
        return SearchClan.cmd(state, option = SearchClanOption(title = state.current.title, is_showing_coop = False))

    if state.current.next_step == "DONE":  
        return ManageClans.cmd(state)
    
    description = "\n".join([
        f"Clan: {state.current.clan.tag}",
        f"Nationality: {state.current.clan.flag}",
        f"Invite: {state.current.clan.invite}"
    ])
    if error != None: description += f"\n\n{error}"
            
    embed = Embed(title = "Edit Clan", description = description)
    components = [
        [
            Button(emoji = "🏷️", label = "tag", custom_id = InputFromMessage.cmd(state, option = InputFromMessageOption("SELECT_TAG", "Enter Clan Tag"))),
            Button(emoji = "🏳️‍🌈", label = "flag", custom_id = SelectFlag.cmd(state, option = SelectFlagOption(field = "SELECT_FLAG"))),
            Button(emoji = "🔗", label = "invite", custom_id = InputFromMessage.cmd(state, option = InputFromMessageOption("SELECT_INVITE", "Enter Disord Invite URL"))),
        ],
        [
            Button(emoji='🆗', custom_id = EditClan.cmd(state, confirm = "CONFIRM")),
            Button(emoji='🔼', custom_id = Home.cmd(state))
        ]
    ]
    
    if state.interaction != None:
        logging.info(f"responding to interaction: {embed.title} - {embed.description}")
        await state.interaction.respond(type = 7, content = "", embed = embed, components = components)
    else:
        logging.info(f"update message: {state.parent.interaction.message.id} ")
        await state.current.interaction.message.delete() # delete the message before the search
        await state.current.interaction.author.send(content = "", embed = embed, components = components)
        

async def delete_clan(state, cmd : SimpleNamespace):
    logging.info(f"{cmd}")    
    
    if cmd.result == None:
        cmd = state.current.options[cmd.input]
        state.push(DeleteClan(state, cmd.next_step))
    else:
        result = cmd.result if type(cmd.result) == str else SimpleNamespace(**cmd.result)

        if state.current.next_step == None: # first step: search for CLAN
            logging.info(f"CLAN: {result.selected}")    
            state.current.clan = result.selected            
            state.current.next_step = "CONFIRM"

        elif state.current.next_step == "CONFIRM":
            logging.info(f"CONFIRM - delete from DB: {state.current.clan}")
            clan_list.remove(state.current.clan) # todo - delete from database
            state.current.next_step = "DONE"

    if state.current.next_step == None: # first step: search for CLAN
        return SearchClan.cmd(state, option = SearchClanOption( title = "Delete Clan" ))

    if state.current.next_step == "CONFIRM":     
        return DeleteClanConfirm.cmd(state, option = DeleteClanConfirmOption(clan = state.current.clan))
    
    if state.current.next_step == "DONE":  
        return ManageClans.cmd(state)
   
   
async def delete_clan_confirm(state, cmd : SimpleNamespace):
    logging.info(f"{cmd}")    
    
    if cmd.result != None:
        return Return.cmd(state, result = { "user": state.userid })
    
    cmd = state.current.options[cmd.input]
    logging.info(f"{cmd}")

    state.push(DeleteClanConfirm(state.current))
    
    embed = Embed(title = "Confirm clan deletion", description = f"**Are you absolutely sure, this clan should be deleted?**")
    
    components = [
        [
            Button(emoji='🆗', custom_id = DeleteClanConfirm.cmd(state, confirm = "CONFIRM" )),
            Button(emoji='🔼', custom_id = ManageClans.cmd(state))
        ]
    ]
    
    await state.current.respond(embed = embed, components = components)    