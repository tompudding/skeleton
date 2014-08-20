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
        distance = self.velocity*self.elapsed*0.03
        if distance:
            distance = self.FinalDistance(distance)
            if not distance:
                return
            self.pos += distance
            self.quad.Move(distance)

    def Update(self):
        self.elapsed = globals.time - self.last_update
        self.last_update = globals.time

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
        super(Paddle,self).Update()
        self.Move()

class EnemyPaddle(Paddle):
    min_speed = 0.005
    def Update(self):
        super(Paddle,self).Update()
        self.centre = self.quad.bottom_left + self.quad.size/2
        diff = globals.game_view.ball.centre.y - self.centre.y
        direction = 1 if diff > 0 else -1
        self.velocity = Point(0,(diff**1)*0.1)
        if abs(self.velocity.y) < self.min_speed:
            self.velocity.y = direction*self.min_speed
        print diff
        self.Move()

class Ball(BoardObject):
    ball_reset_time = 2000
    def __init__(self,parent):
        self.parent = parent
        self.size = parent.root.GetRelative(Point(4,3))
        self.SetRandomStart()
        self.last_update = globals.time
        self.in_paddle = False
        bl = self.pos - self.size/2
        tr = bl + self.size
        self.quad = ui.Box(parent=self.parent,
                           pos=bl,
                           tr=tr,
                           colour=drawing.constants.colours.white,
                           buffer=globals.colour_tiles)
        self.centre = self.quad.bottom_left + self.quad.size/2
        self.new_ball = None

    def FinalDistance(self,distance):
        self.centre = self.quad.bottom_left + self.quad.size/2

        if self.in_paddle:
            if not self.in_paddle.quad.ContainsRelative(self.centre):
                self.in_paddle = None

        for paddle in self.parent.parent.paddles:
            if not self.in_paddle and paddle.quad.ContainsRelative(self.centre):
                #We've colided with a paddle. make a note so we don't collide with it again until we're out
                self.in_paddle = paddle
                self.velocity.x *= -1
                #where in the paddle did we hit? We go out a bit at the edges
                #paddle_part = (paddle.quad.top_right.y-centre.y)/(paddle.quad.top_right.y-paddle.quad.bottom_left.y)
                #edginess = 2*(paddle_part**4)-0.5
                #self.velocity.y += (paddle.velocity.y*0.5)
                return

        if self.centre.y > self.board_max:
            if distance.y > 0:
                self.velocity.y *= -1
        elif self.centre.y < self.board_min:
            if distance.y < 0:
                self.velocity.y *= -1
        if self.centre.x > self.board_max:
            if distance.x > 0:
                globals.game_view.player_score.Increment()
                self.quad.Disable()
                self.new_ball = globals.time + self.ball_reset_time
        elif self.centre.x < self.board_min:
            if distance.x < 0:
                globals.game_view.enemy_score.Increment()
                self.quad.Disable()
                self.new_ball = globals.time + self.ball_reset_time

        return distance

    def SetRandomStart(self):
        self.pos = Point(random.random()*0.2+0.4,random.random())
        self.velocity = Point((0.5+random.random()*0.5),0.5+random.random()*0.5)*0.03

        if random.random() > 0.5:
            self.velocity.x *= -1
            self.pos.x += 0.3
        if random.random() > 0.5:
            self.velocity.y *= -1
            self.pos.x -= 0.3

    def Update(self):
        super(Ball,self).Update()
        if self.new_ball:
            if globals.time > self.new_ball:
                self.SetRandomStart()
                self.quad.SetPos(self.pos)
                self.quad.Enable()
                self.new_ball = None
                print 'a',self.velocity
        else:
            print 'b',self.velocity
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

    def Increment(self):
        self.score += 1
        self.text.SetText(text='%d' % self.score)
        self.parent.OnScoreUpdate()

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
        self.paddles = []
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
        self.enemy_paddle = EnemyPaddle(self.border,Point(0.95,0.5))
        self.ball = Ball(self.border)
        self.paddles = [self.player_paddle,self.enemy_paddle]
        self.objects = self.paddles + [self.ball]
        self.player_score = Score(self,Point(0.45,0.85),0)
        self.enemy_score = Score(self,Point(0.55,0.85),0)
        self.net = ui.DottedLine(parent=self.border,
                                 pos=Point(0.49,-0.17),
                                 tr=Point(0.51,1.2),
                                 colour=drawing.constants.colours.white,
                                 buffer=globals.colour_tiles)
        self.angle = 0
        self.rotate_speed = 0.5
        self.have_board = True
        self.OnScoreUpdate()

    def OnScoreUpdate(self):
        if self.player_score.score <= self.enemy_score.score:
            self.rotate_speed = 0.5
            return
        diff = self.player_score.score - self.enemy_score.score
        self.rotate_speed = diff**2

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

