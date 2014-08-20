from OpenGL.GL import *
import random,numpy,cmath,math,pygame

import ui,globals,drawing,os,copy
from globals.types import Point
import sys

class Mode(object):
    """ Base class to represent game modes """
    def __init__(self,parent):
        self.parent = parent
    
    def KeyDown(self,key):
        pass
    
    def KeyUp(self,key):
        pass

    def MouseButtonDown(self,pos,button):
        return False,False

    def Update(self):
        pass

class TitleStages(object):
    STARTED  = 0
    COMPLETE = 1
    TEXT     = 2
    SCROLL   = 3
    WAIT     = 4

class Titles(Mode):
    blurb = "CYBER PONG!!"
    def __init__(self,parent):
        self.parent          = parent
        self.start           = globals.time
        self.stage           = TitleStages.STARTED

        bl = Point(0,0)
        tr = bl + Point(1,0.7)
        self.blurb_text = ui.TextBox(parent = self.parent,
                                     bl     = bl         ,
                                     tr     = tr         ,
                                     text   = self.blurb ,
                                     textType = drawing.texture.TextTypes.SCREEN_RELATIVE,
                                     alignment = drawing.texture.TextAlignments.CENTRE,
                                     colour = (1,1,1,1),
                                     scale  = 4)

        self.play = ui.TextBoxButton(self.parent ,
                                     'Play'               ,
                                     Point(0.35,0.25),
                                     Point(0.45,0.30),
                                     size=3,
                                     callback = self.Play,
                                     line_width=1)
        self.quit = ui.TextBoxButton(self.parent,
                                     'Quit',
                                     Point(0.55,0.25),
                                     Point(0.65,0.30),
                                     size=3,
                                     callback = self.Quit,
                                     line_width=1)
        self.play.Enable()
        self.buttons = [self.play,self.quit]


    def KeyDown(self,key):
        self.stage = TitleStages.COMPLETE

    def Update(self):    
        pass
        #self.elapsed = globals.time - self.start
        #self.stage = self.handlers[self.stage](globals.time)

    def Delete(self):
        self.blurb_text.Delete()
        for button in self.buttons:
            button.Delete()

    def Play(self,t):
        self.Delete()
        self.parent.mode = GameMode(self.parent)
    
    def Quit(self,t):
        #Can make a gameover mode here for something more complicated...
        raise SystemExit('byeeee')

    def Startup(self,t):
        return TitleStages.STARTED

class GameMode(Mode):
    speed = 1
    direction_amounts = {pygame.K_LEFT  : Point(0, 0.02*speed),
                         pygame.K_RIGHT : Point(0, -0.02*speed),}

    class KeyFlags:
        LEFT  = 1
        RIGHT = 2
        UP    = 4
        DOWN  = 8

    keyflags = {pygame.K_LEFT  : KeyFlags.LEFT,
                pygame.K_RIGHT : KeyFlags.RIGHT,
                pygame.K_UP    : KeyFlags.UP,
                pygame.K_DOWN  : KeyFlags.DOWN}
    def __init__(self,parent):
        self.parent = parent
        self.parent.reset_board()
        self.keydownmap = 0
        
    def KeyDown(self,key):
        if key in self.direction_amounts:
            self.keydownmap |= self.keyflags[key]
            self.parent.player_paddle.velocity += self.direction_amounts[key]

    def KeyUp(self,key):
        if key in self.direction_amounts and (self.keydownmap & self.keyflags[key]):
            self.keydownmap &= (~self.keyflags[key])
            self.parent.player_paddle.velocity -= self.direction_amounts[key]
