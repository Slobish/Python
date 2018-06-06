import tkinter
import golf
import importlib
import sys
import string
import threading
import socket
import os
from PIL import ImageTk, Image
from map_data import map_db
from map_generator import generator_window
from history_db import score_db
from tkinter import messagebox

def invitation(name, mapa, tries, creator):
    answer = messagebox.askyesno("Partida ONLINE", """Te han invitado a jugar.\n
    Partida: {}\n
    Mapa: {}\n
    Max.Intentos: {}\n
    Creador: {}""".format(name, mapa, tries, creator))
    return answer

class waiting_window(tkinter.Frame):
    def __init__(self, parent):
        tkinter.Frame.__init__(self, parent)
        
        parent.protocol("WM_DELETE_WINDOW", self.close)
                
        self.mensaje = tkinter.Label(self, text = "Esperando respuestas...", font = ("Arial", "10", "bold"))
        
        self.mensaje.pack()
        
        self.pack()
        
    def close(self):
        pass
    
class gameObject():
    def __init__(self):
        self.on = False
        self.path = None
        self.filename = None
        self.order = None
        self.cantidad = None
        self.before = None
        self.waiting = False
        self.v = False
    
    def run(self):
        if self.on:
            self.on = False
            importlib.reload(golf)
            self.Game = golf.main_game()
            self.Game.start_online(self.path, self.filename, self.order, self.cantidad, self.before)
        app.after(500, self.run)
    
    def wait(self):
        if self.waiting:
            if not self.v:
                self.s = tkinter.Toplevel()
                self.s.resizable(False, False)
                self.v = waiting_window(self.s)
                app.withdraw()
        else:
            if self.v:
                self.v = False
                self.s.destroy()
                app.state(tkinter.NORMAL)
        app.after(500, self.wait)

class online_game():
    def __init__(self, name, mapa, max_tries, creator):
        self.name = name
        self.map = mapa
        self.max = max_tries
        self.creator = creator

class client(threading.Thread):
    def __init__(self):
        self.sv_name = ""
        self.sv_ip = ""
        self.sv_port = 0       
        self.PIN = "PGLK1410"
        self.top10 = []
                
        self.playing = False
        self.invited = False
        self.online = False
        self.logged = False
        self.username = ""
        self.score = 0
        
        self.timer_chat = 0
        self.timer_userlist = 0
        
        self.current_game = None
        
        self.msj = ""
        self.game_info =""
        self.game_hit = ""
        
        self.flag_chatin = False
        self.flag_game_invite = False
        self.flag_game_hit = False
        self.flag_game_stop = False
        self.flag_top10 = False
        
    def run(self):
        while self.logged:
            try:
                data = self.socket.recv(512).decode().split('-')
                if data[0] == "GAME":
                    if data[1] == "REQUEST" and not self.playing and not self.invited:
                        answer = invitation( data[2], data[3], data[4], data[5] )
                        if answer:
                            self.current_game = online_game( data[2], data[3], data[4], data[5] )
                            self.invited = True
                            self.send_answer("OK")
                            partida.waiting = True
                        else:
                            self.send_answer("NO")
                    elif data[1] == "START" and not self.playing:
                        partida.waiting = False
                        self.playing = True
                        self.invited = False
                        
                        partida.path = os.path.join(map_db.directory, map_db.map_path, map_db.data_path)
                        partida.filename = map_db.map_filenames[self.current_game.map]
                        partida.order = data[2]
                        partida.cantidad = data[3]
                        partida.before = self
                        partida.on = True
                        
                    elif data[1] == "NADIE":
                        partida.waiting = False
                        error("Partida ONLINE", "Partida cancelada, nadie acepto")
                    elif data[1] == "PLAY" and self.playing:
                        partida.Game.your_turn()
                    elif data[1] == "PLAYER" and self.playing:
                        if len(data) == 5:
                            partida.Game.move_player(data[2], data[3], data[4])
                        else:
                            partida.Game.move_player(data[2], -float(data[4]), data[5])
                    elif data[1] == "END" and self.playing:
                        self.playing = False
                        self.invited = False
                        info("Partida ONLINE", "La partida ha terminado, ha ganado {}".format(data[2]))
                                                 
            except socket.timeout:
                if self.flag_chatin and not self.playing:
                    self.chat_in(self.msj)
                    self.msj = ""
                    self.flag_chatin = False
                elif self.flag_game_invite and not self.playing:
                    self.send_game( self.game_info )
                    self.flag_game_invite = False
                elif self.flag_game_hit and self.playing:
                    self.send_hit( self.game_hit )
                    self.flag_game_hit = False
                elif self.flag_game_stop and self.playing:
                    self.send_stop()
                    self.flag_game_stop = False
                elif self.flag_top10 and not self.playing:
                    self.request_top10()
                    self.flag_top10 = False
                elif not self.playing and self.logged and win.online.modo == "CHAT":
                    if self.timer_chat > 2:
                        win.chat.update_chatbox(self.chat_out())
                        self.timer_chat = 0
                    else:
                        self.timer_chat += 1
                    
                    if self.timer_userlist > 2:
                        win.chat.update_userlist(self.get_userlist())
                        self.timer_userlist = 0
                    else:
                        self.timer_userlist += 1
                    
                    
            except OSError:
                break
            
            except ConnectionResetError:
                break
    
    def request_top10(self):
        self.top10 = []
        self.socket.send("TOP10-".encode())
        
        while True:
            try:
                data = self.socket.recv(512).decode().split('-')
                if data[1] == "END":
                    break
                else:
                    self.top10.append( ( data[1], data[2], data[3 ]) )
                self.socket.send("TOP10-OK".encode())
            except:
                pass
    
    def download_map(self, mapa):
        map_header = []
        map_data = []
        self.socket.send("GAME-DOWNLOAD-{}".format(mapa).encode())
        while True:
            try:
                res = self.socket.recv(512).decode().split('-')
                if res[2] == "HEAD":
                    map_header = res[3:]
                elif res[2] == "DATA":
                    if res[3] == "END":
                        break
                    else:
                        map_data.append( res[3] )
                self.socket.send("GAME-DOWNLOAD-OK".encode())
            except:
                pass
        map_db.downloaded_map(map_header, map_data)
        info("Partida ONLINE", """Se ha descargado un nuevo mapa!\n
        Nombre: {}\n
        Creador: {}\n""".format(map_header[0], map_header[2]))     
    
    def send_win(self):
        self.playing = False
        self.invited = False
        self.score += 100
        self.socket.send("GAME-WIN".encode())
        
    def send_stop(self):
        self.socket.send("GAME-STOP".encode())
    
    def send_hit(self, msj):
        text = "GAME-HIT-{}-{}".format(msj[0], msj[1])
        self.socket.send(text.encode())
    
    def send_ready(self):
        self.socket.send("GAME-WAITING".encode())
    
    def send_game(self, msj):
        info = msj.split('-')
        self.current_game = online_game( info[0], info[1], info[2], self.username )
        if not map_db.check_haveit( self.current_game.map ):
            self.download_map( self.current_game.map )
        text = "GAME-INVITE-" + msj
        self.socket.send(text.encode())
        partida.waiting = True
        
    def send_answer(self, msj):
        if msj == "OK":
            if not map_db.check_haveit( self.current_game.map ):
                self.download_map( self.current_game.map )
        text = "GAME-ANSWER-{}".format(msj)            
        self.socket.send(text.encode())            
    
    def get_maplist(self):
        self.socket.send("MAPLIST-REQUEST".encode())
        try:
            data = self.socket.recv(512).decode().split('-')[1:]
        except:
            data = []
        return data

    def change_pw(self, old, new):
        self.socket.send("CHANGE-{}-{}".format(old, new).encode())
        res = self.socket.recv(512).decode().split('-')
        if res[1] == OK:
            return True
        return False
        
    def get_userlist(self):
        self.socket.send("USERS-".encode())
        try:
            data = self.socket.recv(512).decode().split('-')[1:]
            if data:
                lista = ""
                for u in data:
                    lista += "{}\n".format(u)
                return lista
        except:
            pass
        return False
        
    def disconnect(self):
        if self.online:
            if self.logged:
                self.log_out(self.username)
            try:
                self.socket.send("CLOSE-".encode())
            except:
                pass
            self.close()
        win.top.update()

    def chat_out(self):
        lista = []
        self.socket.settimeout(None)
        self.socket.send("CHATOUT-".encode())
        while True:
            try:
                data = self.socket.recv(512).decode().split('-')
                if data[1] == "END":
                    break
                else:
                    lista.append( (data[1], data[2]) )
                self.socket.send("CHATOUT-OK".encode())
            except socket.timeout:
                pass
        self.socket.settimeout(0.1)
        return lista
        
    def chat_in(self, mensaje):
        if self.online:
            self.socket.send("CHATIN-{}".format(mensaje).encode())
            data = self.socket.recv(512).decode().split('-')
            if data[1] == OK and data[0] == "CHATIN":
                return True
            return False 
        else:
            return False
            
    def log_out(self, usuario):
        if self.online:
            self.logged = False
            data = True
            while data:
                self.socket.send("LOGOUT-{}".format(usuario).encode())
                try:
                    data = self.socket.recv(512).decode() != "LOGOUT-OK"
                except:
                    data = True
                
    def log_in(self, usuario, clave):
        if self.online:
            self.socket.send("LOGIN-{}-{}".format(usuario, clave).encode())
            data = False
            while not data:
                try:
                    data = self.socket.recv(512).decode().split('-')
                except:
                    data = False
            if data[1] == OK and data[0] == 'LOGIN':
                self.username = usuario
                self.score = int(data[2])
                self.logged = True
                threading.Thread.__init__(self)
                self.start()
                return True
            return False
        else:
            return False
        
    def register(self, usuario, clave):
        if self.online:
            self.socket.send("REGISTER-{}-{}".format(usuario, clave).encode())
            data = False
            while not data:
                try:
                    data = self.socket.recv(512).decode().split('-')
                except:
                    data = False
            if data[1] == OK and data[0] == 'REGISTER':
                return True
            return False
        else:
            return False
    
    def open(self, ip, port):
        self.sv_ip = ip
        self.sv_port = port
        self.sv_address = (self.sv_ip, self.sv_port)
        self.socket = socket.socket()
        self.socket.settimeout(0.1)
        try:
            self.socket.connect( (self.sv_address) )
            if not self.wait_validation():
                self.close()
                win.top.update()
                return False
            self.online = True
            win.top.update()
            return True
        except ConnectionRefusedError:
            win.top.update()
            return False
    
    def close(self):
        self.online = False
        self.socket.close()
    
    def wait_validation(self):
        data = self.socket.recv(512).decode().split('-')
        if data[0] == 'VALIDATE':
            self.socket.send("VALIDATE-{}".format(self.PIN).encode())
            data = self.socket.recv(512).decode().split('-')
            if data[1] == OK:
                self.sv_name = data[2]
                return True
            else:
                return False
        else:
            return False
        
