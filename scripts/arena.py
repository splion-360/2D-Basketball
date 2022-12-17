




class Arena:
    def __init__(self,frame_size,basket_y,blockSize,three_pointer_cd,start_angle,stop_angle):
        self.arena_x,self.arena_y   = frame_size
        self.basket_x,self.basket_y = [0,basket_y]
        self.blockSize = blockSize 
        self.three_pointer_x,self.three_pointer_y = three_pointer_cd
        self.arc_start_angle,self.arc_stop_angle = start_angle,stop_angle
        self.maxDistfromBasket = ((self.arena_x-self.basket_x)**2+(self.arena_y-self.basket_y)**2)**0.5

class Ball:
    def __init__(self, b_x,b_y):
        self.b_x = b_x
        self.b_y = b_y
    def update(self,new_coords_x,new_coords_y):
        self.b_x = new_coords_x
        self.b_y = new_coords_y
    def getCoords(self):
        return self.b_x, self.b_y