import json
import logging
from types import SimpleNamespace

#########################################################################################
# state objects to hold the state of the current and previous steps                     #
# option objects to hold the parameters when executing the next step                    #
#########################################################################################

class ObjectState:
    name = None
    def __init__(self, name, state, action = None):
        self.interaction = state.interaction
        self.message = state.message
        self.options = []
        self.input = ""
        self.name = name
        self.action = action
        
    def __repr__(self): return f"{self.name}(input = {self.input}, options = {self.options})"
      
    def last_option(self):
        return len(self.options) - 1

    async def respond(self, content = "", embed = None, components = None):
        await self.interaction.respond(type = 7, content = content, embed = embed, components = components)

    
class Login(ObjectState):
    name = "LOGIN"
    def __init__(self, state): 
        ObjectState.__init__(self, Login.name, state)

    def cmd(input = None) -> str:
        return json.dumps({ "action": Login.name, "input": input, "result": None })
        
        
class Logout(ObjectState):
    name = "LOGOUT"
    def __init__(self, state): 
        ObjectState.__init__(self, Logout.name, state)
    

class Home(ObjectState):
    name = "HOME"
    def __init__(self, state): 
        ObjectState.__init__(self, Home.name, state)

    def cmd(state) -> str:
        return json.dumps({ "action": Home.name, "input": None, "result": None })

        
class ManageClans(ObjectState):
    name = "MANAGE_CLANS"
    def __init__(self, state):
        ObjectState.__init__(self, ManageClans.name, state)

    def cmd(state) -> str:
        return json.dumps({ "action": ManageClans.name, "input": None, "result": None, "callback": None })

        
class AddClan(ObjectState):
    name = "ADD_CLAN"
    def __init__(self, state, next_step, title): 
        ObjectState.__init__(self, AddClan.name, state)
        self.next_step = next_step
        self.title = title

    def cmd(state) -> str:
        return json.dumps({ "action": AddClan.name, "input": None, "result": None, "callback": None })

        
class EditClanOption:
    def __init__(self, next_step = None, title = ""):
        self.next_step = next_step
        self.title = title

    def __repr__(self): return json.dumps(self.__dict__)


class EditClan(ObjectState):
    name = "EDIT_CLAN"
    def __init__(self, state, next_step, title): 
        ObjectState.__init__(self, EditClan.name, state)
        self.next_step = next_step
        self.title = title

    def cmd(state, confirm = None, option = EditClanOption()) -> str:
        return json.dumps({ "action": EditClan.name, "input": state.current.last_option(), "result": confirm })


class DeleteClanOption:
    def __init__(self, next_step = None, title = ""):
        self.next_step = next_step
        self.title = title

    def __repr__(self): return json.dumps(self.__dict__)


class DeleteClan(ObjectState):
    name = "DELETE_CLAN"
    def __init__(self, state, next_step): 
        ObjectState.__init__(self, DeleteClan.name, state)
        self.next_step = next_step

    def cmd(state, confirm = None, option = DeleteClanOption()) -> str:
        state.current.options.append(option)
        return json.dumps({ "action": DeleteClan.name, "input": state.current.last_option(), "result": confirm })


class DeleteClanConfirmOption:
    def __init__(self, clan = None):
        self.clan = clan

    def __repr__(self): return json.dumps(self.__dict__)
        
                
class DeleteClanConfirm(ObjectState):
    name = "DELETE_CLAN_CONFIRM"
    def __init__(self, state): 
        ObjectState.__init__(self, DeleteClanConfirm.name, state)

    def cmd(state, confirm = None, option = DeleteClanOption()) -> str:
        state.current.options.append(option)
        return json.dumps({ "action": DeleteClanConfirm.name, "input": state.current.last_option(), "result": confirm })

        
class SelectFlag(ObjectState):
    name = "SELECT_FLAG"
    def __init__(self, state): 
        ObjectState.__init__(self, SelectFlag.name, state)

    def cmd(state, input = None, option = None) -> str:
        return json.dumps({ "action": SelectFlag.name, "input": input, "result": None })
    

class SelectClanOption:
    def __init__(self, selected = None, next_step = None, is_showing_coop = True, from_search = False, title = ""):
        self.selected = selected
        self.is_showing_coop = is_showing_coop
        self.from_search = from_search
        self.next_step = next_step
        self.title = title
            
    def __repr__(self): return json.dumps(self.__dict__)

      
class SelectClan(ObjectState):
    name = "SELECT_CLAN"
    def __init__(self, state): 
        ObjectState.__init__(self, SelectClan.name, state)

    def cmd(state, option = SelectClanOption()) -> str:
        state.current.options.append(option)
        return json.dumps({ "action": SelectClan.name, "input": state.current.last_option(), "result": None } )