def info(title, text):
    messagebox.showinfo(title, text)

def error(title, text):
    messagebox.showerror(title, text)

class game_window(tkinter.Frame):
    def __init__(self, parent):
        tkinter.Frame.__init__(self, parent, bg = 'gray23')
        
        self.player_list = []
        self.map_list = []
        
        self.parent = parent
        self.maximo_intentos = tkinter.StringVar()
        self.game_name = tkinter.StringVar()
        
        """ SUB-FRAMES """
        self.gaps_frame = tkinter.Frame(self, bg = 'gray23')
        self.players_frame = tkinter.Frame(self.gaps_frame, bg = 'gray23')
        self.config_frame = tkinter.Frame(self.gaps_frame, bg = 'gray23')
        self.button_frame = tkinter.Frame(self, bg = 'gray23')
        
        """ LABELS """
        self.l_players = tkinter.Label(self.players_frame, fg = 'OliveDrab1', bg = 'gray23', text = "JUGADORES", font = ("Arial", "9", "bold"))
        self.l_map = tkinter.Label(self.config_frame, fg = 'OliveDrab1', bg = 'gray23', text = "Mapa", font = ("Arial", "9", "bold"))
        self.l_max = tkinter.Label(self.config_frame, fg = 'OliveDrab1', bg = 'gray23', text = "Maximos intentos", font = ("Arial", "9", "bold"))
        self.l_name = tkinter.Label(self.config_frame, fg = 'OliveDrab1', bg = 'gray23', text = "Nombre de partida", font = ("Arial", "9", "bold"))
        
        """ LISTBOX """
        self.players = tkinter.Listbox(self.players_frame, exportselection = 0, selectmode = tkinter.MULTIPLE, width = 22, height = 15)
        self.maps = tkinter.Listbox(self.config_frame, exportselection = 0, width = 17, height = 7)
        
        """ ENTRY """
        self.max = tkinter.Entry(self.config_frame, textvariable = self.maximo_intentos, width = 10)
        self.name = tkinter.Entry(self.config_frame, textvariable = self.game_name, width = 10)
        
        """ BUTTON """
        self.b_play = tkinter.Button(self.button_frame, text = "JUGAR", font = ("Helvetica", "12", "normal"), width = 10, height = 1, fg = 'yellow', bg = 'green', command = self.play)
        self.b_refresh = tkinter.Button(self.button_frame, text = "ACTUALIZAR", font = ("Helvetica", "12", "normal"), width = 10, height = 1, fg = 'yellow', bg = 'green', command = self.update)
                
        """ ORG """
        self.l_players.pack(pady = 5)
        self.players.pack(pady = 5)
        
        self.l_name.pack(pady = 2)
        self.name.pack(pady = 5)        
        self.l_max.pack(pady = 2)
        self.max.pack(pady = 5)
        self.l_map.pack(pady = 2)
        self.maps.pack(pady = 5)
        
        self.b_refresh.grid(row = 0, column = 0, padx = 10)
        self.b_play.grid(row = 0, column = 1, padx = 10)
        
        self.players_frame.grid(row = 0, column = 0, padx = 20)
        self.config_frame.grid(row = 0, column = 1, padx = 20)
        self.gaps_frame.pack(pady = 5)
        self.button_frame.pack(pady = 5)
        
    def update(self):
        self.update_players(user.get_userlist())
        
    def play(self):
        name = self.game_name.get()
        max_tries = self.maximo_intentos.get()
        players = self.players.curselection()
        mapa = self.maps.curselection()
        user.game_info = "{}-{}-{}".format(name, self.map_list[ mapa[0] ], max_tries)
        for p in players:
            user.game_info = user.game_info + '-' + self.player_list[ p ]
        user.flag_game_invite = True        
    
    def update_players(self, data):
        lista = data.split('\n')
        self.player_list = lista
        if lista:
            self.players.delete(0, self.players.size() - 1)
            for i, item in enumerate(lista):
                self.players.insert(i, item)    
    
    def update_maps(self, data):
        self.map_list = data
        lista = data
        old = self.maps.get(0, self.maps.size())
        if lista:
            for i, item in enumerate(lista):
                if item not in old:
                    self.maps.insert(i, item)
            if i < ( self.maps.size() - 1 ):
                self.maps.delete(i + 1, self.maps.size())
        
