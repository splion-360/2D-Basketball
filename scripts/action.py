import numpy as np
import random 

class Action:
    def __init__(self):
        self.SHOOT     = 'SHOOT'
        self.PASS      = 'PASS'
        self.STEAL     = 'STEAL'
        self.MOVE_UP   = 'UP'
        self.MOVE_DOWN = 'DOWN'
        self.MOVE_LEFT = 'LEFT'
        self.MOVE_RIGHT= 'RIGHT'
        self.NONE      = 'NONE'
        self.ACTION_LIST = [self.SHOOT,self.PASS,self.STEAL,self.MOVE_UP,self.MOVE_DOWN,self.MOVE_LEFT,self.MOVE_RIGHT,self.NONE]
        
    def mapNumbertoAction(self,number):return self.ACTION_LIST[number]

    def checkGridOccupied(self,x,y):
        for player in self.stateVectorGlobal.keys():
            px,py = self.stateVectorGlobal[player]['posx'],self.stateVectorGlobal[player]['posy']
            if (px,py) == (x,y):return True
        return False
    
    def hasBall(self):
        for player in self.stateVectorGlobal.keys():
            px,py = self.stateVectorGlobal[player]['posx'],self.stateVectorGlobal[player]['posy']
            if self.stateVectorGlobal[player]['control'] == 1:
                self.BALL.update(px,py)
                return
            if (px,py) == self.BALL.getCoords() and self.stateVectorGlobal[player]['control'] != 1:
                self.stateVectorGlobal[player]['control'] = 1
                self.BALL.update(px,py)
            else:self.stateVectorGlobal[player]['control'] = 0
    
    def perform(self,stateVectorGlobal,name,stepSize,ball,arena):
    
        self.NAME,self.BALL,self.ARENA = name,ball,arena
        self.stateVectorGlobal = stateVectorGlobal
        action = self.stateVectorGlobal[self.NAME]['action']
        px,py = self.stateVectorGlobal[self.NAME]['posx'],self.stateVectorGlobal[self.NAME]['posy']
        self.hasBall()
        
        if action == self.MOVE_UP and py > stepSize: #self.ARENA.blockSize//2 #stepSize//2
            projx,projy = self.stateVectorGlobal[self.NAME]['posx'],self.stateVectorGlobal[self.NAME]['posy']-stepSize
            if not self.checkGridOccupied(projx,projy):
                self.stateVectorGlobal[self.NAME]['posy'] -= stepSize
                
        elif action == self.MOVE_DOWN and py+(stepSize)<self.ARENA.arena_y:
            projx,projy = self.stateVectorGlobal[self.NAME]['posx'],self.stateVectorGlobal[self.NAME]['posy']+stepSize
            if not self.checkGridOccupied(projx,projy):
                self.stateVectorGlobal[self.NAME]['posy'] += stepSize
            
        elif action == self.MOVE_LEFT and px> stepSize:
            projx,projy = self.stateVectorGlobal[self.NAME]['posx']-stepSize,self.stateVectorGlobal[self.NAME]['posy']
            if not self.checkGridOccupied(projx,projy): 
                self.stateVectorGlobal[self.NAME]['posx'] -= stepSize
                
        elif action == self.MOVE_RIGHT and px+(stepSize)<self.ARENA.arena_x:
            projx,projy = self.stateVectorGlobal[self.NAME]['posx']+stepSize,self.stateVectorGlobal[self.NAME]['posy']
            if not self.checkGridOccupied(projx,projy): 
                self.stateVectorGlobal[self.NAME]['posx'] += stepSize
        elif action == self.PASS: self._PASS()
        elif action == self.SHOOT:self._SHOOT()
        elif action == self.STEAL:self._STEAL()
        elif action == self.NONE: self._NONE()
        else:pass
        return self.stateVectorGlobal
    
    def _NONE(self):
        pass
    
    def _PASS(self):
        px,py = self.stateVectorGlobal[self.NAME]['posx'],self.stateVectorGlobal[self.NAME]['posy']
        if self.stateVectorGlobal[self.NAME]['control']==0:return self.stateVectorGlobal
        else:
            for player in self.stateVectorGlobal.keys():
                if(player[-3] == self.NAME[-3]):
                    teammate = player
                    break
                    
            block_diag_length = (2**(0.5))*self.ARENA.blockSize
            threshDistance =  4*block_diag_length 
            passx,passy  = self.stateVectorGlobal[teammate]['posx'],self.stateVectorGlobal[teammate]['posy']
            passDistance = self.distance(px,passx,py,passy)
            
            if passDistance<threshDistance:
                if random.uniform(0,1) <= self.stateVectorGlobal[self.NAME]['pass_ability']:
                    self.stateVectorGlobal[self.NAME]['control'] = 0
                    self.stateVectorGlobal[teammate]['control'] = 1
                    self.stateVectorGlobal[self.NAME]['pass'] = True
                    return self.stateVectorGlobal
                else:
                    swayx,swayy  = random.sample([-40,-80,40,80],2)
                    bx,by = self.stateVectorGlobal[teammate]['posx']+swayx,self.stateVectorGlobal[teammate]['posy']+swayy
                    self.BALL.update(bx,by)
                    self.stateVectorGlobal[self.NAME]['control'] = 0
                    return self.stateVectorGlobal
            else:
                return self.stateVectorGlobal
                   
    
    def distance(self,coord_x1,coord_y1,coord_x2,coord_y2): #Helper function
        return((coord_x1-coord_x2)**2 + (coord_y1 - coord_y2)**2)**(0.5)
    
    def distance_probability(self): #Helper function
        px = self.stateVectorGlobal[self.NAME]['posx']
        py = self.stateVectorGlobal[self.NAME]['posy']
        max_dist = self.ARENA.maxDistfromBasket
        curr_dist = self.distance(self.ARENA.basket_x,self.ARENA.basket_y,px,py)
        return 1 - curr_dist/max_dist
    
    def defense_probability(self): #Helper function
        px = self.stateVectorGlobal[self.NAME]['posx']
        py = self.stateVectorGlobal[self.NAME]['posy']
        max_dist = self.distance(0,0,self.ARENA.arena_x,self.ARENA.arena_y)
        nearest_player_dist = max_dist
        for player in self.stateVectorGlobal.keys():
            if(player == self.NAME) or player[-3] == self.NAME[-3]:continue
            else:
                dist = self.distance(self.stateVectorGlobal[player]['posx'],self.stateVectorGlobal[player]['posy'],px,py)
                if(dist < nearest_player_dist):
                    nearest_player_dist = dist
                    nearest_player_name = player
        return (1 - nearest_player_dist/max_dist)*self.stateVectorGlobal[nearest_player_name]['defense_ability']
    
    def _SHOOT(self):  #Will return a truth value saying scored or not
        if self.stateVectorGlobal[self.NAME]['control']==0:return self.stateVectorGlobal
        
        shooting_ability     = self.stateVectorGlobal[self.NAME]['shooting_ability']  ##Accessing shooting ability as this
        distance_probability = self.distance_probability()
        defence_probability  = self.defense_probability()
    
        #Choosing random y coordinate near basket for the ball to land on
        rand_y = self.ARENA.basket_y + random.choice([-1*self.ARENA.blockSize,0*self.ARENA.blockSize,1*self.ARENA.blockSize,2*self.ARENA.blockSize]) 
        self.BALL.update(self.ARENA.basket_x+self.ARENA.blockSize//2,rand_y)

        success_prob = shooting_ability*distance_probability*(1-defence_probability)  
        if(np.random.uniform(0,1)<=success_prob):
            self.stateVectorGlobal[self.NAME]['scored']  = True
        self.stateVectorGlobal[self.NAME]['control'] = 0
        return self.stateVectorGlobal
               
    def _STEAL(self): #Function will change the stateVectorGlobal
        player_with_possession = None
        for player in self.stateVectorGlobal.keys(): #Getting the player in possession
            if (self.stateVectorGlobal[player]['control'] == 1):
                player_with_possession = player
                break
        if player_with_possession == None:
            return self.stateVectorGlobal
        else:
            px = self.stateVectorGlobal[self.NAME]['posx']
            py = self.stateVectorGlobal[self.NAME]['posy']

            posp_x = self.stateVectorGlobal[player_with_possession]['posx']
            posp_y = self.stateVectorGlobal[player_with_possession]['posy']

            block_diag_length = (2**(0.5))*self.ARENA.blockSize
            threshold_length =  2*block_diag_length # must be within two blocks to steal the ball

            distance_to_player_in_poss = self.distance(px,py,posp_x,posp_y)
            if(distance_to_player_in_poss > threshold_length): #Do nothing
                return self.stateVectorGlobal
        
            else:
                defence_ability = self.stateVectorGlobal[self.NAME]['defense_ability']
                if(np.random.uniform(0,1)<=defence_ability): # Steal succeeds
                    self.stateVectorGlobal[self.NAME]['control'] = 1  ## Changing the ball the control
                    self.stateVectorGlobal[player_with_possession]['stolen'] = True
                    self.stateVectorGlobal[player_with_possession]['control'] = 0
                    return self.stateVectorGlobal

                else: #Do nothing
                    return self.stateVectorGlobal
