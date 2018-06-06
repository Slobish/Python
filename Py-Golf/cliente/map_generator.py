import tkinter
from tkinter import messagebox
from map_data import *
from math import cos, sin, radians

def info(title, text):
    messagebox.showinfo(title, text)

def error(title, text):
    messagebox.showerror(title, text)

def mouse_area(x, y, l):
    square = []
    for aux_y in range(y - l, y + l, 1):
        for aux_x in range(x - l, x + l, 1):
            square.append((aux_x, aux_y))
    return square

class color_window(tkinter.Frame):
    def __init__(self, parent, before):
        tkinter.Frame.__init__(self, parent)
        self.parent = parent
        self.before = before

        self.r = tkinter.DoubleVar()
        self.g = tkinter.DoubleVar()
        self.b = tkinter.DoubleVar()
        
        """ SUB -FRAMES """
        self.option_frame = tkinter.Frame(self)
        self.slider_frame = tkinter.Frame(self.option_frame)

        """ BUTTON """
        self.b_save = tkinter.Button(self.option_frame, text = "Aplicar", width = 10, height = 2, command = self.save)

        """ CANVAS """
        self.show = tkinter.Canvas(self, height = 200, width = 200)

        """ SLIDERS """
        self.s_red = tkinter.Scale(self.slider_frame, variable = self.r, length = 150, from_ = 255, to = 0, troughcolor = 'red', activebackground = 'black', command = self.update)
        self.s_green = tkinter.Scale(self.slider_frame, variable = self.b, length = 150, from_ = 255, to = 0, troughcolor = 'green', activebackground = 'black', command = self.update)
        self.s_blue = tkinter.Scale(self.slider_frame, variable = self.g, length = 150, from_ = 255, to = 0, troughcolor = 'blue', activebackground = 'black', command = self.update)

        """ ORG """
        self.s_red.grid(row = 0, column = 0, padx = 5)
        self.s_green.grid(row = 0, column = 1, padx = 5)
        self.s_blue.grid(row = 0, column = 2, padx = 5)

        self.slider_frame.pack()
        self.b_save.pack()
        self.option_frame.grid(row = 0, column = 0)
        
        self.show.grid(row = 0, column = 1, padx = 5, pady = 5)
        self.pack()

    def update(self, a):
        rojo = self.r.get()
        green = self.g.get()
        blue = self.b.get()
        self.color(rojo, green, blue)

    def color(self, rojo, green, blue):
        self.show["bg"] = '#%0.2x%0.2x%0.2x' % (rojo, blue, green)

    def save(self):
        rojo = int(self.r.get())
        green = int( self.g.get())
        blue = int(self.b.get())
        self.before.color = (rojo, blue, green)
        self.parent.withdraw()
    
class ladrillo():
    def __init__(self, x, y, parent, color):
        self.object = None
        self.parent = parent
        self.color = color
        self.x = x
        self.y = y
        self.ancho = None
        self.alto = None
        self.end_x = None
        self.end_y = None
        self.vertices = []
        self.area = []

    def update(self, x, y):
        self.end_x = x
        self.end_y = y
        self.vertices = [(self.x, self.y), (self.end_x - self.x, self.y), (self.x, self.end_y - self.y), (self.end_x, self.end_y)]
        self.parent.delete(self.object)
        color  = '#%0.2x%0.2x%0.2x' % self.color
        self.object = self.parent.create_polygon(self.x, self.y, self.x, self.end_y, self.end_x, self.end_y, self.end_x, self.y, fill = color)
        
    def get_area(self):
        self.area = []
        line = []
        for x in range(self.x, self.end_x, 1):
            line.append((x, self.y))
            
        for x in range(self.end_x, self.x, 1):
            line.append((x, self.y))
        
        for y in range(self.y, self.end_y, 1):
            for point in line:
                self.area.append((point[0], y))
        
        for y in range(self.end_y, self.y, 1):
            for point in line:
                self.area.append((point[0], y))

    def calculate(self):
        if self.end_x > 600:    self.end_x = 600
        elif self.end_x < 0:    self.end_x = 0
        if self.end_y > 300:    self.end_y = 300
        elif self.end_y < 0:    self.end_y = 0
        self.ancho = abs(self.end_x - self.x)
        self.alto = abs(self.end_y - self.y)
        if self.x < self.end_x and self.y > self.end_y:
            pass 
        elif self.x < self.end_x and self.y < self.end_y:
            self.y = self.end_y   
        elif self.x > self.end_x and self.y > self.end_y:
            self.x = self.end_x   
        else:
            self.x = self.end_x
            self.y = self.end_y
        self.y = 300 - self.y
        if self.x > 600:    self.x = 600
        elif self.x < 0:    self.x = 0
        if self.y > 300:    self.y = 300
        elif self.y < 0:    self.y = 0
            