class session_window(tkinter.Frame):
    def __init__(self, parent):
        tkinter.Frame.__init__(self, parent, bg = 'gray23')

        self.parent = parent
        
        """ SUB - FRAMES """
        self.button_frame = tkinter.Frame(self, bg = 'gray23')
        self.chat_frame = tkinter.Frame(self, bg = 'gray23')
        self.message_frame = tkinter.Frame(self.chat_frame, bg = 'gray23')
        
        """ LABELS """
        self.title = tkinter.Label(self.button_frame, fg = 'OliveDrab1', bg = 'gray23', text = "Sala Previa", font = ("Arial", "15", "bold"))
        self.l_score = tkinter.Label(self.button_frame, fg = 'OliveDrab1', bg = 'gray23', font = ("Arial", "9", "normal") )
        self.l_users = tkinter.Label(self.button_frame, fg = 'green', bg = 'gray23', text = "Users Online", font = ("Arial", "9", "normal"))
                 
        """ TEXT """
        self.chatbox = tkinter.Text(self.chat_frame, width = 50, bg = 'black', fg = 'white', height = 20, state = tkinter.DISABLED, font = ("Arial", "9", "normal"))
        self.users = tkinter.Text(self.button_frame, width = 30, height = 13, state = tkinter.DISABLED, font = ("Arial", "9", "normal"))
        self.message = tkinter.Text(self.message_frame, width = 36, height = 2, font = ("Arial", "9", "normal"))
        
        """ BUTTONS """
        self.b_send = tkinter.Button(self.message_frame, text = "ENVIAR", font = ("Helvetica", "11", "normal"), width = 5, height = 2, fg = 'DarkGoldenrod1', bg = 'gray10', command = self.send_message)
        
        self.update_score()
        self.message.bind('<Return>', self.enter)
        
        """ ORG """
        self.message.grid(row = 0, column = 0, padx = 3)
        self.b_send.grid(row = 0, column = 1, padx = 3)
        self.chatbox.pack()
        self.message_frame.pack()
        
        self.title.pack()
        self.l_score.pack(pady = 20)
        self.l_users.pack()
        self.users.pack(pady = 5)
        
        self.button_frame.grid(row = 0, column = 0, padx = 20, pady = 5)
        self.chat_frame.grid(row = 0, column = 1, padx = 20, pady = 5)

    def enter(self, event):
        if user.logged:
            self.send_message()
        else:
            error("ONLINE", "Debes conectarte con una cuenta primero!")
            
    def update_userlist(self, lista):
        if lista:
            self.users["state"] = tkinter.NORMAL
            self.users.delete('1.0', tkinter.END)
            self.users.insert(tkinter.INSERT, lista)
            self.users["state"] = tkinter.DISABLED            
        
    def update_chatbox(self, data):
        for msj in data:
            self.chatbox["state"] = tkinter.NORMAL
            self.chatbox.insert(tkinter.INSERT, "{}: {}".format(msj[0], msj[1]))
            self.chatbox["state"] = tkinter.DISABLED
        
    def send_message(self):
        text = self.message.get('1.0', tkinter.END)
        self.message.delete('1.0', tkinter.END)
        if len(text) > 128:
            info("Mensaje muy largo. Maximo 128 caracteres")
        else:
            if not user.flag_chatin:
                user.flag_chatin = True
                user.msj = text
    
    def update_score(self):
        self.l_score["text"] = "Usuario: {}\nPuntos: {}".format(user.username, user.score)
        
    def open_game(self):
        self.win = tkinter.Toplevel()
        self.screen = game_window(self.win)

