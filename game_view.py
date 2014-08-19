from OpenGL.GL import *
import random,numpy,cmath,math,pygame

import ui,globals,drawing,os,copy
from globals.types import Point
import modes
import random

class Paddle(object):
    
    def __init__(self,parent,pos):
        self.parent = parent
        self.size = parent.root.GetRelative(Point(10,20))
        bl = pos - self.size/2
        tr = bl + self.size
        self.quad = ui.Box(parent=self.parent,
                           pos=bl,
                           tr=tr,
                           colour=drawing.constants.colours.white,
                           buffer=globals.colour_tiles)
                           

class GameView(ui.RootElement):
    def __init__(self):
        self.atlas = globals.atlas = drawing.texture.TextureAtlas('tiles_atlas_0.png','tiles_atlas.txt')
        self.game_over = False
        #pygame.mixer.music.load('music.ogg')
        #self.music_playing = False
        super(GameView,self).__init__(Point(0,0),globals.screen)
        self.grid = ui.Grid(self,Point(-1,-1),Point(2,2),Point(12,12))
        self.grid.Enable()
        self.mode = modes.Titles(self)
        #self.mode = modes.LevelOne(self)
        self.StartMusic()
        
        #self.border = drawing.QuadBorder(globals.colour_tiles,line_width = 1)
        w = 1/(math.sqrt(2))
        border_size = Point(w*globals.screen.y/globals.screen.x,w)
        bl = Point(0.5,0.5)-(border_size/2)
        tr = bl + border_size
        self.border = ui.Border(parent=self,
                                pos=bl,
                                tr=tr,
                                colour=drawing.constants.colours.white,
                                buffer=globals.colour_tiles)
                                
        self.player_paddle = Paddle(self.border,Point(0.05,0.5))
        self.enemy_paddle = Paddle(self.border,Point(0.95,0.5))
        self.angle = 0
    def StartMusic(self):
        pass
        #pygame.mixer.music.play(-1)
        #self.music_playing = True

    def Draw(self):
        drawing.ResetState()
        #drawing.Scale(self.zoom,self.zoom,1)
        
        drawing.Translate(globals.screen.x/2,globals.screen.y/2,0)
        drawing.Rotate(self.angle)
        drawing.Translate(-globals.screen.x/2,-globals.screen.y/2,0)
        drawing.LineWidth(2)
        drawing.DrawNoTexture(globals.line_buffer)
        drawing.DrawNoTexture(globals.colour_tiles)
        drawing.DrawAll(globals.nonstatic_text_buffer,globals.text_manager.atlas.texture.texture)
        
        #drawing.ResetState()
        #drawing.Translate(self.mouse_pos.x,self.mouse_pos.y,10)
        #drawing.DrawAll(globals.mouse_relative_buffer,globals.text_manager.atlas.texture.texture)
        #drawing.DrawNoTexture(globals.mouse_relative_tiles)

        #drawing.ResetState()
        #drawing.DrawNoTexture(globals.line_buffer)
        #drawing.DrawNoTexture(globals.colour_tiles)
        #drawing.DrawAll(globals.quad_buffer,self.atlas.texture.texture)
        #drawing.DrawAll(globals.nonstatic_text_buffer,globals.text_manager.atlas.texture.texture)
        
    def Update(self):
        self.angle = globals.time/100.
        if self.mode:
            self.mode.Update()

        if self.game_over:
            return
            
    def GameOver(self):
        self.game_over = True
        self.mode = modes.GameOver(self)
        
    def KeyDown(self,key):
        self.mode.KeyDown(key)

    def KeyUp(self,key):
        if key == pygame.K_DELETE:
            if self.music_playing:
                self.music_playing = False
                pygame.mixer.music.set_volume(0)
            else:
                self.music_playing = True
                pygame.mixer.music.set_volume(1)
        self.mode.KeyUp(key)