class hoyo():
    def __init__(self, x, y, parent, color):
        self.object = None
        self.parent = parent
        self.color = color
        self.x = x
        self.y = y
        self.radio = None
        self.end_x = None
        self.end_y = None
        self.vertices = []
        self.area = []

    def update(self, x, y):
        self.end_x = x
        self.end_y = y
        self.vertices = [(self.x, self.y), (self.end_x, self.end_y)]
        self.parent.delete(self.object)
        color  = '#%0.2x%0.2x%0.2x' % self.color
        self.object = self.parent.create_oval(self.x, self.y, self.end_x, self.end_y, fill = color)
    
    def get_area(self):
        if self.x < self.end_x:
            if self.y < self.end_y:
                x_1 = self.x
                y_1 = self.y
            elif self.y > self.end_y:
                x_1 = self.x
                y_1 = self.end_y
        elif self.x > self.end_x:
            if self.y < self.end_y:
                x_1 = self.end_x
                y_1 = self.y
            elif self.y > self.end_y:
                x_1 = self.end_x
                y_1 = self.end_y
        self.radio = abs(self.x - self.end_x) // 2
        self.area = []
        for rad in range(self.radio, 1, -1):
            line = []
            for i in range(200):
                ang = radians( ( i / 200 ) * 360 )
                x = int(rad * cos(ang) + x_1 + rad)
                y = int(rad * sin(ang) + y_1 + rad)
                line.append((x, y))
            self.area += line

    def calculate(self):
        if self.x < self.end_x and self.y > self.end_y:
            pass 
        elif self.x < self.end_x and self.y < self.end_y:
            self.y = self.end_y   
        elif self.x > self.end_x and self.y > self.end_y:
            self.x = self.end_x   
        else:
            self.x = self.end_x
            self.y = self.end_y 
        self.y = 300 - self.y
        self.y += self.radio
        self.x += self.radio
        self.radio = int(self.radio)
        