class server_window(tkinter.Frame):
    def __init__(self, parent):
        tkinter.Frame.__init__(self, parent, bg = 'gray23')
        
        self.parent = parent
        
        self.ip_number = tkinter.StringVar()
        self.port_number = tkinter.StringVar()
        
        """ SUB-FRAMES """
        self.info_frame = tkinter.Frame(self, bg = 'gray23')
        self.button_frame = tkinter.Frame(self.info_frame, bg = 'gray23')
        
        """ LABELS """
        self.title = tkinter.Label(self, bg = 'gray23', fg = 'OliveDrab1', text = "Acceso a servidor", font = ("Arial", "11" , "bold"))
        self.ip_text = tkinter.Label(self.button_frame, bg = 'gray23', fg = 'green', text = "Direccion IP", font = ("Arial", "10", "bold"))
        self.port_text = tkinter.Label(self.button_frame, bg = 'gray23', fg = 'green', text = "Puerto", font = ("Arial", "10", "bold"))
        
        """ ENTRIES """
        self.ip = tkinter.Entry(self.button_frame, textvariable = self.ip_number, width = 15)
        self.port = tkinter.Entry(self.button_frame, textvariable = self.port_number, width = 15)
        
        """ BUTTON """
        self.b_connect = tkinter.Button(self, text = "CONECTAR", font = ("Helvetica", "9", "normal"), width = 14, height = 1, fg = 'DarkGoldenrod1', bg = 'gray10', command = self.connect, relief = tkinter.RAISED)
        self.b_disconnect = tkinter.Button(self, text = "DESCONECTAR", font = ("Helvetica", "9", "normal"), width = 14, height = 1, fg = 'DarkGoldenrod1', bg = 'gray10', command = self.disconnect, relief = tkinter.SUNKEN)
        
        """ TEXT """
        self.info = tkinter.Text(self.info_frame, width = 15, height = 5, state = tkinter.DISABLED, font = ("Arial", "9", "normal"))
        self.update_info()
        
        """ ORG """
        self.title.pack(pady = 5)
        self.ip_text.pack()
        self.ip.pack(pady = 5)
        self.port_text.pack()
        self.port.pack(pady = 5)
        self.button_frame.grid(row = 0, column = 0, padx = 5)
        self.info.grid(row = 0, column = 1, padx = 5)
        self.info_frame.pack(pady = 5, padx = 5)
        self.b_connect.pack(pady = 5, padx = 5)
        self.b_disconnect.pack(pady = 5, padx = 5)
    
    def update_info(self, name='-', ip='-', port='-', status='-'):
        self.info["state"] = tkinter.NORMAL
        self.info.delete('1.0', tkinter.END)
        text = "Server: {}\nIp: {}\nPuerto: {}\nEstado: {}".format(name, ip, port, status)
        self.info.insert(tkinter.INSERT, text)
        self.info["state"] = tkinter.DISABLED
    
    def disconnect(self):
        if user.online:
            user.disconnect()
        self.b_connect["relief"] = tkinter.RAISED
        self.b_disconnect["relief"] = tkinter.SUNKEN
        self.update_info()
    
    def connect(self):
        if not user.online:
            ip = self.ip_number.get()
            port = int(self.port_number.get())              
            if user.open(ip, port):
                self.update_info(ip = ip, port = port, name = user.sv_name, status = "ONLINE")
                self.b_connect["relief"] = tkinter.SUNKEN
                self.b_disconnect["relief"] = tkinter.RAISED
            else:
                self.update_info(ip = ip, port = port, status = "OFFLINE")

class logged_window(tkinter.Frame):
    def __init__(self, parent):
        tkinter.Frame.__init__(self, parent, bg = 'gray23')
        
        self.parent = parent
        
        """ SUB-FRAMES """
        self.option_frame = tkinter.Frame(self, bg = 'gray23')
        self.change_frame = tkinter.Frame(self.option_frame, bg = 'gray23')
        self.button_frame = tkinter.Frame(self.option_frame, bg = 'gray23')
        
        """ LABELS """
        self.title = tkinter.Label(self, bg = 'gray23', fg = 'OliveDrab1', text = "Configuracion de cuenta", font = ("Arial", "15" , "bold"))
        self.sub_title = tkinter.Label(self.change_frame, bg = 'gray23', fg = 'green', text = "Cambiar clave", font = ("Arial", "10", "bold"))
        self.l_actual = tkinter.Label(self.change_frame, bg = 'gray23', fg = 'green', text = "Clave actual", font = ("Arial", "9", "normal"))
        self.l_new = tkinter.Label(self.change_frame, bg = 'gray23', fg = 'green', text = "Clave nueva", font = ("Arial", "9", "normal"))
        self.l_re = tkinter.Label(self.change_frame, bg = 'gray23', fg = 'green', text = "Confirmar clave", font = ("Arial", "9", "normal"))
        
        """ ENTRIES """
        self.actual_pw = tkinter.Entry(self.change_frame, width = 20, show = '*')
        self.nueva_pw = tkinter.Entry(self.change_frame, width = 20, show = '*')
        self.re_pw = tkinter.Entry(self.change_frame, width = 20, show = '*')
        
        """ BUTTONS """
        self.b_change = tkinter.Button(self.button_frame, text = "Cambiar", font = ("Helvetica", "10", "normal"), width = 10, height = 1, fg = 'yellow', bg = 'green', command = self.change)
        self.b_logout = tkinter.Button(self.button_frame, text = "Salir", font = ("Helvetica", "10", "normal"), width = 10, height = 1, fg = 'yellow', bg = 'green', command = self.log_out)
        
        """ ORG """
        self.title.pack(pady = 5)
        self.sub_title.pack(pady = 15)
        self.l_actual.pack(pady = 5)
        self.actual_pw.pack(pady = 5)
        self.l_new.pack(pady = 5)
        self.nueva_pw.pack(pady = 5)
        self.l_re.pack(pady = 5)
        self.re_pw.pack(pady = 5)
        self.b_change.pack(pady = 5)
        self.b_logout.pack(pady = 5)
        self.change_frame.grid(row = 0, column = 0, padx = 10)
        self.button_frame.grid(row = 0, column = 1, padx = 10)
        self.option_frame.pack(pady = 5)
    
    def change(self):
        old = self.actual_pw.get()
        new = self.nueva_pw.get()
        re = self.re_pw.get()
        if re != new:
            info("Configuracion", "Las claves no coinciden")
        else:
            if not user.change_pw(old, new):
                error("Configuracion", "Clave actual incorrecta")
            else:
                info("Configuracion", "Clave cambiada con exito!")
        
    def log_out(self):
        user.log_out(user.username)
        info("Configuracion", "Desconectado correctamente.")
        
        
class account_window(tkinter.Frame):
    def __init__(self, parent):
        tkinter.Frame.__init__(self, parent, bg = 'gray23')
        
        self.parent = parent
        
        self.log = enter_window(self)
        self.sign = register_window(self)
        
        self.log.grid(row = 0, column = 0, padx = 50)
        self.sign.grid(row = 0, column = 1, padx = 50)
        
