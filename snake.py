import numpy as np
from random import randint
import time
from threading import Thread
from traits.api import Int, HasTraits, Array,Str, Instance, List, Tuple, \
Enum, Bool

from traitsui.key_bindings import KeyBinding, KeyBindings
from traitsui.tabular_adapter import TabularAdapter
from traitsui.api import View, Item, TabularEditor, Group

key_bindings = KeyBindings(
    KeyBinding( binding1    = 'Up',
                description = 'Up',
                method_name = 'up' ),
    KeyBinding( binding1    = 'Down',
                method_name = 'down' ),
    KeyBinding( binding1    = 'Left',
                method_name = 'left' ),
    KeyBinding( binding1    = 'Right',
                method_name = 'right' )
)

class TestArrayAdapter1(TabularAdapter):
    control = Instance(HasTraits)
    columns = List(Tuple)
    width = Int(25)
    
    def _columns_default(self):
        return [('Col{}'.format(i), i) for i in range(self.control.col)]
    
    def get_format(self, object, name, row, column):
        return ''

    def get_bg_color ( self, object, trait, row, column = 0):
        return ["white","black","red"][int(getattr(object,trait)[row][column])]

                 
class SnakeGame ( HasTraits ):
    row  = Int(25)
    col = Int(35)

    grid  = Array
    snake = List
    food_x = Int
    food_y = Int
    direction = Enum("dont_move", "up","down","left","right")
    direction_move = dict(dont_move=[np.nan,np.nan],up=[0,-1],down=[0,1],left=[-1,0], right=[1,0])
    is_snake_dead = Bool(False)

    score = Int(0)
    status = Str('Yay I am Alive')
    
    def _grid_default(self):
        grid = np.zeros((self.row,self.col))
        for i in range(0,4):
            grid[0][i]=1
        return grid
    
    def _snake_default(self):
        return [[0,0],[0,1],[0,2],[0,3]]
        
    def initialize(self):
        self.create_new_food()
        self.direction = "dont_move"
        t = Thread(target = self.thread_interrupt)
        t.daemon = True
        t.start()
        
    def create_new_food(self):
        self.food_x = randint(0,self.col-1)
        self.food_y = randint(0,self.row-1)
        self.grid[self.food_y][self.food_x]=2
        
    def check_snake_health(self, value_x, value_y):
        if [value_y,value_x] in self.snake or \
        value_x in [-1, self.col] or value_y in [-1,self.row]:
            self.status=' I am dead :( '
            self.is_snake_dead=True
        
    def move(self):
        if self.direction=='dont_move':
            return
            
        x,y = self.direction_move[self.direction]
        value_x = self.snake[-1][1]+x
        value_y = self.snake[-1][0]+y
        
        self.check_snake_health(value_x, value_y)
        if not self.is_snake_dead:
            self.grid[value_y][value_x]=1
            if [value_y,value_x] == [self.food_y,self.food_x]:
                self.create_new_food()
            else:
                self.grid[self.snake[0][0]][self.snake[0][1]]=0
                self.snake=self.snake[1:]
            self.snake.append([value_y,value_x])
            self.trait_property_changed('grid',self.grid, self.grid) 
            
    def _direction_changed(self, old, new):
        if (self.direction_move[old][0]==(-1)*self.direction_move[new][0] 
        or self.direction_move[old][1]==(-1)*self.direction_move[new][1]
        or self.is_snake_dead):
            print "Direction Changed Invalid Move",old,"to",new,"snake is dead",self.is_snake_dead
            self.trait_setq(direction = old)
        
        self.move()
            
    def right(self,event=None):
        self.direction = "right"
                        
    def left(self,event=None):
        self.direction = "left"
                    
    def down(self,event=None):
        self.direction = "down"
        
    def up(self,event=None):
        self.direction = "up"
                  
    def dont_move(self, event=None):
        pass
    
    def thread_interrupt(self):
        while not self.is_snake_dead:
            self.score = len(self.snake)-4
            time.sleep(0.3)
            self.move()
              
    def default_traits_view(self):
        view = View(Group(Item('status',style='readonly'),
                          Item('score',style='readonly')),
                          Item('grid',show_label=False,style='readonly',enabled_when='False', 
                         editor=TabularEditor(show_titles=False ,
                                              editable=False,
                                              operations=[],
                                              selectable=False, 
                                              horizontal_lines=False,
                                              vertical_lines =False,
                                              stretch_last_section = False,
                                              adapter=TestArrayAdapter1(control=self))),
                         key_bindings = key_bindings,scrollable=False, resizable = False, height=800, width=1200,
                         )
                         
        return view
                 
obj = SnakeGame()
obj.initialize()
obj.configure_traits()