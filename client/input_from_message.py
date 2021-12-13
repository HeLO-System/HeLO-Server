import discord, logging
from data import *
from object_models import *
from new_match import *


##################
# perform action #
##################
        
async def input_from_message(state, cmd : SimpleNamespace):
    logging.info(f"{cmd}")

    if cmd.result != None:
        return Return.cmd(state, cmd.result)
    
    input = state.current.options[cmd.input]
    state.push(InputFromMessage(state.current))
    state.current.callback = "INPUT_FROM_MESSAGE"
    state.current.options = [input]
    
    embed = discord.Embed(title = input.title, description = "Enter value as message text below:")
    await state.interaction.respond(type = 7, content = "", embed = embed, components = [])
    
    
async def input_from_message_callback(state, input):
    option = state.current.options[0]
    logging.info(f"field = {option.field}, input = {input}")
    state.parent.interaction = state.current.interaction
    return InputFromMessage.cmd(state, { "field": state.current.options[0].field, "input": input }, InputFromMessageOption(field = state.current.options[0].field))