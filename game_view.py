from OpenGL.GL import *
import random,numpy,cmath,math,pygame

import ui,globals,drawing,os,copy
from globals.types import Point
import modes
import random

class BoardObject(object):
    board_max = 0.98
    board_min = 0.02
    def Move(self):
        elapsed = globals.time - self.last_update
        self.last_update = globals.time
        distance = self.velocity*elapsed*0.03
        print self.velocity,distance
        if distance:
            distance = self.FinalDistance(distance)
            if not distance:
                return
            self.pos += distance
            self.quad.Move(distance)

class Paddle(BoardObject):
    def __init__(self,parent,pos):
        self.parent = parent
        self.size = parent.root.GetRelative(Point(10,30))
        self.velocity = Point(0,0)
        self.pos = pos
        self.last_update = globals.time

        bl = pos - self.size/2
        tr = bl + self.size
        self.quad = ui.Box(parent=self.parent,
                           pos=bl,
                           tr=tr,
                           colour=drawing.constants.colours.white,
                           buffer=globals.colour_tiles)

    
    def FinalDistance(self,distance):
        if distance.y > 0 and self.quad.top_right.y >= self.board_max:
            return 
        elif distance.y < 0 and self.quad.bottom_left.y <= self.board_min:
            return
        return distance
        
    def Update(self):
        self.Move()

class Ball(BoardObject):
    def __init__(self,parent):
        self.parent = parent
        self.size = parent.root.GetRelative(Point(4,3))
        self.pos = Point(random.random()*0.2+0.4,random.random())
        self.velocity = Point(0.5+random.random()*0.5,0.5+random.random()*0.5)*0.03
        self.last_update = globals.time
        bl = self.pos - self.size/2
        tr = bl + self.size
        self.quad = ui.Box(parent=self.parent,
                           pos=bl,
                           tr=tr,
                           colour=drawing.constants.colours.white,
                           buffer=globals.colour_tiles)

    def FinalDistance(self,distance):
        if self.quad.top_right.y > self.board_max:
            if distance.y > 0:
                self.velocity.y *= -1
        elif self.quad.bottom_left.y < self.board_min:
            if distance.y < 0:
                self.velocity.y *= -1
        if self.quad.top_right.x > self.board_max:
            if distance.x > 0:
                self.velocity.x *= -1
        elif self.quad.bottom_left.x < self.board_min:
            if distance.x < 0:
                self.velocity.x *= -1

        return distance

    def Update(self):
        self.Move()
                           
class Score(object):
    def __init__(self,parent,pos,score):
        self.score  = score
        self.parent = parent
        bl = pos-Point(0.03,0)
        tr = pos+Point(0.03,0.1)
        self.text   = ui.TextBox(parent = self.parent,
                                 bl     = bl         ,
                                 tr     = tr         ,
                                 text   = '%d' % self.score ,
                                 textType = drawing.texture.TextTypes.SCREEN_RELATIVE,
                                 alignment = drawing.texture.TextAlignments.CENTRE,
                                 colour = (1,1,1,1),
                                 scale  = 5)

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
        self.angle = 0
        self.rotate_speed = 0
        #self.mode = modes.LevelOne(self)
        self.last = globals.time
        self.objects = []
        self.StartMusic()
        
    def reset_board(self):
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
        self.ball = Ball(self.border)
        self.objects = [self.player_paddle,self.enemy_paddle,self.ball]
        self.player_score = Score(self,Point(0.45,0.85),0)
        self.enemy_score = Score(self,Point(0.55,0.85),0)
        self.net = ui.DottedLine(parent=self.border,
                                 pos=Point(0.49,-0.17),
                                 tr=Point(0.51,1.2),
                                 colour=drawing.constants.colours.white,
                                 buffer=globals.colour_tiles)
        self.angle = 0
        self.rotate_speed = 0.5

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
        elapsed = globals.time-self.last
        self.last = globals.time
        self.angle += (elapsed*self.rotate_speed/100.0)
        if self.mode:
            self.mode.Update()

        if self.game_over:
            return
        
        #frame_rate independent...
        for paddle in self.objects:
            paddle.Update()
            
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

