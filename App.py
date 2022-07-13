import Config as cf

from kivy.config import Config
Config.set('graphics','resizable','0')
Config.set('graphics','height',cf.WIN_HEIGHT)
Config.set('graphics','width',cf.WIN_WIDTH)
global hours    #
global minutes  # Global variables for setting the timer
global seconds  #
hours = ''
minutes = '30'  # Default
seconds = ''

import os
from tinydb import TinyDB, Query, operations
from math import floor

from kivy.app import App

from kivy.uix.image import Image
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button

from kivy.uix.floatlayout import FloatLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.gridlayout import GridLayout

class Upper_Buttons(GridLayout): # Contains two main buttons, abort and shutdown buttons
    def __init__(self, **kwargs):
        super(GridLayout,self).__init__(**kwargs)
    
    def abort_shut(self):       # callback function for abort button
        os.system('cmd /c shutdown -a')

    def shut_timer(self):       # callback function for shutdown button
        db = TinyDB('db.json')
        User = Query()          # Uses TinyDB database to store 3 last timers

        global hours
        global minutes
        global seconds
        time = 0

        if(hours.text  !=''):
            time += int(hours.text)*3600
        if(minutes.text!=''):
            time += int(minutes.text)*60
        if(seconds.text!=''):
            time += int(seconds.text)
        
        lengt = len(db.search(User.id < 4))
        if len(db.search(User.time == time)) == 0:
            if lengt < 3:   # Adds new timer
                db.insert({'id':lengt+1,'time':time})
            else:           # Moves two last timers to 2 and 3 positions and sets timer on first position 
                            # (updates last timer)
                db.update(operations.set('id',4), User.id==1)
                db.update(operations.set('id',1), User.id==2)
                db.update(operations.set('id',2), User.id==3)
                db.update(operations.set('time',time), User.id==4)
                db.update(operations.set('id',3), User.id==4)

            
        os.system('cmd /c shutdown -s -t ' + str(time))

class H_Inp(TextInput): #Input for Hours
    def insert_text(self,substring,from_undo=False):
        s = substring

        t = False
        try:
            t = int(s)
            t = True
        except:
            t = False
        if not t:
            return super().insert_text('', from_undo=from_undo) # If input is char, return ''

        if len(self.text)<2:
            if int(self.text+s) < 25: # Hard cap for hours - 24
                return super().insert_text(s, from_undo=from_undo)
        return super().insert_text('', from_undo=from_undo)


class S_M_Inp(TextInput): #Input for Seconds and Minutes
    def insert_text(self,substring,from_undo=False):
        s = substring

        t = False
        try:
            t = int(s)
            t = True
        except:
            t = False
        if not t:
            return super().insert_text('', from_undo=from_undo) # If input is char, return ''

        if len(self.text)<2:
            if int(self.text+s) < 61: # Hard cap for seconds or minutes - 60
                return super().insert_text(s, from_undo=from_undo)
        return super().insert_text('', from_undo=from_undo)

class H_Box(GridLayout): # Grid with label and hours input
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        global hours
        hours = H_Inp()
        self.add_widget(hours)

class M_Box(GridLayout): # Grid with label and minutes input
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        global minutes
        minutes = S_M_Inp()
        self.add_widget(minutes)

class S_Box(GridLayout): # Grid with label and seconds input
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        global seconds
        seconds = S_M_Inp()
        self.add_widget(seconds)

class Time_Input(GridLayout): # Container for new timer input
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_widget(H_Box())
        self.add_widget(M_Box())
        self.add_widget(S_Box())

class Old_Input(GridLayout): # Container with last 3 timer inputs
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        db = TinyDB('db.json')
        User = Query()
        data = db.search(User.id < 4)
        print(data)
        self.time = []
        self.names = []
        for id in data:
            time = id['time']
            hour = floor(time/3600)
            minute = floor((time-hour*3600)/60)
            second = time - hour*3600 - minute*60
            name = str(hour) + 'h' + str(minute) + 'm ' + str(second) + 's'

            btn = Button(text=name)
            btn.bind(on_press=self.shut)

            self.add_widget(btn)

            self.time.append(time)
            self.names.append(name)
    def shut(self,instance):
        os.system('cmd /c shutdown -s -t ' + str(self.time[self.names.index(instance.text)]))



class Background(AnchorLayout): # Sets the background to png
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        bg = FloatLayout(size_hint = [1.1,1.1])
        bg.add_widget(Image(source=cf.BACKGROUND_IMG,keep_ratio=False,allow_stretch=True))
        self.add_widget(bg)


class SleeperApp(App):
    def build(self):
        self.icon = 'png/Shut_down.png'
        main_l = FloatLayout()
        main_l.add_widget(Background())
        main_l.add_widget(Upper_Buttons())
        main_l.add_widget(Time_Input())
        main_l.add_widget(Old_Input())
        return main_l

if __name__ == "__main__":
    SleeperApp().run()