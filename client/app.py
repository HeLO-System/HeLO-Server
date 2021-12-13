import discord, logging, os, pytz
from discord_components import DiscordComponents
from login import *
from home import *
from select_clan import *
from new_match import *
from match_result import *
from match_date import *
from select_map import *
from search_clan import *
from manage_clans import *
from select_flag import *
from user_state import *
from match_confirm import *
from input_from_message import *
from routing import *


#################
# vars and init #
#################

discord_token = os.environ.get("DISCORD_TOKEN")
tz = pytz.timezone("Europe/Berlin")

logging.basicConfig(encoding='utf-8', level=logging.INFO, format=f"%(filename)20s:%(lineno)-3s - %(funcName)-30s %(message)s")
logging.getLogger("discord").setLevel(logging.ERROR)

discordClient = discord.Client()
DiscordComponents(discordClient)


########################
# commands and actions #
########################

def parse_cmd(cmd) -> SimpleNamespace:
    try:
        cmd = json.loads(cmd)
    except ValueError:
        cmd, *args = cmd.split(" ")
        cmd = json.loads(Login.cmd(cmd.upper()))

    return SimpleNamespace(**cmd)


async def perform(state, cmd):
    while cmd != None: # chaining commands       
        input = parse_cmd(cmd)

        if input.action != "LOGIN" or type(input.input) != int:
            logging.info(f"{input.action}(state, cmd.input = {input.input}, cmd.result = {input.result})")
        else: # do not show numpad input
            logging.info(f"{input.action}(state, cmd.input = ?, cmd.result = {input.result})")

        cmd = await actions.get(input.action, other_action)(state, input)


########################
# handle button clicks #
########################

@discordClient.event
async def on_button_click(interaction):
    logging.info("------------------------------------------------------------------------")     
    logging.info(f"msg.id = {interaction.message.id}")
    
    state = get_state(interaction)
    cmd = interaction.custom_id    
    await perform(state, cmd)


#########################
# process text messages #
#########################
   
@discordClient.event
async def on_message(msg):
    if isinstance(msg.channel, discord.channel.DMChannel) and msg.author != discordClient.user:        
        logging.info("------------------------------------------------------------------------")
        logging.info(f"msg.id = {msg.id}")
        
        state = get_state(msg)

        # waiting for input when already logged in
        if state.current != None and state.current.name != None: 
            callback = callbacks.get(state.current.name)

            if (callback != None): 
                logging.info(f"callback with input: {msg.content}")
                cmd = await callback(state, msg.content)
                await perform(state, cmd)
                
            return

        # waiting for login command
        cmd = parse_cmd(msg.content)
        if cmd.action.upper() == Login.name:             
            await login(state, cmd)
        else:
            logging.info(f"command not recognised: {state.interaction.content}")
            await state.current.respond()

   
########
# main #
########

@discordClient.event
async def on_ready():
    logging.info("discord connected...")

logging.info("starting bot...")
if __name__ == "__main__":
    discordClient.run(discord_token)