class register_window(tkinter.Frame):
    def __init__(self, parent):
        tkinter.Frame.__init__(self, parent, bg = 'gray23')
        
        self.parent = parent
        
        self.username = tkinter.StringVar()
        self.password = tkinter.StringVar()
        self.re_password = tkinter.StringVar()
        
        """ LABELS """
        self.title = tkinter.Label(self, bg = 'gray23', fg = 'OliveDrab1', text = "Registrar una cuenta", font = ("Arial", "11", "bold"))
        self.user_text = tkinter.Label(self, bg = 'gray23', fg = 'green', text = "Username", font = ("Arial", "9", "normal"))
        self.pw_text = tkinter.Label(self, bg = 'gray23', fg = 'green', text = "Clave", font = ("Arial", "9", "normal"))
        self.re_pw_text = tkinter.Label(self, bg = 'gray23', fg = 'green', text = "Nuevamente clave", font = ("Arial", "9", "normal"))
        
        """ ENTRIES """
        self.user = tkinter.Entry(self, textvariable = self.username, width = 20)
        self.pw = tkinter.Entry(self, textvariable = self.password, width = 20, show = '*')
        self.re_pw = tkinter.Entry(self, textvariable = self.re_password, width = 20, show = '*')
        
        """ BUTTON """
        self.b_register = tkinter.Button(self, text = "REGISTRAR", font = ("Helvetica", "10", "normal"), width = 10, height = 1, fg = 'yellow', bg = 'green', command = self.register)
        
        """ ORG """
        self.title.pack(padx = 5, pady = 7)
        self.user_text.pack(padx = 5)
        self.user.pack(padx = 5, pady = 7)
        self.pw_text.pack(padx = 5)
        self.pw.pack(padx = 5, pady = 7)
        self.re_pw_text.pack(padx = 5)
        self.re_pw.pack(padx = 5, pady = 7)
        self.b_register.pack(padx = 5, pady = 11)
    
    def check_username(self, name):
        letter_exist = False
        number_exist = False
        for l in name:
            if not letter_exist and l in string.ascii_letters:
                letter_exist = True
            if not number_exist and l in string.digits:
                number_exist = True
            if letter_exist and number_exist:
                return True
        return False        

    def register(self):
        usuario = self.username.get()
        clave = self.password.get()
        re_clave = self.re_password.get()
        if len(clave) > 20 or len(usuario) > 20 or len(re_clave) > 20:
            info("Registro", "No se pueden superar los 20 caracteres")
        elif len(clave) < 4 or len(usuario) < 4 or len(re_clave) < 4:
            info("Registro", "Se requiere un minimo de 4 caracteres")
        else:
            if "-" in clave or "*" in clave:
                error("Registro", "Uso de caracteres no permitidos!")
            elif "-" in usuario or "*" in usuario:
                error("Registro", "Uso de caracteres no permitidos!")
            else:
                if not self.check_username(usuario):
                    info("Registro", "El usuario debe tener tanto numeros como letras")
                else:
                    if clave != re_clave:
                        error("Registro", "Las claves no coinciden")
                    else:
                        if user.register(usuario, clave):
                            info("Registro", "Registrado con exito!")
                        else:
                            error("Registro", "Esa cuenta ya existe o no se conecto al servidor.")

class enter_window(tkinter.Frame):
    def __init__(self, parent,):
        tkinter.Frame.__init__(self, parent, bg = 'gray23')
        
        self.parent = parent
        
        self.username = tkinter.StringVar()
        self.password = tkinter.StringVar()
        
        """ LABELS """
        self.title = tkinter.Label(self, bg = 'gray23', fg = 'OliveDrab1', text = "Conexion de cuenta", font = ("Arial", "11", "bold"))
        self.user_text = tkinter.Label(self, bg = 'gray23', fg = 'green', text = "Username", font = ("Arial", "9", "normal"))
        self.pw_text = tkinter.Label(self, bg = 'gray23', fg = 'green', text = "Clave", font = ("Arial", "9", "normal"))
        
        """ ENTRIES """
        self.user = tkinter.Entry(self, textvariable = self.username, width = 20)
        self.pw = tkinter.Entry(self, textvariable = self.password, width = 20, show = '*')
        
        """ BUTTON """
        self.b_enter = tkinter.Button(self, text = "ENTRAR", font = ("Helvetica", "10", "normal"), width = 10, height = 1, fg = 'yellow', bg = 'green', command = self.log)
        
        """ ORG """
        self.title.pack(padx = 5, pady = 7)
        self.user_text.pack(padx = 5)
        self.user.pack(padx = 5, pady = 7)
        self.pw_text.pack(padx = 5)
        self.pw.pack(padx = 5, pady = 7)
        self.b_enter.pack(padx = 5, pady = 11)
        
    def log(self):
        usuario = self.username.get()
        clave = self.password.get()
        if len(usuario) < 4 or len(clave) < 4:
            info("Ingreso", "Son requeridos al menos 4 caracteres")
        else:
            if user.log_in(usuario, clave):
                info("Ingreso", "Acceso permitido!")
            else:
                error("Ingreso", "Acceso denegado!")
                        
class online_window(tkinter.Frame):
    def __init__(self, parent, before):
        tkinter.Frame.__init__(self, parent, bg = 'gray23')
        
        self.parent = parent

        self.before = before

        self.modo = ""
        
        """ BUTTONS """
        self.b_game = tkinter.Button(self, text = "PARTIDA", font = ("Helvetica", "15", "normal"), width = 10, height = 1, fg = 'yellow3', bg = 'dark green', command = self.open_game)
        self.b_chat = tkinter.Button(self, text = "CHAT", font = ("Helvetica", "15", "normal"), width = 10, height = 1, fg = 'yellow3', bg = 'dark green', command = self.open_chat)
        self.b_score = tkinter.Button(self, text = "SCORE", font = ("Helvetica", "15", "normal"), width = 10, height = 1, fg = 'yellow3', bg = 'dark green', command = self.open_score)
        self.b_account = tkinter.Button(self, text = "CUENTA", font = ("Helvetica", "15", "normal"), width = 10, height = 1, fg = 'yellow3', bg = 'dark green', command = self.open_account)
        self.b_server = tkinter.Button(self, text = "SERVER", font = ("Helvetica", "15", "normal"), width = 10, height = 1, fg = 'yellow3', bg = 'dark green', command = self.open_server)
        
        self.b_game.pack(pady = 10)
        self.b_chat.pack(pady = 10)
        self.b_score.pack(pady = 10)
        self.b_account.pack(pady = 10)
        self.b_server.pack(pady = 10)

    def open_game(self):
        if not user.online:
            error("ONLINE", "Debes acceder a un servidor primero!")
        elif not user.logged:
            error("ONLINE", "Debes conectarte con una cuenta primero!")
        else:
            self.modo = "PARTIDA"
            self.before.update_onscreen()
        
    def open_chat(self):
        if not user.online:
            error("ONLINE", "Debes acceder a un servidor primero!")
        elif not user.logged:
            error("ONLINE", "Debes conectarte con una cuenta primero!")
        else:
            self.modo = "CHAT"
            self.before.update_onscreen()
        
    def open_score(self):
        if not user.online:
            error("ONLINE", "Debes acceder a un servidor primero!")
        elif not user.logged:
            error("ONLINE", "Debes conectarte con una cuenta primero!")
        else:
            self.modo = "SCORE"
            self.before.update_onscreen()
        
    def open_account(self):
        if not user.online:
            error("ONLINE", "Debes acceder a un servidor primero!")
        else:
            self.modo = "CUENTA"
            self.before.update_onscreen()
        
    def open_server(self):
        self.modo = "SERVER"
        self.before.update_onscreen()
        
