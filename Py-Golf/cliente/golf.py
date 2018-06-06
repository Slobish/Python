import pyglet, os, sys
from pyglet.window import key
from math import sin, cos, radians, exp, sqrt, atan, degrees

colores = {
    "BLANCO":[255, 255, 255],
    "NEGRO":[0, 0, 0],
    "ROJO":[255, 0, 0],
    "VERDE":[0, 255, 0],
    "AMARILLO":[255, 255, 0],
    "AZUL":[0, 0, 255]}

COLORES = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255), (0, 255, 255), (120, 120, 0), (120, 0, 120), (0, 120, 120), (125, 125, 125)]

online_speed = 0.1
offline_speed = 1.2

MAX_ANGLE = 95
MIN_ANGLE = 85

MAX_LINE = 80
MAX_MOVEMENT = 3

mid_x = 20
mid_y = 140 

min_y = 5
max_y = 295
anchor_y = 5

min_x = 5
max_x = 595
anchor_x = 5
    
def reduce(area):
    for p in area:
        v = area.count(p)
        if v > 1:
            for i in range(v - 1):
                area.remove(p)
    return area

def ang_correction(ang):
    if ang > 180:
        ang -= 360
    elif ang < -180:
        ang += 360
    return ang

class ball():
    def __init__(self, color, mapa):
        self.color = color
        self.r = 10
        self.p_x = mid_x
        self.p_y = mid_y
        self.x = mid_x
        self.y = mid_y
        self.time = 0
        self.movement = False
        self.count = 0
        self.speed = 0
        self.ang = 0
        self.dist = 0
        self.vertex = []
        self.group = pyglet.graphics.Group()
        self.makeCircle(300, mapa)
        self.puntos = {}
        self.o_area = []
        self.area = []        
    
    def dif_angle(self, action, reaction):
        result = ( action[0] + reaction[0], action[1] + reaction[1] )
        if result[0] != 0:  
            result_ang = degrees( atan( result[1] / result[0] ) ) 
            if result[0] < 0 and result[1] > 0:
                result_ang = 180 + result_ang
            elif result[0] < 0 and result[1] < 0:
                result_ang = result_ang - 180
            elif result[1] == 0 and result[0] < 0:
                result_ang = 180
        else:   
            if result[1] < 0:   result_ang = -90    
            else:   result_ang = 90        
        return result_ang
    
    def check_bounce(self, game):
        result = self.check_collision(game)
        if result[0] and result[1] != "won":
            r_ang = result[1] + 90
            r_ang = ang_correction(r_ang)
            check = r_ang - self.ang
            check = ang_correction(check)
            if check > 90 or check < -90:
                vector_r = ( cos( radians(r_ang) ) * 2 * self.dist, sin( radians(r_ang) ) * 2 * self.dist)
                vector_a = ( cos( radians(self.ang) ) * self.dist, sin( radians(self.ang) ) * self.dist )
                self.ang = self.dif_angle(vector_a, vector_r)
            return False
        elif result[1] == "won":
            return True
    
    def collision_correction(self, coord):
        vector = ( coord[0] - self.x - self.r, coord[1] - self.y - self.r)
        if vector[0] != 0:
            angle = degrees( atan( vector[1] / vector[0] ) )
            if vector[1] == 0 and vector[0] < 0:
                angle = 180
            elif vector[0] < 0 and vector[1] > 0:
                angle += 180
            elif vector[1] < 0 and vector[0] < 0:
                angle -= 180
        else:
            if vector[1] > 0:
                angle = 90
            else:
                angle = -90
        return angle
    
    def check_collision(self, game):
        self.update_area()
        for p in self.area:
            ball_angle = self.collision_correction(p)
            for k in game.campo.lados.keys():
                if k != "corner":
                    obj_angle = int(k)
                else:
                    obj_angle = ball_angle + 90
                dif = int(abs(ball_angle - obj_angle))
                if dif > 180:   
                    dif = abs( dif - 360 )
                if  dif > MIN_ANGLE and dif < MAX_ANGLE:
                    for c in game.campo.lados[k]:
                        if abs( p[0] - c[0] ) < 2 and abs( p[1] - c[1] ) < 2:
                            return True, obj_angle
                    
            for c in game.campo.holes[0].area:
                if abs( p[0] - c[0] ) < 2 and abs( p[1] - c[1] ) < 2:
                    return True, "won"
                
        return False, None
    
    def update_area(self):
        self.area = []
        for p in self.o_area:
            self.area.append( ( self.x + self.r + p[0], self.y + self.r + p[1]) )
        
    def get_area(self):
        self.o_area = []
        for r in range(self.r, self.r + 1, 1):
            for i in range(500):
                angle = radians( i * 360 / 500 )
                x = int(r * cos(angle))
                y = int(r * sin(angle))
                self.o_area.append( (x, y) )
        self.o_area = reduce(self.o_area)
                
    def makeCircle(self, numPoints, mapa):
        for i in range(numPoints):
            angle = radians( float(i) / numPoints * 360 )
            x = self.r * cos(angle) + self.x + self.r
            y = self.r * sin(angle) + self.y + self.r
            verts = [self.x + self.r, self.y + self.r, x, y]
            color = (self.color + self.color)
            self.vertex.append(mapa.batch.add(2, pyglet.gl.GL_LINE_STRIP, self.group, ('v2f', verts), ('c3B', color)))

    def hit(self, speed, direction, game):
        self.movement = True
        self.time = 0
        if game.mode:
            self.speed = ( speed * online_speed ) / 100
        else:
            self.speed = ( speed * offline_speed ) / 100
        self.ang = direction
    
    def update(self, game):
        if self.movement:
            self.dist = self.friction()
            if self.dist < 0.3:
                self.stop(game)
            else:
                self.p_x = self.x
                self.p_y = self.y
                self.x += cos(radians(self.ang)) * self.dist
                self.y += sin(radians(self.ang)) * self.dist
                self.coordinates_change()
        else:
            self.current = 1000
    
    def stop(self, game):
        self.movement = False
        if not game.mode: 
            self.p_x = self.x
            self.p_y = self.y
            self.x = mid_x
            self.y = mid_y  
            game.line.on = True
            game.intentos += 1
        else:
            game.online_stop()
        self.coordinates_change()        
        
    def friction(self):
        self.time += 0.001
        return MAX_MOVEMENT * exp( -self.time * ( 1 / self.speed ) )
    
    def coordinates_change(self):
        y = self.y - self.p_y
        x = self.x - self.p_x
        for l in self.vertex:
            for i, value in enumerate(l.vertices):
                if not i % 2:   l.vertices[i] = value + x
                else:   l.vertices[i] = value + y

