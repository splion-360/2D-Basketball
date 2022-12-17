from field import Arena,Ball
from action import Action
from player import Player,PlayerObservation
import numpy as np
import random
import pygame
from pygame import display
from copy import copy
import functools
import itertools
from gym.spaces import Dict as GymDict, Box, Discrete

class BasketBallEnv():
    def __init__(self,n_players,n_teams,agent_params:dict,grid=False,ticks=150,with_pygame=True):
        # Create an Arena
        
        self.ARENA = Arena((400,400),180,40,(200,400),3*np.pi/2,np.pi/2)
        self.BALL  = Ball(0,0)
        self.grid,self.ticks  = grid,ticks
        self.ACTION = Action()
        
        # Team Colors
        self.RED      = pygame.Color(255,0,0)
        self.YELLOW  =  pygame.Color(148,0,211)
        
        # Field Colors
        self.BLACK = pygame.Color(0,0,0)
        self.WHITE = pygame.Color(255,255,255)
        
        # Ball Color
        self.GREEN = pygame.Color(0,255,0)
        self.BLUE  = pygame.Color(0,0,255)
        
        self.n_players = n_players
        self.players = []
        n_players_ = list(range(1,self.n_players+1))
        n_teams_   = list(itertools.chain(*[[element]*n_teams for element in range(1,n_teams+1)]))

        # Create players
        shooting_ability = agent_params['shooting_ability']
        pass_ability = agent_params['pass_ability']
        stepSize = agent_params['stepSize']     
        defense_ability = agent_params['defense_ability']
        

        for i,(player,team) in enumerate(zip(n_players_,n_teams_)):
            self.players.append(Player(f'player_{team}_{player}',team,stepSize[i],shooting_ability[i],defense_ability[i],pass_ability[i]))
        self.possible_agents = [agents.name for agents in self.players]
        self.possession = {agent:0 for agent in self.possible_agents}
        # Create the pygame window
        self.pygame = with_pygame
        
        if self.pygame:
            pygame.init()
            pygame.display.set_caption('BB Simulator')
            self.field = pygame.display.set_mode(size=(self.ARENA.arena_x,self.ARENA.arena_y))
        self.gamereset = False
        self.reset()
        

    @functools.lru_cache(maxsize=None)
    def action_space(self,agent):
        return Discrete(len(self.ACTION.ACTION_LIST))
    
    @functools.lru_cache(maxsize=None)
    def observation_space(self, agent):
        fr,bs = self.ARENA.arena_x*3,self.ARENA.blockSize
        obs = {'obs':Box(low=-bs,high=fr,shape=(8,),dtype=np.float32),'state':Box(low=-bs,high=fr,shape=(4,),dtype=np.float32)}
        return GymDict(obs)
        
    def generateRandomCoordinates(self):
        halfstep = self.ARENA.blockSize//2
        cd_x,cd_y = self.ARENA.blockSize,self.ARENA.blockSize
        while cd_x%self.ARENA.blockSize == 0 or cd_y%self.ARENA.blockSize == 0:
            cd_x = random.randrange(halfstep,self.ARENA.arena_x,step=halfstep)
            cd_y = random.randrange(halfstep,self.ARENA.arena_y,step=halfstep)
        return (cd_x,cd_y)

    def distance(self,coord_x1,coord_y1,coord_x2,coord_y2):
        return((coord_x1-coord_x2)**2 + (coord_y1 - coord_y2)**2)**(0.5)
    
    def reset(self):
        # Set random positions 
        if self.pygame:self.field.fill(self.WHITE)
        
        self.timestep = 0
        self.agents = copy(self.possible_agents)
        if self.gamereset:
            self.rewards = {agent: self.rewards[agent]*0.01 for agent in self.agents}
            self.gamereset = False
        else:
            self.rewards = {agent: 0 for agent in self.agents}
        self.globalStateDict = {} 
        
        for player in self.players:
            player.stateDict['posx'],player.stateDict['posy'] = self.generateRandomCoordinates()
            self.globalStateDict[player.name]=player.getObservation()
        
        # Randomly give control of the ball to a player
        playerwithposs = self.players[random.randint(1,self.n_players-1)]
        playerwithposs.stateDict['control'] = 1
        self.BALL.update(playerwithposs.stateDict['posx'],playerwithposs.stateDict['posx'])
        
        ## Observation Vector for each player
        observations = {}
        keys = np.array(list(self.globalStateDict.keys()))
        for i,player in enumerate(keys):
            mask = np.ones_like(keys,dtype=bool)
            mask[i] = False
            otherplayers = keys[mask,...]
            obsObj = PlayerObservation(self.globalStateDict,player,otherplayers,self.BALL,self.ARENA)
            # Distance relative to agent with posession
            obs_1 = obsObj.distanceFromPossessor()
            # has control
            obs_2 = obsObj.playerhasControl()
            # team has control
            obs_3 = obsObj.teamhasControl()
            # Distance relative to teammate
            obs_4 = obsObj.distancefromTeammate()
            # opponent has control
            obs_5 = obsObj.opponenthasControl()
            # distance relative to other opponents
            obs_6,obs_7 = obsObj.distancetoOpponents()
            # distance to the ball
            obs_8 = obsObj.distancetoBall()
            
            # distance to basket
            obs_9 = obsObj.distancetoBasketTeammate()
            obs_10 = obsObj.distancetoBasketCurrent()

            obs_11,obs_12 = obsObj.distancetoBasketOpponents()            

            observations[player] = {'obs':(obs_1,obs_2,obs_3,obs_4,obs_5,obs_6,obs_7,obs_8),\
                                    'state':(obs_9,obs_10,obs_11,obs_12)} #'state':(obs_1,obs_2,obs_3,obs_4,obs_5,obs_6,obs_7,obs_8,obs_9,obs_10,obs_11,obs_12)
        
        return observations
    
    def getTeammate(self,currentagent,agentKeys):
        for agent in agentKeys:
            if currentagent[-3]==agent[-3]:
                return agent
    def getOpponent(self,currentagent,agentKeys):
        opponents = []
        for agent in agentKeys:
            if currentagent[-3] != agent[-3]:
                opponents.append(agent)
        return opponents
    
    def gameOver(self):
        if self.pygame:
            self.field.fill(self.WHITE)
            font = pygame.font.Font('freesansbold.ttf', 20)
            text = font.render('GameOver', True, self.GREEN, self.BLUE)
            textRect = text.get_rect()
            textRect.center = (self.ARENA.arena_x // 2, self.ARENA.arena_y // 2)
            self.field.blit(text, textRect)
            self.render()
        self.gamereset = True
        self.reset()
        
    def render(self):
        display.update()

    def mapRange(self,value, inMin, inMax, outMin, outMax):
        return outMin + (((value - inMin) / (inMax - inMin)) * (outMax - outMin))
        
    def step(self,action):
        
        truncations,terminations  = {agent: False for agent in self.agents},{agent: False for agent in self.agents}

        keys = np.array(list(self.globalStateDict.keys()))
        ## Assuming I get a dictionary  indicating the actions for each agent
        for i,player in enumerate(keys):
            mask = np.ones_like(keys,dtype=bool)
            mask[i] = False
            otherplayers = keys[mask,...]
            
            self.globalStateDict[player]['action'] = self.ACTION.mapNumbertoAction(action[player])
            stateVectorGlobal = self.players[i].takeStep(self.globalStateDict,self.BALL,self.ARENA)
            
            # Give rewards based on the performance
            posx,posy = self.globalStateDict[player]['posx'],self.globalStateDict[player]['posy']
            teammate = self.getTeammate(player,otherplayers)

            if stateVectorGlobal[player]['stolen']:
                self.rewards[player]-=1/(200*self.ticks)
                self.rewards[teammate] -= 1/(500*self.ticks)
                stateVectorGlobal[player]['stolen'] = False
  
            # Give them an incentive to move towards the cell containing the ball

            if (posx,posy) == (self.BALL.b_x,self.BALL.b_y):
                self.rewards[player]   += 1
                self.rewards[teammate] += 0.5             

            self.rewards[player]   += self.mapRange((1/(self.distance(posx,posy,self.BALL.b_x,self.BALL.b_y)+1e-07)),0,800,0,2e-05)
            self.rewards[teammate] += self.mapRange((1/(self.distance(posx,posy,self.BALL.b_x,self.BALL.b_y)+1e-07)),0,800,0,1e-05)

            # Penalise them for not finding the ball after some number of ticks
     
            if stateVectorGlobal[player]['control']!=1 or stateVectorGlobal[teammate]['control']!=1:
                self.possession[player],self.possession[teammate] = 0,0
                if (self.possession[player] == 0 or self.possession[teammate] == 0) and self.timestep > 30:
                    self.rewards[player]   -=5
                    self.rewards[teammate] -=5

            if stateVectorGlobal[player]['control'] == 1:
                if stateVectorGlobal[player]['pass']:
                    stateVectorGlobal[player]['win']['1']+=1
                else:
                    stateVectorGlobal[player]['win']['0']+=1
                self.possession[player]+= 1
                                
                self.possession[player] < 10: self.rewards[player] 
                self.rewards[player] += 1/(20*self.ticks)
                self.rewards[teammate]+= 1/(20*self.ticks)
   

            if stateVectorGlobal[player]['scored'] and posx > 3*self.ARENA.three_pointer_x:
                terminations = {agent: False for agent in self.agents}
                terminations[player] = True
                self.rewards[player] += 30                
                if stateVectorGlobal[teammate]['pass']:self.rewards[teammate]+=0
                else:self.rewards[teammate]+= 20

                ## Negate the rewards of the opponent
                opp1,opp2 = self.getOpponent(player,otherplayers)
                self.rewards[opp1] -= 15
                self.rewards[opp2] -= 15
                
                self.globalStateDict[player]['scored']  = False
                self.globalStateDict[player]['control'] = 0
                self.globalStateDict[player]['threepointer']+=1
                self.gameOver()

            if stateVectorGlobal[player]['scored']: #and posx < 3*self.ARENA.three_pointer_x
                terminations = {agent: False for agent in self.agents}
                terminations[player] = True
                self.rewards[player] += 20
                if stateVectorGlobal[teammate]['pass']:self.rewards[teammate]+=0
                else:self.rewards[teammate] += 10
                self.globalStateDict[player]['onepointer']+=1
                ## Negate the rewards of the opponent
                opp1,opp2 = self.getOpponent(player,otherplayers)
                self.rewards[opp1] -= 5
                self.rewards[opp2] -= 5
                self.globalStateDict[player]['scored'] = False
                self.globalStateDict[player]['control'] = 0
                self.gameOver()
                
        if self.pygame:self.updatePygameInterface()
        if self.timestep > self.ticks:
            self.rewards = {agent: -1 for agent in self.agents} #self.rewards[agent]
            truncations = {agent: True for agent in self.agents}
            self.timestep = -1
            for player in self.players:
                player.stateDict['posx'],player.stateDict['posy'] = self.generateRandomCoordinates()
                self.globalStateDict[player.name]=player.getObservation()
            playerwithposs = self.players[random.randint(1,self.n_players-1)]
            playerwithposs.stateDict['control'] = 1
            self.BALL.update(playerwithposs.stateDict['posx'],playerwithposs.stateDict['posx'])
        self.timestep+=1

        observations = {}
        for i,player in enumerate(keys):
            mask = np.ones_like(keys,dtype=bool)
            mask[i] = False
            otherplayers = keys[mask,...]
            obsObj = PlayerObservation(self.globalStateDict,player,otherplayers,self.BALL,self.ARENA)    
            obsDO = obsObj.distancetoOpponents()
            obsball = obsObj.distancetoBall()
            obsbask = obsObj.distancetoBasketOpponents()
            observations[player] = {'obs':(obsObj.distanceFromPossessor(),obsObj.playerhasControl(),\
                        obsObj.teamhasControl(),obsObj.distancefromTeammate(),\
                        obsObj.opponenthasControl(),obsDO[0],obsDO[1],obsball),\
                            'state':(obsObj.distancetoBasketTeammate(),obsObj.distancetoBasketCurrent(),obsbask[0],obsbask[1])}

            # # 'state':(obsObj.distanceFromPossessor(),obsObj.playerhasControl(),\
            #             obsObj.teamhasControl(),obsObj.distancefromTeammate(),\
            #             obsObj.opponenthasControl(),obsDO[0],obsDO[1],obsball[0])}
        
        infos = {agent: {} for agent in self.agents}
        return observations, self.rewards, terminations, truncations, infos
    
    def close(self):
        pass
    
    def drawGrid(self):
        blockSize = self.ARENA.blockSize #Set the size of the grid block
        for x in range(0, self.ARENA.arena_x, blockSize):
            for y in range(0, self.ARENA.arena_y, blockSize):
                rect = pygame.Rect(x, y, blockSize, blockSize)
                pygame.draw.rect(self.field, self.BLACK, rect, 1)        
    
    def updatePygameInterface(self):
            noPoss,noSpawn = True,True
            self.field.fill(self.WHITE)
            if self.grid:self.drawGrid()
            pygame.draw.arc(self.field,self.BLACK, [0,0,self.ARENA.three_pointer_x,self.ARENA.three_pointer_y], \
                            self.ARENA.arc_start_angle, self.ARENA.arc_stop_angle,5)
            
            pygame.draw.rect(self.field,self.BLACK,(self.ARENA.basket_x,self.ARENA.basket_y,self.ARENA.blockSize//2,self.ARENA.blockSize))
            for player in self.globalStateDict.keys():
                if player[-3] == str(1):
                    if player[-1] == str(1):
                        pygame.draw.circle(self.field,self.RED,(self.globalStateDict[player]['posx'],\
                                                            self.globalStateDict[player]['posy']),15)
                    else:
                        pygame.draw.circle(self.field,self.RED,(self.globalStateDict[player]['posx'],\
                                                            self.globalStateDict[player]['posy']),15,width=5)
                elif player[-3] == str(2):
                    if player[-1] == str(3):
                        pygame.draw.circle(self.field,self.YELLOW,(self.globalStateDict[player]['posx'],\
                                                                self.globalStateDict[player]['posy']),15)
                    else:
                        pygame.draw.circle(self.field,self.YELLOW,(self.globalStateDict[player]['posx'],\
                                                                self.globalStateDict[player]['posy']),15,width=5)
                        
                if self.globalStateDict[player]['control'] == 1:
                    noPoss = False
                if (self.globalStateDict[player]['posx'],self.globalStateDict[player]['posy']) == self.BALL.getCoords():
                    noSpawn = False
                    
            if not noPoss or not noSpawn: pygame.draw.circle(self.field,self.GREEN,(self.BALL.getCoords()),8)
            else:pygame.draw.circle(self.field,self.BLUE,(self.BALL.getCoords()),8)