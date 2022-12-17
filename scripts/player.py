from action import Action
import numpy as np


class Player:
    def __init__(self,name,team_id,stepSize,shooting_ability,defense_ability,pass_ability):
        self.name = name
        self.stateDict = {}
        self.FIELDS = ['team_id','posx','posy','control','action','defense_ability','shooting_ability','pass_ability','scored','pass']
        self.stepSize = stepSize
        self.ACTION = Action()
 
        self.stateDict['team_id'] = team_id
        self.stateDict['action']  = self.ACTION.NONE
        self.stateDict['shooting_ability'] = shooting_ability
        self.stateDict['defense_ability']  = defense_ability
        self.stateDict['pass_ability'] = pass_ability
        self.stateDict['scored'] = False
        self.stateDict['control'] = 0
        self.stateDict['posx'],self.stateDict['posy']= None,None
        self.stateDict['pass'] = False
        self.stateDict['stolen'] = False
        self.stateDict['win'] = {'0':0,'1':0}
        self.stateDict['threepointer'] = 0
        self.stateDict['onepointer'] = 0
        
    def setState(self,stateVectorGlobal):
        player_state = stateVectorGlobal[self.name]
        for field in self.FIELDS:
            self.stateDict[field] = player_state[field]
    
    def getObservation(self):
        return self.stateDict
    
    def takeStep(self,stateVectorGlobal,ball:object,arena:object):
        stateVectorGlobal = self.ACTION.perform(stateVectorGlobal,self.name,self.stepSize,ball,arena)
        return stateVectorGlobal


class PlayerObservation:
    def __init__(self,stateDict,currentagent,agentKeys,ball,arena):
        self.currentagent,self.agentKeys,self.stateDict,self.BALL,self.ARENA = currentagent,agentKeys,stateDict,ball,arena
     
    def distance(self,coord_x1,coord_y1,coord_x2,coord_y2):
        return((coord_x1-coord_x2)**2 + (coord_y1 - coord_y2)**2)**(0.5)
    
    def distanceFromPossessor(self):
        px,py = self.stateDict[self.currentagent]['posx'],self.stateDict[self.currentagent]['posy']
        for agent in self.agentKeys:
            if self.stateDict[agent]['control']==1:
                possessor = agent
                pospx,pospy = self.stateDict[possessor]['posx'],self.stateDict[possessor]['posy']           
                relativeDistance = self.distance(px,py,pospx,pospy)    
                return np.round(relativeDistance,3)
            elif self.stateDict[self.currentagent]['control'] == 1:return 0
        return -1
    
    def distancefromTeammate(self):
        px,py = self.stateDict[self.currentagent]['posx'],self.stateDict[self.currentagent]['posy']
        for agent in self.agentKeys:
            if agent[-3]==self.currentagent[-3]:
                teammate = agent
                pospx,pospy = self.stateDict[teammate]['posx'],self.stateDict[teammate]['posy']         
                relativeDistance = self.distance(px,py,pospx,pospy)    
                return np.round(relativeDistance,3)
    
    def playerhasControl(self):
        if self.stateDict[self.currentagent]['control']==1:return 1
        else:return 0
    
    def opponenthasControl(self):
        for agent in self.agentKeys:
            if agent[-3]==self.currentagent[-3]:continue
            else:
                if self.stateDict[agent]['control']==1:return 1
        return 0
    
    def teamhasControl(self):
        for agent in self.agentKeys:
            if agent[-3] == self.currentagent[-3]:
                if self.stateDict[agent]['control']==1 or self.stateDict[self.currentagent]['control']==1:return 1
                else:return 0
        return 0
    
    def distancetoOpponents(self):
        px,py = self.stateDict[self.currentagent]['posx'],self.stateDict[self.currentagent]['posy']
        otheropponentsdist = []
        for agent in self.agentKeys:
            if agent[-3] != self.currentagent[-3]:
                relativeDistance = self.distance(self.stateDict[agent]['posx'],self.stateDict[agent]['posy'],px,py)
                otheropponentsdist.append(np.round(relativeDistance,3))
        return otheropponentsdist
    
    def distancetoBall(self):
        px,py = self.stateDict[self.currentagent]['posx'],self.stateDict[self.currentagent]['posy']
        bx,by = self.BALL.getCoords()
        return np.round(self.distance(px,py,bx,by),3)

    def distancetoBasketCurrent(self):
        px,py = self.stateDict[self.currentagent]['posx'],self.stateDict[self.currentagent]['posy']
        bx,by = self.ARENA.basket_x,self.ARENA.basket_y
        return np.round(self.distance(px,py,bx,by),0)
    
    def distancetoBasketTeammate(self):
        for agent in self.agentKeys:
            if agent[-3]==self.currentagent[-3]:
                teammate = agent
                pospx,pospy = self.stateDict[teammate]['posx'],self.stateDict[teammate]['posy']         
                relativeDistance = self.distance(pospx,pospy,self.ARENA.basket_x,self.ARENA.basket_y)    
                return np.round(relativeDistance,3)
    def distancetoBasketOpponents(self):
        otheropponentsdist = []
        for agent in self.agentKeys:
            if agent[-3] != self.currentagent[-3]:
                relativeDistance = self.distance(self.stateDict[agent]['posx'],self.stateDict[agent]['posy'],self.ARENA.basket_x,self.ARENA.basket_y)
                otheropponentsdist.append(np.round(relativeDistance,3))
        return otheropponentsdist