class score_window(tkinter.Frame):
    def __init__(self, parent):
        tkinter.Frame.__init__(self, parent, bg = 'gray23')
        
        self.parent = parent
        
        """ SUB-FRAME """
        self.table_frame = tkinter.Frame(self, bg = 'gray23')
        
        """ LABELS """
        self.title = tkinter.Label(self, text = "Highscore", fg = 'OliveDrab1', bg = 'gray23', font = ("Arial", "13", "bold"))
        
        self.l_map = tkinter.Label(self.table_frame, text = "MAPA", fg = 'green', bg = 'gray23', font = ("Arial", "10", "bold"))
        self.l_name = tkinter.Label(self.table_frame, text = "NOMBRE", fg = 'green', bg = 'gray23', font = ("Arial", "10", "bold"))
        self.l_tries = tkinter.Label(self.table_frame, text = "INTENTOS", fg = 'green', bg = 'gray23', font = ("Arial", "10", "bold"))
        
        self.maps = [ tkinter.Label(self.table_frame, text = "", fg = 'green', bg = 'gray23', font = ("Arial", "10", "normal")) for i in range(10) ]
        self.names = [ tkinter.Label(self.table_frame, text = "", fg = 'green', bg = 'gray23', font = ("Arial", "10", "normal")) for i in range(10) ]
        self.tries = [ tkinter.Label(self.table_frame, text = "", fg = 'green', bg = 'gray23', font = ("Arial", "10", "normal")) for i in range(10) ]

        self.get_scores()
        
        """ ORG """
        
        self.l_map.grid(row = 0, column = 0, padx = 10)
        self.l_name.grid(row = 0, column = 1, padx = 10)
        self.l_tries.grid(row = 0, column = 2, padx = 10)
        
        for i, mapa in enumerate(self.maps):
            mapa.grid(row = i + 1, column = 0, padx = 10)
            
        for i, name in enumerate(self.names):
            name.grid(row = i + 1, column = 1, padx = 10)
            
        for i, trie in enumerate(self.tries):
            trie.grid(row = i + 1, column = 2, padx = 10)        
        
        self.title.pack(pady = 15)
        self.table_frame.pack(pady = 15)
    
    def get_scores(self):
        h_scores = score_db.highscore(map_db.map_list)
        
        for i, score in enumerate(h_scores):
            self.maps[i]["text"] = score[2]
            self.names[i]["text"] = score[1]
            self.tries[i]["text"] = score[3]        

class offline_window(tkinter.Frame):
    def __init__(self, parent, before):
        tkinter.Frame.__init__(self, parent, bg = 'gray23')
        
        self.before = before
        
        self.modo = ""

        """ BUTTONS """
        self.b_play = tkinter.Button(self, text = "PARTIDA", font = ("Helvetica", "15", "normal"), width = 10, height = 1, fg = 'yellow3', bg = 'dark green', command = self.open_play)
        self.b_score = tkinter.Button(self, text = "SCORE", font = ("Helvetica", "15", "normal"), width = 10, height = 1, fg = 'yellow3', bg = 'dark green', command = self.open_score)
        self.b_config = tkinter.Button(self, text = "OPCIONES", font = ("Helvetica", "15", "normal"), width = 10, height = 1, fg = 'yellow3', bg = 'dark green', command = self.open_config)
        self.b_creator = tkinter.Button(self, text = "CREADOR", font = ("Helvetica", "15", "normal"), width = 10, height = 1, fg = 'yellow3', bg = 'dark green', command = self.open_creator)
        
        """ ORG - BUTTONS """
        self.b_play.pack(pady = 10)
        self.b_score.pack(pady = 10)
        self.b_config.pack(pady = 10)
        self.b_creator.pack(pady = 10)
    
    def open_score(self):
        self.modo = "SCORE"
        self.before.update_offscreen()

    def open_creator(self):
        self.modo = "CREATOR"
        self.before.update_offscreen()

    def open_play(self):
        self.modo = "PARTIDA"
        self.before.update_offscreen()

    def open_config(self):
        self.modo = "CONFIG"
        self.before.update_offscreen()

class config_window(tkinter.Frame):
    def __init__(self, parent, before):
        tkinter.Frame.__init__(self, parent, bg = 'gray23')
        
        self.parent = parent
        self.before = before
        self.username = tkinter.StringVar()

        """ SUB-FRAMES """
        self.gaps = tkinter.Frame(self, bg = 'gray23')

        """ LABELS """
        self.config_title = tkinter.Label(self, text = "Menu de configuracion", fg = 'OliveDrab1', bg = 'gray23', font = ("Arial", "12", "bold"))
        self.name = tkinter.Label(self.gaps, text = "Username", fg = 'green', bg = 'gray23', font = ("Arial", "10"))

        """ ENTRIES """
        self.name_entry = tkinter.Entry(self.gaps, textvariable = self.username, width = 8)

        """ BUTTONS """
        self.b_save = tkinter.Button(self, font = ("Helvetica", "15", "normal"), width = 10, height = 1, fg = 'yellow', bg = 'green', text = "GUARDAR", command = self.save)

        """ ORGS """
        self.name.grid(row = 0, column = 0, padx = 5)
        self.name_entry.grid(row = 0, column = 1, padx = 5)
        self.config_title.pack(pady = 10)
        self.gaps.pack(pady = 10)
        self.b_save.pack(pady = 10)
    
    def save(self):
        global username
        username = self.username.get()
        self.before.top.update()
        
        
