import discord, logging, math
from discord_components.component import Button
from discord_components.interaction import Interaction
from data import *
from object_models import *
from new_match import match_description

#############################
# process message from user #
#############################

async def select_clan(state, cmd : SimpleNamespace):
    logging.info(f"{cmd}")

    if cmd.result != None:
        return Return.cmd(state, cmd.result)
    
    input = state.current.options[cmd.input]
    logging.info(f"{input}")

    if input.selected == None: # select all clans to start with
        selected = clan_list
    else:
        selected = input.selected

    if selected != None and len(selected) == 1 and input.from_search == False: # single clan selected                
        return Return.cmd(state, { "selected": selected[0], "is_showing_coop": input.is_showing_coop, "next_step": "RETURN" } )
        

    else: # build buttons for ranges / clans

        state.push(SelectClan(state.current))

        embed = discord.Embed(title = input.title, description=f"{match_description(state)}**Select a clan**")
        components = []

        selected.sort()               
        state.current.options = [] # building new buttons, discard the old button options
        if len(selected) > 5:
            step = max(5, math.ceil((len(selected)) / 5)) # at least 5 clans per page
            for i in range(0, len(selected), step):
                button_range = selected[i:i+step]
                if len(button_range) > 1:
                    components.append([
                        Button(label=f"{button_range[0]} - {button_range[-1]}", custom_id = SelectClan.cmd(state, SelectClanOption(selected = button_range))),
                    ])
                else:
                    components.append([ Button(label = button_range[0], custom_id = SelectClan.cmd(state, SelectClanOption(selected = [button_range[0]], is_showing_coop = True))) ])
                    if input.is_showing_coop: # additional button for coop
                        components[-1].append(Button(emoji="🚻", custom_id = SelectClan.cmd(state, SelectClanOption(selected = [button_range[0]], is_showing_coop = False))))

        else:
            for clan in selected: 
                components.append([ Button(label = clan, custom_id = SelectClan.cmd(state, SelectClanOption(selected = [clan], is_showing_coop = True))) ])
                if input.is_showing_coop: # additional button for coop
                    components[-1].append(Button(emoji="🚻", custom_id = SelectClan.cmd(state, SelectClanOption(selected = [clan], is_showing_coop = False))))
    
    components[-1].append(Button(emoji='◀️', custom_id = SelectClan.cmd(state, SelectClanOption(is_showing_coop = input.is_showing_coop))))
    components[-1].append(Button(emoji='🔼', custom_id = Home.cmd(state)))

    if type(state.interaction) == Interaction:
        logging.info(f"responding to interaction: {embed.title} - {embed.description}")
        await state.interaction.respond(type = 7, content = "", embed = embed, components = components)
    else:
        logging.info(f"update message: {state.parent.interaction.message.id} ")
        await state.parent.interaction.message.delete() # delete the message before the search
        await state.parent.interaction.author.send(content = "", embed = embed, components = components)
        
