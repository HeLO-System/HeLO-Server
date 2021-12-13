from discord_components.interaction import Interaction
from object_models import *

user_states = {}


#########################################################################
# user state to store the current session state                         #
# user states are stores in a global map to get access by userid        #
#########################################################################


class UserState():

    user_states = []

    def __init__(self, userid):
        global user_states
        self.userid = str(userid)
        self.interaction = None
        self.message = None
        self.user = None
        self.stack = []
        user_states[str(userid)] = self


    def clear(self):
        user_states[self.userid] = None
        self.userid = None
        self.interaction = None
        self.message = None
        self.input_message = None
        self.user = None
        self.stack = []


    @property
    def current(self) -> ObjectState:
        current = len(self.stack) - 1
        return self.stack[current] if current >= 0 else None


    @property
    def parent(self) -> ObjectState:
        parent = len(self.stack) - 2
        return self.stack[parent] if parent >= 0 else None


    def push(self, state : ObjectState, when = None):
        if when == None or when:
            self.stack.append(state)
        else:
            state = self.current
            
        state.interaction = self.interaction


    def pop(self) -> ObjectState:
        return self.stack.pop(len(self.stack) - 1)

    
    def pop_to(self, state_type) -> ObjectState:
        matches = [s for s in self.stack if type(s) == state_type]
        states = []
        if len(matches) > 0:
            while type(self.current) != state_type:
                states.append(self.pop())
        
        return states
        

    def find(self, state_type) -> ObjectState:
        for i in reversed(range(len(self.stack) - 1)):
            if type(self.stack[i]) == state_type:
                return self.stack[i]
            
            
def get_state(interactionOrMessage) -> UserState:    
    userid = str(interactionOrMessage.author.id)
    if not userid in user_states or user_states[userid] == None:
        user_states[userid] = UserState(userid)
    
    state = user_states[userid]
    if type(interactionOrMessage) == Interaction:
        state.interaction = interactionOrMessage
        state.message = None
    else:
        state.interaction = None
        state.message = interactionOrMessage
        
    return state