class mouse_follower():
    def __init__(self, user, mapa):
        self.on = True
        self.user = user
        self.mod = 0
        self.angle = 0
        self.vertex = mapa.batch.add(2, pyglet.gl.GL_LINE_STRIP, None, ('v2f', (self.user.x + self.user.r, self.user.y + self.user.r, self.user.x + self.user.r, self.user.y + self.user.r)), ('c3B', (colores["AMARILLO"] + colores["AMARILLO"])))
    
    def update(self, x, y):
        if x > self.user.x + self.user.r:
            self.mod = sqrt( (x - self.user.x + self.user.r - 20) ** 2 + (y - self.user.y + self.user.r - 20) ** 2 )
            if self.mod > MAX_LINE:    self.mod = MAX_LINE
            vector = (x - self.user.x + self.user.r - 20, y - self.user.y + self.user.r - 20)
            self.angle = atan( vector[1] / vector[0] )
        elif x < self.user.x + self.user.r:
            self.mod = sqrt( (x - self.user.x + self.user.r - 20) ** 2 + (y - self.user.y + self.user.r - 20) ** 2 )
            if self.mod > MAX_LINE:    self.mod = MAX_LINE
            vector = (x - self.user.x + self.user.r - 20, y - self.user.y + self.user.r - 20)
            self.angle = atan( vector[1] / vector[0] ) + radians(180)
            

    def animation(self):
        if self.on:
            x = cos( self.angle ) * self.mod
            y = sin( self.angle ) * self.mod
            self.vertex.vertices = (self.user.x + self.user.r, self.user.y + self.user.r, x + self.user.x + self.user.r, y + self.user.y + self.user.r)
        else:
            self.vertex.vertices = (0, 0, 0, 0)