class play_offline(tkinter.Frame):
    def __init__(self, parent):
        tkinter.Frame.__init__(self, parent, bg = 'gray23')
        
        self.parent = parent
        
        self.history_text = ""
        self.intentos = 0

        """ SUB-FRAMES """
        self.frame_select = tkinter.Frame(self, bg = 'gray23')
        self.frame_info = tkinter.Frame(self, bg = 'gray23')

        """ TEXT LABELS """
        self.map_title = tkinter.Label(self.frame_select, fg = 'OliveDrab1', bg = 'gray23', text = "Mapas", font = ("Arial", "11", "bold"))
        self.selected_title = tkinter.Label(self.frame_info, fg = 'OliveDrab1', bg = 'gray23', text = "Historia", font = ("Arial", "11", "bold"))
        self.history = tkinter.Text(self.frame_info, width = 18, height = 5, font = ("Arial", "10", "normal"))

        """ LIST BOX """
        self.map_selector = tkinter.Listbox(self.frame_select, width = 26, height = 10)
        self.map_selector.bind('<<ListboxSelect>>', self.show_info)

        """ BUTTONS """
        self.b_play = tkinter.Button(self.frame_select, text = "Jugar", font = ("Helvetica", "15", "normal"), width = 10, height = 1, fg = 'yellow', bg = 'green', command = self.play_screen)
        self.b_update = tkinter.Button(self.frame_info, text = "Actualizar", font = ("Helvetica", "15", "normal"), width = 10, height = 1, fg = 'yellow', bg = 'green', command = self.update_maplist)

        """ ORG """
        self.map_title.pack(pady = 10)
        self.map_selector.pack(pady = 10)
        self.b_play.pack(pady = 15)
        self.b_update.pack(pady = 5)
        self.selected_title.pack(pady = 4)
        self.history.pack(pady = 5)
        self.frame_select.grid(row=0, column=0, padx = 20)
        self.frame_info.grid(row=0, column=1, padx = 20)
    
    def show_info(self, obj):
        global username
        try:
            selection = self.map_selector.selection_get()
            tries = score_db.get_tries(username, selection)
            if tries:
                self.update_history("Nombre: {}\nCreador: {}\nMejor jugada: {}\nUsuario: {}".format(selection, map_db.map_creator[selection][:-1], tries, username))
            else:
                self.update_history("Nombre: {}\nCreador: {}\nMejor jugada: {}\nUsuario: {}".format(selection, map_db.map_creator[selection][:-1], "-", username))                
        except:
            pass

    def update_history(self, text):
        self.history["state"] = tkinter.NORMAL
        self.history_text = text
        self.history.delete('1.0', tkinter.END)
        self.history.insert('1.0', self.history_text)
        self.history["state"] = tkinter.DISABLED

    def update_maplist(self):
        map_db.update_maplist()
        self.map_selector.delete(0, self.map_selector.size() - 1)
        for i, item in enumerate(map_db.map_list):
            self.map_selector.insert(i, item)
    
    def play_screen(self):
        selection = self.map_selector.selection_get()
        filename = map_db.map_filenames[selection]
        path = os.path.join(map_db.directory, map_db.map_path, map_db.data_path)
        importlib.reload(golf)
        game = golf.main_game()
        game.start_offline(path, filename, self)
        if self.intentos:
            p_tries = score_db.get_tries(username, selection)
            if p_tries:
                if p_tries > self.intentos:
                    score_db.update_tries(username, selection, self.intentos)
            else:
                score_db.set_tries(username, selection, self.intentos)

class highscore_window(tkinter.Frame):
    def __init__(self, parent):
        tkinter.Frame.__init__(self, parent, bg = 'gray23')
        
        """ SUB-FRAME """
        self.table_frame = tkinter.Frame(self, bg = 'gray23')
        
        """ LABELS """
        self.title = tkinter.Label(self, text = "Ranking TOP 10", fg = 'OliveDrab1', bg = 'gray23', font = ("Arial", "13", "bold"))
        self.l_pos = tkinter.Label(self.table_frame, text = "POSICION", fg = 'green', bg = 'gray23', font = ("Arial", "10", "bold"))
        self.l_name = tkinter.Label(self.table_frame, text = "NOMBRE", fg = 'green', bg = 'gray23', font = ("Arial", "10", "bold"))
        self.l_score = tkinter.Label(self.table_frame, text = "PUNTOS", fg = 'green', bg = 'gray23', font = ("Arial", "10", "bold"))
        
        self.positions = [ tkinter.Label(self.table_frame, fg = 'green', bg = 'gray23', font = ("Arial", "10", "normal")) for i in range(10) ]
        self.names = [ tkinter.Label(self.table_frame, fg = 'green', bg = 'gray23', font = ("Arial", "10", "normal")) for i in range(10) ]
        self.scores = [ tkinter.Label(self.table_frame, fg = 'green', bg = 'gray23', font = ("Arial", "10", "normal")) for i in range(10) ]
        
        """ ORG """
        self.l_pos.grid(row = 0, column = 0, padx = 15)
        self.l_name.grid(row = 0, column = 1, padx = 15)
        self.l_score.grid(row = 0, column = 2, padx = 15)
        
        for i, pos in enumerate(self.positions):
            pos.grid(row = i + 1, column = 0, padx = 10)
        
        for i, name in enumerate(self.names):
            name.grid(row = i + 1, column = 1, padx = 10)
        
        for i, score in enumerate(self.scores):
            score.grid(row = i + 1, column = 2, padx = 10)
        
        self.title.pack(pady = 20)
        self.table_frame.pack(pady = 20)
    
    def update(self):
        user.flag_top10 = True
        while( user.flag_top10 ):
            pass
        
        for i, u in enumerate( user.top10 ):
            self.positions[i]["text"] = u[0]
            self.names[i]["text"] = u[1]
            self.scores[i]["text"] = u[2]

