import pyglet, random
from pyglet.window import key

class Food():
    def __init__(self):
        self.image = pyglet.image.load('food.png')
        self.x = random.randrange(20, 480, 10)
        self.y = random.randrange(20, 480, 10)
        self.points = 10
    def new_place(self):
        self.x = random.randrange(20, 480, 10)
        self.y = random.randrange(20, 480, 10)
    def refresh(self):
        self.image.blit(self.x, self.y)

class SnakePart():
    def __init__(self, x, y):
        self.image = pyglet.image.load('square.png')
        self.x = x
        self.y = y
    def refresh(self):
        self.image.blit(self.x, self.y)
    def change_xy(self, next_point):
        self.x = next_point.x
        self.y = next_point.y

class Snake():
    def __init__(self):
        self.direction = None
        self.parts = []
        self.parts.append(SnakePart(initialX, initialY))
    def new_part(self):
        x = self.parts[len(self.parts) - 1].x
        y = self.parts[len(self.parts) - 1].y
        self.parts.append(SnakePart(x, y))
    def refresh(self):
        for part in self.parts:
            part.refresh()
    def eating(self, food):
        if self.parts[0].x == food.x and self.parts[0].y == food.y:
            return True
        return False
    def collision(self):
        for i, part in enumerate(self.parts):
            for ii in range(i + 1, len(self.parts)):
                if self.parts[ii].x == part.x and self.parts[ii].y == part.y:
                    return True
            if part.x == 10 or part.x == 480 or part.y == 10 or part.y == 480:
                return True
        return False
            
            
def update(t):
    global player, score, bg
    if player.collision():
        print("Has perdido!!!\nPuntaje total: {}".format(score))
        window.close()
    if player.eating(food):
        food.new_place()
        player.new_part()
        score += food.points
        food.points += 1
    for part in player.parts[::-1]:
        if player.parts.index(part):
            part.change_xy(player.parts[player.parts.index(part) - 1])
    if player.direction == 1:
        player.parts[0].x -= jump
    if player.direction == 2:
        player.parts[0].x += jump
    if player.direction == 3:
        player.parts[0].y += jump
    if player.direction == 4:
        player.parts[0].y -= jump
    window.clear()
    bg.blit(0, 0)
    player.refresh()
    food.refresh()
    
initialX = 40
initialY = 40
jump = 10
score = 0
bg = pyglet.image.load('camp.png')

food = Food()

player = Snake()

window = pyglet.window.Window(500, 500)

pyglet.clock.schedule_interval(update, 0.1)

@window.event
def on_draw():
    window.clear()
    bg.blit(0, 0)
    player.refresh()
    food.refresh()

@window.event
def on_key_press(symbol, modifier):
    global player
    if symbol == key.LEFT and player.direction != 2:
        player.direction = 1
    if symbol == key.RIGHT and player.direction != 1:
        player.direction = 2
    if symbol == key.UP and player.direction != 4:
        player.direction = 3
    if symbol == key.DOWN and player.direction != 3:
        player.direction = 4

pyglet.app.run()