class mapa():
    def __init__(self):
        self.name = ""
        self.path = ""
        self.filename = ""
        self.file = None
        self.ladrillos = []
        self.batch = pyglet.graphics.Batch()
        self.holes = []
        self.lados = {}
    
    def get_area(self):
        self.get_map_area()
        self.get_lads_area()
    
    def get_lads_area(self):
        for lad in self.ladrillos:
            lad.get_area()
            for k in lad.lados.keys():
                if k in self.lados.keys():
                    self.lados[k] += lad.lados[k]
                else:
                    self.lados[k] = lad.lados[k]
                    
    def get_map_area(self):
        self.lados["0"] = []
        self.lados["90"] = []
        self.lados["180"] = []
        self.lados["-90"] = []
        for x in range(0, 601, 1):
            self.lados["0"].append((x, 0))
            self.lados["180"].append((x, 300))
        for y in range(0, 301, 1):
            self.lados["-90"].append((0, y))
            self.lados["90"].append((600, y))
    
    def set_map(self, filename, path):
        self.ladrillos = []
        self.holes = []
        self.path = path
        self.filename = filename
        self.file = open(os.path.join(self.path, self.filename))
        for lines in self.file:
            buffer = lines.split('*')
            buffer[-1] = buffer[-1][:-1]
            if buffer[0] == "ladrillo":
                self.ladrillos.append(ladrillo(buffer[1], buffer[2], buffer[3], buffer[4], buffer[5], buffer[6], buffer[7], self))
            elif buffer[0] == "hoyo":
                self.holes.append(hole(buffer[1], buffer[2], buffer[3], buffer[4], buffer[5], buffer[6], self))
            else:
                self.name = buffer[0]
        self.file.close()
                
    def draw(self):
        self.batch.draw()
            
class hole():
    def __init__(self, x, y, rad, red, green, blue, mapa):
        self.color = [int(red), int(green), int(blue)]
        self.x = float(x)
        self.y = float(y)
        self.r = float(rad)
        self.vertex = []
        self.batch = pyglet.graphics.Batch()
        self.group = pyglet.graphics.Group()
        self.area = []
        self.makeCircle(300, self.r, self.color, mapa)
        self.makeCircle(300, self.r * 0.75, (0, 0, 0), mapa)
        self.get_area()
    
    def get_area(self):
        self.area = []
        for i in range(60):
            angle = i / 60 * 360
            x = self.r * 0.75 * cos(angle) + self.x
            y = self.r * 0.75 * sin(angle) + self.y
            self.area.append( (int(x), int(y)) )
        self.area = reduce(self.area)

    def makeCircle(self, numPoints, r, color, mapa):
        for i in range(numPoints):
            angle = radians(float(i)/numPoints * 360.0)
            x = r * cos(angle) + self.x
            y = r * sin(angle) + self.y
            verts = [self.x, self.y, x, y]
            self.vertex = mapa.batch.add(2, pyglet.gl.GL_LINE_STRIP, self.group, ('v2f', verts), ('c3B', (color + color)))

class ladrillo():
    def __init__(self, x, y, ancho, alto, red, green, blue, mapa):
        self.x = int(x)
        self.y = int(y)
        self.color = (int(red), int(green), int(blue))
        self.ancho = int(ancho)
        self.alto = int(alto)
        self.lados = {}
        self.group = pyglet.graphics.Group()
        self.vertex_list = mapa.batch.add(4, pyglet.gl.GL_POLYGON, self.group,
                                                    ('v2i', (self.x, self.y,
                                                             self.x, self.y + self.alto,
                                                             self.x + self.ancho, self.y + self.alto,
                                                             self.x + self.ancho, self.y)),
                                                    ('c3B', (self.color +
                                                             self.color +
                                                             self.color +
                                                             self.color)))

    def get_area(self):
        self.lados["0"] = []
        self.lados["90"] = []
        self.lados["-90"] = []
        self.lados["180"] = []
        self.lados["corner"] = []
        for x in range(self.x + 1, self.x + self.ancho - 1, 1):
            self.lados["180"].append((x, self.y))
        for x in range(self.x + 1, self.x + self.ancho - 1, 1):
            self.lados["0"].append((x, self.y + self.alto))
        for y in range(self.y + 1, self.y + self.alto - 1, 1):
            self.lados["90"].append( (self.x, y) )
        for y in range(self.y + 1, self.y + self.alto - 1, 1):
            self.lados["-90"].append( (self.x + self.ancho, y) )
            
        self.lados["corner"].append( (self.x, self.y) )                
        self.lados["corner"].append( (self.x + self.ancho, self.y) )
        self.lados["corner"].append( (self.x, self.y + self.alto) )
        self.lados["corner"].append( (self.x + self.ancho, self.y + self.alto) )