class head(tkinter.Frame):
    def __init__(self, parent, before):
        tkinter.Frame.__init__(self, parent, height = 100, width = 920, bg = "black")
        
        self.before = before
        self.modo = "OFFLINE"
        
        """ SUB - FRAMES """
        self.button_frame = tkinter.Frame(self, bg = "black")
        self.text_frame = tkinter.Frame(self, bg = "black")
        
        """ LABELS """
        logo_img = ImageTk.PhotoImage(Image.open( "images/logo.jpg" )) 
        self.title = tkinter.Label(self, bg = "black", image = logo_img)
        self.title.image = logo_img
        self.label_user = tkinter.Label(self.text_frame, bg = "black", text = "", font = ("Arial", "9", "bold"))
        
        """ BUTTONS """
        self.b_mode = tkinter.Button(self.button_frame, text = "ONLINE", font = ("Arial", "12", "normal"), width = 9, height = 1, fg = 'snow', bg = 'navy', command = self.change_mode)
        self.b_info = tkinter.Button(self.button_frame, text = "INFO", font = ("Arial", "12", "normal"), width = 9, height = 1, fg = 'snow', bg = 'navy', command = self.open_info)
        
        self.update()
        
        """ ORG """
        self.label_user.pack()
        self.b_mode.pack(pady = 2)
        self.b_info.pack(pady = 2)
        self.text_frame.place(x = 10, y = 50, anchor = "w")
        self.title.place(x = 375, y = 50, anchor = "w")
        self.button_frame.place(x = 830, y = 50, anchor = "w")
        
        self.pack()
    
    def open_info(self):
        screen = tkinter.Toplevel()
        screen.resizable(False, False)
        info = info_window(screen)
        
    def change_mode(self):
        if self.modo == "OFFLINE":
            self.modo = "ONLINE"
            self.b_mode["text"] = "OFFLINE"
        else:
            self.modo = "OFFLINE"
            self.b_mode["text"] = "ONLINE"
            if user.online or user.logged:
                user.disconnect()
                info("ONLINE", "Desconectado del servidor")
                self.before.offline.modo = "PARTIDA"
                self.before.update_offscreen()
        self.before.update_menu()
        self.update()
    
    def update(self):
        global username
        if self.modo == "OFFLINE":
            self.label_user["fg"] = "SlateBlue2"
            self.label_user["text"] = "Usuario: {}".format(username)
        else:
            self.label_user["fg"] = "SlateBlue4"
            if user.online:
                self.label_user["text"] = "Conectado a {}".format(user.sv_name)
            else:
                self.label_user["text"] = "Desconectado de servidor"

class info_window(tkinter.Frame):
    
    def __init__(self, parent):
        tkinter.Frame.__init__(self, parent)
        
        self.view = tkinter.Text(self, height = 30, width = 95)
        
        self.read()
        
        self.view.pack()
        self.pack()
    
    def read(self):
        filename = "info.txt"
        file = open(filename)
        for line in file:
            self.view.insert(tkinter.INSERT, line)
        self.view.insert(tkinter.INSERT, "\n\nKAMMANN, Lucas")
            
        file.close()

class main_window_v2(tkinter.Frame):
    def __init__(self, parent):
        tkinter.Frame.__init__(self, parent, bg = "black")
        
        self.path = ""
        self.filename = ""
        self.order = 0
        self.cantidad = 0
        self.before = None
        
        """ SUB-FRAMES """
        self.top_frame = tkinter.Frame(self, bg = "black")
        self.bottom_frame = tkinter.Frame(self, bg = "black")
        self.menu_frame = tkinter.LabelFrame(self.bottom_frame, height = 370, width = 170, bg = 'gray23')
        self.screen_frame = tkinter.LabelFrame(self.bottom_frame, height = 370, width = 750, bg = 'gray23')
        
        self.top = head(self.top_frame, self)
        
        self.online = online_window(self.menu_frame, self)
        self.offline = offline_window(self.menu_frame, self)
        
        """ OFFLINE """
        self.partida_offline = play_offline(self.screen_frame)
        self.score_table = score_window(self.screen_frame)
        self.config = config_window(self.screen_frame, self)
        self.creator = generator_window(self.screen_frame, self)
        
        """ ONLINE """        
        self.partida_online = game_window(self.screen_frame)
        self.chat = session_window(self.screen_frame)
        self.top10 = highscore_window(self.screen_frame)
        self.server = server_window(self.screen_frame)
        self.account = account_window(self.screen_frame)
        
        self.offline.place(x = 23, y = 180, anchor = "w")
        
        self.menu_frame.grid(row = 0, column = 0, pady = 10)
        self.screen_frame.grid(row = 0, column = 1, pady = 10)
        self.top_frame.pack()
        self.bottom_frame.pack()
        
        self.pack()
    
    def update_onscreen(self):
        self.clean_screen()
        if self.online.modo == "PARTIDA":
            self.partida_online.place(x = 160, y = 170, anchor = "w")
            self.partida_online.update_players(user.get_userlist())
            data = user.get_maplist()
            self.partida_online.update_maps(data)
        elif self.online.modo == "CHAT":
            self.chat.update_score()
            self.chat.place(x = 35, y = 180, anchor = "w")
        elif self.online.modo == "SCORE":
            self.top10.update()
            self.top10.place(x = 160, y = 175, anchor = "w")
        elif self.online.modo == "SERVER":
            if not user.online:
                self.server.disconnect()
            self.server.place(x = 215, y = 165, anchor = "w")
        elif self.online.modo == "CUENTA":
            if not user.logged:
                self.account = account_window(self.screen_frame)
                self.account.place(x = 108, y = 180, anchor = "w")
            else:
                self.account = logged_window(self.screen_frame)
                self.account.place(x = 225, y = 180, anchor = "w")
    
    def update_offscreen(self):
        self.clean_screen()
        if self.offline.modo == "PARTIDA":
            self.partida_offline.place(x = 155, y = 180, anchor = "w")
        elif self.offline.modo == "SCORE":
            self.score_table.get_scores()
            self.score_table.place(x = 245, y = 180, anchor = "w")
        elif self.offline.modo == "CONFIG":
            self.config.place(x = 275, y = 180, anchor = "w")
        elif self.offline.modo == "CREATOR":
            self.creator.place(x = 0, y = 180, anchor = "w")

    def clean_screen(self):
        self.partida_offline.place_forget()
        self.score_table.place_forget()
        self.config.place_forget()
        self.creator.place_forget()        
        try:
            self.partida_online.place_forget()
        except:
            pass
        try:
            self.chat.place_forget()
        except:
            pass
        try:
            self.top10.place_forget()
        except:
            pass
        try:
            self.server.place_forget()
        except:
            pass
        try:
            self.account.place_forget()
        except:
            pass
        
    def update_menu(self):
        if self.top.modo == "ONLINE":
            self.offline.destroy()
            self.online = online_window(self.menu_frame, self)
            self.online.place(x = 23, y = 180, anchor = "w")
        else:
            self.online.destroy()
            self.offline = offline_window(self.menu_frame, self)
            self.offline.place(x = 23, y = 180, anchor = "w")



def close():
    user.disconnect()
    sys.exit()

OK = 'TRUE'
NOT_OK = 'FALSE'
username = "Player"
user = client()
partida = gameObject()

app = tkinter.Tk()
app.configure(background = "black")
app.geometry( "950x500" )
app.resizable(False, False)
app.title("PyGolf v2.0")

app.protocol("WM_DELETE_WINDOW", close)

win = main_window_v2(app)

app.after(500, partida.run)
app.after(500, partida.wait)

app.mainloop()