# Template interfaces for the Azul game framework
# This provides the abstract base classes that the azul_* modules depend on

import abc


class GameState:
    """Abstract base class for game state representation."""
    
    def __init__(self, num_agents):
        self.num_agents = num_agents


class GameRule(abc.ABC):
    """Abstract base class for game rule engines."""
    
    def __init__(self, num_of_agent):
        self.num_of_agent = num_of_agent
        self.current_agent_index = 0
        self.current_game_state = None
    
    @abc.abstractmethod
    def validAction(self, action, actions):
        """Check if an action is valid given the list of legal actions."""
        pass
    
    @abc.abstractmethod
    def initialGameState(self):
        """Return the initial game state."""
        pass
    
    @abc.abstractmethod
    def generateSuccessor(self, state, action, agent_id):
        """Generate the successor state after applying an action."""
        pass
    
    @abc.abstractmethod
    def getNextAgentIndex(self):
        """Get the index of the next agent to play."""
        pass
    
    @abc.abstractmethod
    def gameEnds(self):
        """Check if the game has ended."""
        pass
    
    @abc.abstractmethod
    def calScore(self, game_state, agent_id):
        """Calculate the final score for an agent."""
        pass
    
    @abc.abstractmethod
    def getLegalActions(self, game_state, agent_id):
        """Get the list of legal actions for an agent."""
        pass


class Agent:
    """Abstract base class for game agents/players."""
    
    def __init__(self, agent_id):
        self.id = agent_id
    
    def SelectAction(self, actions, game_state):
        """Select an action from the list of legal actions."""
        import random
        return random.choice(actions)


class Displayer(abc.ABC):
    """Abstract base class for game display/visualization."""
    
    @abc.abstractmethod
    def InitDisplayer(self, runner):
        """Initialize the display system."""
        pass
    
    @abc.abstractmethod
    def StartRound(self, game_state):
        """Display the start of a new round."""
        pass
    
    @abc.abstractmethod
    def ExcuteAction(self, player_id, move, game_state):
        """Display the execution of an action."""
        pass
    
    @abc.abstractmethod
    def TimeOutWarning(self, runner, agent_id):
        """Display a timeout warning."""
        pass
    
    @abc.abstractmethod
    def IllegalWarning(self, runner, agent_id, exception):
        """Display an illegal move warning."""
        pass
    
    @abc.abstractmethod
    def EndRound(self, game_state):
        """Display the end of a round."""
        pass
    
    @abc.abstractmethod
    def EndGame(self, game_state, scores):
        """Display the end of the game."""
        pass