class SearchClanOption:
    def __init__(self, selected = None, next_step = None, is_showing_coop = True, title = ""):
        self.is_showing_coop = is_showing_coop
        self.next_step = next_step
        self.title = title
            
    def __repr__(self): return json.dumps(self.__dict__)


class SearchClan(ObjectState):
    name = "SEARCH_CLAN"
    def __init__(self, state):
        ObjectState.__init__(self, SearchClan.name, state)

    def cmd(state, option = SelectClanOption()) -> str:
        state.current.options.append(option)
        return json.dumps({ "action": SearchClan.name, "input": state.current.last_option(), "result": None, "callback": None })


class InputFromMessage(ObjectState):
    name = "INPUT_FROM_MESSAGE"
    def __init__(self, state): 
        ObjectState.__init__(self, InputFromMessage.name, state)

    def cmd(state, result = None, option = None) -> str:
        state.current.options.append(option)
        return json.dumps({ "action": InputFromMessage.name, "input": state.current.last_option(), "result": result })

    def __repr__(self): return json.dumps(self.__dict__)


class NewMatchOption:
    def __init__(self, clan1 = None, next_step = None, title = ""):
        self.clan1 = clan1
        self.next_step = next_step
        self.title = title

    def __repr__(self): return json.dumps(self.__dict__)


class NewMatch(ObjectState):
    name = "NEW_MATCH"
    def __init__(self, state, clan1 = None, next_step = None): 
        ObjectState.__init__(self, NewMatch.name, state)
        self.next_step = next_step
        self.clan1 = clan1
        self.coop1 = None
        self.side1 = None
        self.score1 = None
        self.clan2 = None
        self.coop2 = None
        self.side2 = None
        self.score2 = None
        self.date = None
        self.map = None

    def cmd(state, option = NewMatchOption()) -> str:
        state.current.options.append(option)
        return json.dumps({ "action": NewMatch.name, "input": state.current.last_option(), "result": None })


class SelectMap():
    name = "SELECT_MAP"
    def cmd(state, map = None) -> str:
        return json.dumps({ "action": SelectMap.name, "input": None, "result": map })


class MatchDate(ObjectState):
    name = "MATCH_DATE"
    def cmd(state, date = None) -> str:
        return json.dumps({ "action": MatchDate.name, "input": None, "result": date })


class MatchResult(ObjectState):
    name = "MATCH_RESULT"
    def __init__(self, state): 
        ObjectState.__init__(self, MatchResult.name, state)
        
    def cmd(state, score1 = None, side1 = None) -> str:
        if score1 == None or side1 == None:
            return json.dumps({ "action": MatchResult.name, "input": None, "result": side1 })    
        else:
            return json.dumps({ "action": MatchResult.name, "input": None, "result": { "score1": score1, "side1": side1 } })


class MatchConfirm(ObjectState):
    name = "MATCH_CONFIRM"
    def __init__(self, state): 
        ObjectState.__init__(self, MatchConfirm.name, state)

    def cmd(state, confirm = None, option = None) -> str:
        state.current.options.append(option)
        return json.dumps({ "action": MatchConfirm.name, "input": state.current.last_option(), "result": confirm })


class InputFromMessageOption:
    def __init__(self, field = None, title = ""):
        self.field = field
        self.title = title

    def __repr__(self): return json.dumps(self.__dict__)


class SelectFlagOption:
    def __init__(self, field = ""):
        self.field = field


class MatchConfirmOption:
    def __init__(self, next_step = None, title = "", clan1 = None, coop1 = None, clan2 = None, coop2 = None, side1 = None, side2 = None, score1 = None, score2 = None, date = None, map = None, user1 = None, user2 = None):
        self.next_step = next_step
        self.title = title
        self.clan1 = clan1
        self.coop1 = coop1
        self.side1 = side1
        self.score1 = score1
        self.clan2 = clan2
        self.coop2 = coop2
        self.side2 = side2
        self.score2 = score2
        self.date = date
        self.map = map,
        self.user1 = user1,
        self.user2 = user2

    def __repr__(self): return json.dumps(self.__dict__)
        

class Return(ObjectState):
    name = "RETURN"
    def __init__(self, state):
        super().__init__(Return.name, state)
        
    def cmd(state, result) -> str:
        return json.dumps({ "action": Return.name, "input": None, "result": result })

    async def process_message(state, cmd : SimpleNamespace):
        object_state = state.pop()
        
        logging.info(f"{cmd}")
        result = ReturnProcess.cmd(state.current.name, cmd.result)
        return result


class ReturnProcess(ObjectState):
    name = "RETURN_PROCESS"
    def cmd(action, result) -> str:
        return json.dumps({ "action": action, "input": None, "result": result })