class main_game(pyglet.window.Window):
    def __init__(self):
        pyglet.window.Window.__init__(self, 600, 300)
        self.set_mouse_visible(False)
        self.campo = mapa()
    
    def start_online(self, path, filename, order, cantidad, before):
        
        self.mode = True
        self.before = before
        self.campo.set_map(filename, path)
        self.order = int(order)
        self.players = []
        self.campo.get_area()
        self.current = 1000
        self.intentos = 0
        
        for i in range(int(cantidad)):
            self.players.append( ball(COLORES[i], self.campo) )
            self.players[i].get_area()
            
        self.line = mouse_follower(self.players[int(order)], self.campo)
        self.line.on = False
        
        self.before.send_ready()
        
        self.label_tries = pyglet.text.Label("Intentos: ",
                          font_name='Arial',
                          font_size=12,
                          x=3, y=285, color = (255, 255, 0, 255))
        
        self.won_label = pyglet.text.Label("Has ganado!",
                          font_name='Arial',
                          font_size=20,
                          x=300, y=150, 
                          anchor_x = 'center', anchor_y = 'center',
                          color = (255, 255, 255, 255))
        
        self.lost_label = pyglet.text.Label("Has perdido!",
                          font_name='Arial',
                          font_size=20,
                          x=300, y=150, 
                          anchor_x = 'center', anchor_y = 'center',
                          color = (255, 255, 255, 255))
        
        pyglet.clock.schedule_interval(self.update_online, 0.0001)
        pyglet.app.run()
    
    def start_offline(self, path, filename, before):
        
        self.mode = False
        self.before = before
        self.before.intentos = False
        self.intentos = 1
        self.campo.set_map(filename, path)
        self.user = ball((200, 70, 0), self.campo)
        self.line = mouse_follower(self.user, self.campo)
        self.campo.get_area()
        self.user.get_area()
        
        self.label_tries = pyglet.text.Label("Intentos: ",
                          font_name='Arial',
                          font_size=12,
                          x=3, y=285, color = (255, 255, 0, 255))
        
        self.end_label = pyglet.text.Label("Has ganado",
                          font_name='Arial',
                          font_size=20,
                          x=300, y=150, 
                          anchor_x = 'center', anchor_y = 'center',
                          color = (255, 255, 255, 255))
        
        pyglet.clock.schedule_interval(self.update_offline, 0.001)
        pyglet.app.run()
    
    def online_stop(self):
        if self.current == self.order:
            self.before.flag_game_stop = True
        
    def move_player(self, order, ang, speed):
        self.current = int(order)
        self.players[int(order)].hit(float(speed), float(ang), self)
        
    def your_turn(self):
        self.line.on = True
        self.intentos += 1

    def end(self):
        if not self.mode:
            self.before.intentos = True
        pyglet.clock.schedule_once(self.on_close, 3)

    def update_online(self, t):
        self.line.animation()
        if self.before.playing:
            if self.current != 1000:
                if self.players[self.current].check_bounce(self):
                    self.before.send_win()
                    pyglet.clock.unschedule(self.update_online)
                    self.end()
                    self.won_label.draw()
                else:
                    self.players[self.current].update(self)
            self.clear()
            pyglet.gl.glColor3f(0, 0, 0)
            self.campo.draw()
            self.label_tries.text = "Intentos: " + str(self.intentos)
            self.label_tries.draw()
        else:
            pyglet.clock.unschedule(self.update_online)
            self.end()
            self.lost_label.draw()
    
    def update_offline(self, t):
        self.line.animation()
        if self.user.check_bounce(self):
            self.end()
            self.end_label.draw()
            pyglet.clock.unschedule(self.update_offline)
        else:
            self.user.update(self)
            self.clear()
            pyglet.gl.glColor3f(0, 0, 0)
            self.campo.draw()
            self.label_tries.text = "Intentos: " + str(self.intentos)
            self.label_tries.draw()
    
    def on_key_press(self, symbol, mod):
        if symbol == key.ESCAPE:
            if not self.mode:
                if self.user.movement:
                    self.user.stop(self)

    def on_draw(self):
        pass
    
    def on_close(self, t=None):
        if not self.mode and self.before.intentos:
            self.before.intentos = self.intentos
        if not self.mode:            
            pyglet.clock.unschedule(self.update_offline)
        pyglet.app.exit()
        self.close()
    
    def on_mouse_motion(self, x, y, dx, dy):
        if not self.mode:
            self.line.update(x, y)
        elif self.line.on:
            self.line.update(x, y)        
    
    def on_mouse_press(self, x, y, button, modifier):
        if not self.mode:
            if self.line.on:
                sp = ( self.line.mod / MAX_LINE ) * 100
                self.user.hit(sp, degrees(self.line.angle), self)
                self.line.on = False
        elif self.line.on:
            sp = ( self.line.mod / MAX_LINE ) * 100
            self.before.game_hit = (round(degrees(self.line.angle), 2), int(sp))
            self.before.flag_game_hit = True
            self.players[ self.order ].hit(sp, round(degrees(self.line.angle), 2), self)
            self.current = self.order
            self.line.on = False