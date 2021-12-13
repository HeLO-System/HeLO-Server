from types import SimpleNamespace
import discord, logging
from discord_components.component import Button
from discord_components.interaction import Interaction

from home import *
from data import *
from object_models import *


#############################
# process message from user #
#############################

async def login(state, cmd : SimpleNamespace):
    logging.info(f"{cmd if type(cmd.input) != int else 'numpad button pressed'}")

    state.push(Login(state), when = state.current == None)    

    inputs = {
        "CLEAR" :   clear_perform,
        "AUTH":     auth_perform,
        "LOGIN":    login_perform,
        "LOGOUT":   logout_perform,
        "HELP":     help_perform
    }

    await inputs.get(cmd.input, numpad)(state, cmd)


async def numpad(state, cmd):
    if type(cmd.input) == int:
        state.current.input += str(cmd.input)
    else:
        logging.info(f"No valid command: {cmd.input}")
        return

    await state.current.respond()


async def clear_perform(state, cmd):
    logging.info(f"clear numpad input")
    state.current.input = ""
    await state.current.respond()


async def login_perform(state, cmd):
    logging.info(f"show numpad")
    state.current.input = ""
    
    embed = discord.Embed(title="Login", description="Enter your PIN")
    components = [[
        Button(emoji="1️⃣", custom_id=Login.cmd(1)),
        Button(emoji="2️⃣", custom_id=Login.cmd(2)),   
        Button(emoji="3️⃣", custom_id=Login.cmd(3)),   
    ], [
        Button(emoji="4️⃣", custom_id=Login.cmd(4)),
        Button(emoji="5️⃣", custom_id=Login.cmd(5)),   
        Button(emoji="6️⃣", custom_id=Login.cmd(6)),   
    ], [
        Button(emoji="7️⃣", custom_id=Login.cmd(7)),
        Button(emoji="8️⃣", custom_id=Login.cmd(8)),   
        Button(emoji="9️⃣", custom_id=Login.cmd(9)),   
    ], [
        Button(emoji="◀️", custom_id=Login.cmd("CLEAR")),
        Button(emoji="0️⃣", custom_id=Login.cmd(0)),   
        Button(emoji="🆗", custom_id=Login.cmd("AUTH")),   
    ]]
    if type(state.current.interaction) == Interaction:
        await state.current.respond(embed = embed, components = components)
    else:
        await state.current.message.channel.send(embed = embed, components = components)
        

async def auth_perform(state, cmd : SimpleNamespace):
    logging.info(f"authenticate user")
    user = users[state.userid] # todo - read user data from database
    if state.current.input == user.pin:
        state.user = user
        await home(state, SimpleNamespace(**{ "action": "HOME" }))
    else:
        await login_perform(state, cmd)


async def logout_perform(state, cmd : SimpleNamespace):
    logging.info(f"logout and clear user state")
    state.clear()
    # todo - what else to be cleared up for logout?
    embed = discord.Embed(title="Done", description="logged out")
    components = [ Button(emoji = '🔑', label = 'Login', custom_id = Login.cmd("LOGIN")) ]
    await state.interaction.respond(type = 7, content = "", embed = embed, components = components)


async def help_perform(state, cmd : SimpleNamespace):
    logging.info(f"send help message")
    await state.interaction.channel.send("\n".join([
        "Usage:", 
        "- help",
        "- login",
        "- logout",
    ]))