class generator_window(tkinter.Frame):
    def __init__(self, parent, before=False):
        tkinter.Frame.__init__(self, parent, bg = 'gray23')
        
        self.parent = parent

        self.map_name = tkinter.StringVar()
        self.creator_name = tkinter.StringVar()

        self.ladrillos = []
        self.hoyos = []
        self.color = (0, 0, 0)
        
        self.using = None

        self.first = True
        self.origin = []

        """ SUB - FRAMES """
        self.button_frame = tkinter.Frame(self, bg = 'gray23')
        self.space_frame = tkinter.Frame(self, bg = 'gray23')
        self.gaps_frame = tkinter.Frame(self.space_frame, bg = 'gray23')

        """ BUTTONS """
        self.b_lad = tkinter.Button(self.button_frame, font = ("Helvetica", "15", "normal"), width = 8, height = 1, fg = 'DarkGoldenrod1', bg = 'gray10', text = "Ladrillo", command = self.ladrillo_on)
        self.b_hole = tkinter.Button(self.button_frame, font = ("Helvetica", "15", "normal"), width = 8, height = 1, fg = 'DarkGoldenrod1', bg = 'gray10', text = "Hoyo", command = self.hole_on)
        self.b_save = tkinter.Button(self.button_frame, font = ("Helvetica", "15", "normal"), width = 8, height = 1, fg = 'DarkGoldenrod1', bg = 'gray10', text = "Guardar", command = self.save_map)
        self.b_clear = tkinter.Button(self.button_frame, font = ("Helvetica", "15", "normal"), width = 8, height = 1, fg = 'DarkGoldenrod1', bg = 'gray10', text = "Borrar", command = self.clear_on)
        self.b_color = tkinter.Button(self.button_frame, font = ("Helvetica", "15", "normal"), width = 8, height = 1, fg = 'DarkGoldenrod1', bg = 'gray10', text = "Color", command = self.open_color)

        """ CANVAS """
        self.canvas = tkinter.Canvas(self.space_frame, height = 300, width = 600, bg = 'black')

        """ LABEL """
        self.title_label = tkinter.Label(self, text = "Creado de mapas", font = ("Arial", "10", "bold"))
        self.name_label = tkinter.Label(self.gaps_frame, bg = 'gray23', fg = 'OliveDrab1', text = "Nombre")
        self.creator_label = tkinter.Label(self.gaps_frame, bg = 'gray23', fg = 'OliveDrab1', text = "Creador")

        """ TEXT """
        self.name_text = tkinter.Entry(self.gaps_frame, textvariable = self.map_name, width = 15)
        self.creator_text = tkinter.Entry(self.gaps_frame, textvariable = self.creator_name, width = 15)
        
        self.canvas.bind("<Button-1>", self.mouse_press)
        self.canvas.bind("<B1-Motion>", self.mouse_on)
        self.canvas.bind("<ButtonRelease-1>", self.mouse_off)
        
        """ ORG """
        self.b_lad.pack()
        self.b_hole.pack()
        self.b_color.pack()
        self.b_clear.pack()
        self.b_save.pack()

        self.creator_label.grid(row = 0, column = 2, padx = 5)
        self.creator_text.grid(row = 0, column = 3, padx = 5)        
        
        self.name_label.grid(row = 0, column = 0, padx = 5)
        self.name_text.grid(row = 0, column = 1, padx = 5)

        self.gaps_frame.pack(pady = 5)
        self.canvas.pack(pady = 5)
        
        self.button_frame.grid(row = 0, column = 0, padx = 5)
        self.space_frame.grid(row = 0, column = 1, padx = 5)
        
        if not before:            
            self.pack()
            
    def open_color(self):
        self.win = tkinter.Toplevel()
        self.screen = color_window(self.win, self)
        self.screen.pack()
        
    def save_map(self):
        if "-" in self.map_name.get() or "*" in self.map_name.get():
            error("Map creator", "Uso de caracteres no permitidos!")
        else:
            if not map_db.create_map(self.map_name.get(), self.creator_name.get(), self.ladrillos, self.hoyos):
                error("Map creator", "El nombre asignado al mapa ya esta utilizado por otro mapa.")
        
    def ladrillo_on(self):
        self.using = 'ladrillo'
        self.b_lad["relief"] = tkinter.SUNKEN
        self.b_hole["relief"] = tkinter.RAISED
        self.b_clear["relief"] = tkinter.RAISED

    def hole_on(self):
        self.using = 'hoyo'
        self.b_lad["relief"] = tkinter.RAISED
        self.b_hole["relief"] = tkinter.SUNKEN
        self.b_clear["relief"] = tkinter.RAISED

    def clear_on(self):
        self.using = 'clear'
        self.b_clear["relief"] = tkinter.SUNKEN
        self.b_lad["relief"] = tkinter.RAISED
        self.b_hole["relief"] = tkinter.RAISED
        
    def mouse_press(self, event):
        if self.using == 'clear': 
            for lads in self.ladrillos:
                if (event.x, event.y) in lads.area:
                    self.canvas.delete(lads.object)
                    self.ladrillos.remove(lads)
            for h in self.hoyos:
                m_p = mouse_area(event.x, event.y, 2)
                for p in m_p:
                    if p in h.area:
                        self.canvas.delete(h.object)
                        self.hoyos.remove(h)
                        break
                    
    def mouse_on(self, event):
        if not self.using == 'clear':
            if self.first:
                if self.using == 'ladrillo':
                    self.ladrillos.append(ladrillo(event.x, event.y, self.canvas, self.color))
                elif self.using == 'hoyo':
                    self.hoyos.append(hoyo(event.x, event.y, self.canvas, self.color))
                self.first = False
            else:
                if self.using == 'ladrillo':
                    self.ladrillos[-1].update(event.x, event.y)
                elif self.using == 'hoyo':
                    self.hoyos[-1].update(event.x, event.y)
        
    def mouse_off(self, event):
        if not self.using == 'clear':
            if not self.first:
                if self.using == 'ladrillo':
                    self.ladrillos[-1].get_area()
                    self.ladrillos[-1].calculate()
                elif self.using == 'hoyo':
                    self.hoyos[-1].get_area()
                    self.hoyos[-1].calculate()
                self.first = True

if __name__ == '__main__':
    app = tkinter.Tk()
    app.title("Golf map creator v1.0")

    ventana = generator_window(app)

    app.mainloop()

