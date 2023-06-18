"""
PyGraphica 1.0.0
by Luke Campbell

PyGraphica is a simple GUI and game library designed for Python. It works off the following classes:
    -   Window
    -   line
    -   rect
    -   text
    -   textbox
    -   image
And the following functions:
    -   touching
    -   to_front
    -   to_back

See the README file for more details and instructions   
"""


import sdl2
import sdl2.ext
import time
import ctypes
import os
from PIL import Image

class window:
    #Restart the window, used when the window is started or resized (as resize requires restart)
    def start(self):
        sdl2.ext.init()
        if self.resizable:
            self.__window = sdl2.ext.Window(self.name, (self.width, self.height), flags=sdl2.SDL_WINDOW_RESIZABLE, position=self.position)
        else:
            self.__window = sdl2.ext.Window(self.name, (self.width, self.height), position=self.position)
        if self.icon:
            sdl2.SDL_SetWindowIcon(
                self.__window.window,
                sdl2.ext.image.load_img(self.icon)
            )
        self.surface = self.__window.get_surface()
        self.__window.show()
    
    #Initialise window class
    def __init__(self, name="PyGraphica", size=(800,600), resizable=False, icon=False, position=(0,20), origin=0, colour=(0,0,0)):
        self.name = name
        self.width = size[0]
        self.height = size[1]
        self.resizable = resizable
        self.icon = icon
        self.position = position
        self.origin = origin
        self.colour = colour
        #Keys pressed
        self.keys = []
        self.comms = []
        self.key_changes = []
        self.comm_changes = []
        self.caps = False
        #Mouse details
        self.mouse_x = 0
        self.mouse_y = 0
        self.mouse_down = False
        self.mouse_held = False
        self.start()

    #Loop through events to check if window close button has been pressed
    def running(self):
        running = True
        events = sdl2.ext.get_events()
        for event in events:
            if event.type == sdl2.SDL_QUIT:
                running = False
                break
        return(running)
    
    #Update window
    def update(self):
        #Retrieve python-friendly data for mouse position
        x, y = ctypes.c_int(0), ctypes.c_int(0)
        buttonstate = sdl2.mouse.SDL_GetMouseState(ctypes.byref(x), ctypes.byref(y))
        x, y = x.value,y.value
        self.mouse_x = x
        self.mouse_y = y

        prev = self.mouse_down
        buttonstate = sdl2.ext.mouse.mouse_button_state()
        self.mouse_down = buttonstate.left
        
        #If mouse is down for two consecutive cycles it is 'held', this allows the library to only register each click once
        if prev and self.mouse_down:
            self.mouse_held = True
        else:
            self.mouse_held = False
    
        #Fill screen with background colour
        size = self.__window.size
        sdl2.ext.fill(self.surface,self.colour)
        self.position = self.__window.position

        #Check if window needs to be resized
        if size != (self.width, self.height):
            self.width = size[0]
            self.height = size[1]
            self.__window.show()
            self.start()
        
        #Blit all visible shapes to screen
        for shape in all_shapes:
            if shape.visible:
                shape.display()
        
        #Push changes to window
        self.__window.refresh()

        #Get key changes from function
        new_keys, new_comms = keys(self.caps)

        #Adjust lists accordingly
        self.key_changes = list(set(new_keys)-set(self.keys))
        self.keys = new_keys
        self.comm_changes = list(set(new_comms)-set(self.comms))
        self.comms = new_comms
        
        #Toggle 'caps' flag
        if "CAPS" in self.comm_changes:
            self.caps = not self.caps
    
    #When the window is closed (and the window deleted) clean up any images in the 'images' folder
    def __del__(self):
        for file in os.listdir("PyGraphica/images"):
            os.remove("PyGraphica/images/"+file)
        all_shapes = []
    
class line:
    def __init__(self,window,x1,y1,x2,y2,colour):
        self.__window = window
        #start coordinates = (x1,y1); end coordinates = (x2,y2)
        self.x1 = x1
        self.y1 = y1
        self.x2 =  x2
        self.y2 = y2
        self.colour = colour
        #Flag for whether line should be displayed or not
        self.visible = True
        #Add self to list of items to be displayed
        all_shapes.append(self)
    
    def display(self):
        #Adjust coordinates from user form to computer form
        start = make_pos(self.__window,(self.x1,self.y1))
        end = make_pos(self.__window,(self.x2,self.y2))
        #Display line
        sdl2.ext.line(self.__window.surface,self.colour,(start[0],start[1],end[0],end[1]))

class rect:
    def __init__(self,window,x1,y1,x2,y2,colour=False,border_colour=False,border_thickness=1):
        self.__window = window
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.colour = colour
        self.visible = True
        self.border_colour = border_colour
        self.border_thickness = border_thickness
        #Flags for hover and clicked are changed in update function
        self.hover = False
        self.clicked = False
        all_shapes.append(self)
    
    def display(self):
        start = make_pos(self.__window,(self.x1,self.y1))
        end = make_pos(self.__window,(self.x2,self.y2))

        #Get coordinates of hitbox in ascending order
        xmin,xmax = sorted((start[0],end[0]))
        ymin,ymax = sorted((start[1],end[1]))

        #If mouse in hitbox, object is being hovered over, otherwise it isn't
        if xmin < self.__window.mouse_x and self.__window.mouse_x < xmax and ymin < self.__window.mouse_y and self.__window.mouse_y < ymax:
            self.hover = True
        else:
            self.hover = False

        #If the rectangle is filled in, fill in the corresponding area
        if self.colour:
            w = end[0] - start[0]
            h = end[1] - start[1]
            if w < 0:
                x = end[0]
                w = w * -1
            else:
                x = start[0]
            if h < 0:
                y = end[1]
                h = h * -1
            else:
                y = start[1]
            sdl2.ext.draw.fill(self.__window.surface,self.colour,(x,y,w,h))
        
        #If rectangle has a border, create the four lines of the border
        if self.border_colour:
            sdl2.ext.line(self.__window.surface,self.border_colour,(start[0],start[1],start[0],end[1]),self.border_thickness)
            sdl2.ext.line(self.__window.surface,self.border_colour,(end[0],start[1],end[0],end[1]),self.border_thickness)
            sdl2.ext.line(self.__window.surface,self.border_colour,(start[0],start[1],end[0],start[1]),self.border_thickness)
            sdl2.ext.line(self.__window.surface,self.border_colour,(start[0],end[1],end[0],end[1]),self.border_thickness)

        #If the mouse is newly clicked, if the object is hovered on toggle clicked, otherwise it is not clicked
        if not self.__window.mouse_held and self.__window.mouse_down:
            if self.hover and not self.clicked:
                self.clicked = True
            else:
                self.clicked = False

class text:
    def __init__(self, window, x1, y1, size, colour, content, font = "PyGraphica/my_fonts/calibri.ttf"):
        self.__window = window
        self.x1 = x1
        self.y1 = y1
        self.size = size
        self.colour = colour
        self.font = font
        self.content = content
        self.visible = True
        self.height = 0
        self.width = 0
        self.hover = False
        self.clicked = False
        all_shapes.append(self)

        start = make_pos(self.__window,(self.x1,self.y1))
        size = make_height(self.__window,self.size)

        #Create font object
        font = sdl2.ext.ttf.FontTTF(self.font,str(str(size)+"px"),self.colour)

        #Render content in font
        textbox = font.render_text(self.content)

        #Make area where text will go
        rect = (start[0],start[1],start[0]+textbox.w,start[1]+textbox.h)
        self.width = textbox.w
        self.height = textbox.h

        #Make function to get the endpoint of the text based on the position of the origin and the size of the text, important for making textboxes later on
        if self.__window.origin == 0:
            self.__get_end = lambda obj:(obj.x1+obj.width,obj.y1+obj.height)
        elif self.__window.origin == 1:
            self.__get_end = lambda obj:(obj.x1-obj.width,obj.y1+obj.height)
        elif self.__window.origin in [2,4]:
            self.__get_end = lambda obj:(obj.x1+obj.width,obj.y1-obj.height)
        elif self.__window.origin == 3:
            self.__get_end = lambda obj:(obj.x1-obj.width,obj.y1-obj.height)
        
        #Use function to define endpoint of text
        end = self.__get_end(self)
        self.x2 = end[0]
        self.y2 = end[1]
    
    def display(self):
        #Get end in case things have changed
        end = self.__get_end(self)

        self.x2 = end[0]
        self.y2 = end[1]

        end = make_pos(self.__window,(self.x2,self.y2))
        start = make_pos(self.__window,(self.x1,self.y1))

        xmin,xmax = sorted((start[0],end[0]))
        ymin,ymax = sorted((start[1],end[1]))
        
        X = self.__window.mouse_x
        Y = self.__window.mouse_y
        if ymin < Y and Y < ymax and xmin < X and X < xmax:
            self.hover = True
        else:
            self.hover = False
        
        if not self.__window.mouse_held and self.__window.mouse_down:
            if self.hover and not self.clicked:
                self.clicked = True
            else:
                self.clicked = False

        #Recreate text in case anything has changed
        size = make_height(self.__window,self.size)
        font = sdl2.ext.ttf.FontTTF(self.font,str(str(size)+"px"),self.colour)
        textbox = font.render_text(self.content)
        rect = (start[0],start[1],start[0]+textbox.w,start[1]+textbox.h)
        self.width = textbox.w
        self.height = textbox.h
        sdl2.SDL_BlitSurface(textbox,None,self.__window.surface,sdl2.SDL_Rect(rect[0],rect[1],rect[2],rect[3]))

#Text input field, where users can type things and programmers can easily extract them
class textbox:
    def __init__(self,window,x1,y1,size,width=1,default_text="Type here..."):
        self.__window = window
        self.x1 = x1
        self.y1 = y1
        self.size = size
        self.width = width
        self.content = ""
        self.visible = True
        #Text that will be displayed as a prompt when the textbox is empty
        self.default_text = default_text

        #Text object component of textbox
        self.__text = text(self.__window,self.x1,self.y1,self.size,(0,0,0),"Type here...","OpenSans")
        #The textbox will have its own display function, so the text component must be removed from the list of objects to display
        all_shapes.remove(self.__text)

        #create function to calculate the width of the textbox to the start of the text
        if self.__window.origin in [1,3]:
            self.__add_width = lambda obj:obj.__text.x1-obj.width
        else:
            self.__add_width = lambda obj:obj.__text.x1+obj.width

        self.x2 = self.__text.x2
        self.y2 = self.__text.y2

        #Create box component of the textbox
        self.__box = rect(self.__window,self.x1,self.y1,self.x2,self.y2,(255,255,255),((0,0,0),1))
        all_shapes.remove(self.__box)

        all_shapes.append(self)
    
    def display(self):
        #Redefine position of textbox
        self.__text.x1 = self.x1
        self.__text.y1 = self.y1
        self.__box.x1 = self.x1
        self.__box.y1 = self.y1

        #If the text typed in to the textbox is larger than the defaul width of the textbox, stretch to fit it, otherwise use default width
        if self.width > self.__text.width:
            self.__box.x2 = self.__add_width(self)
            self.__box.y2 = self.__text.y2
        else:
            self.__box.x2 = self.__text.x2
            self.__box.y2 = self.__text.y2

        #Extra animations for if box is clicked
        if self.__box.clicked:
            self.__box.border_thickness = 2
            self.__box.border_colour = (255,0,0)
        elif self.__box.hover:
            self.__box.border_thickness = 1
            self.__box.border_colour = (255,0,0)
        else:
            self.__box.border_thickness = 1
            self.__box.border_colour = (0,0,0)

        #If user has not typed anything, display default text in grey, otherwise display user's text
        if self.content == "":
            self.__text.content = " " + self.default_text
            self.__text.colour = (100,100,100)
        else:
            self.__text.content = " " + self.content
            self.__text.colour = (0,0,0)

        #Add content to textbox
        if self.__box.clicked:
            add = self.__window.key_changes
            if "BACKSPACE" in self.__window.comm_changes and self.content != "":
                self.content = self.content[:-1]
            if len(add) > 0:
                self.content = self.content + add[0]

        self.__box.display()
        self.__text.display()

class image:
    def __init__(self,window,path,x1,y1,height=False,width=False):
        self.__window = window
        self.path = path
        self.x1 = x1
        self.y1 = y1
        self.height = height
        self.width = width
        #px width, as sometimes width/height will be in relative units
        self.__hard_width = 0
        self.__hard_height = 0
        self.visible = True

        img = Image.open(self.path)
        self.aspect_ratio = img.size[0]/img.size[1]
        start = make_pos(self.__window,(self.x1,self.y1))

        #If either width or height is undefined, define it using the other dimension and the aspect ratio of the image
        if self.width:
            width = make_width(self.__window,self.width)
        elif self.height:
            width = int(make_height(self.__window,height) * (self.aspect_ratio))
            if type(self.height) == str:
                self.width = rela_width(self.__window,width)
            else:
                self.width = width
        
        if self.height:
            height = make_height(self.__window,self.height)
        elif self.width:
            height = int(make_width(self.__window,self.width) * (1/self.aspect_ratio))
            if type(self.width) == str:
                self.height = rela_height(self.__window,height)
            else:
                self.height = height

        self.__hard_width = width
        self.__hard_height = height
        
        #resize the image and save it to the 'images' folder, then reload the saved image
        img = img.resize((width,height))
        img.save("PyGraphica/images/"+self.path.split("/")[-1])
        self.__img = sdl2.ext.load_image("PyGraphica/images/"+self.path.split("/")[-1])

        all_shapes.append(self)

        start_x = int(self.x1)
        start_y = int(self.y1)
        width = int(self.width)
        height = int(self.height)

        #Calculate the endpoint depending on the position of the origin
        if self.__window.origin in [0,2,4]:
            end_x = start_x + width
        else:
            end_x = start_x - width
            
        if self.__window.origin in [0,1]:
            end_y = start_y + height
        else:
            end_y = start_y - height

        #Define the endpoint in the format that the start was given in
        if type(self.width) == str:
            self.x2 = str(end_x)
            self.y2 = str(end_y)
        else:
            self.x2 = end_x
            self.y2 = end_y
    
    def display(self):
        width = make_width(self.__window,self.width)
        self.__hard_width = width
        height = make_height(self.__window,self.height)
        self.__hard_height = height

        start = make_pos(self.__window,(self.x1,self.y1))
        end = make_pos(self.__window,(self.x2,self.y2))

        resize = True

        #Check if any sizing has changed
        if self.__hard_width != self.__img.w and self.__hard_height != self.__img.h:
            pass
        elif self.__hard_width != self.__img.w:
            height = int(width * (1/self.aspect_ratio))
            if type(self.width) == str:
                self.height = rela_height(self.__window,height)
            else:
                self.height = height
        elif self.__hard_height != self.__img.h:
            width = int(height * self.aspect_ratio)
            if type(self.height) == str:
                self.width = rela_width(self.__window,width)
            else:
                self.width = width
        else:
            resize = False
        
        #If necessary, rewrite image (copy) into new size, then load resized image
        if resize:
            img = Image.open(self.path)
            img = img.resize((width,height))

            self.__hard_width = width
            self.__hard_height = height

            img.save("PyGraphica/images/"+self.path.split("/")[-1])

            self.__img = sdl2.ext.load_image("PyGraphica/images/"+self.path.split("/")[-1])

            start_x = int(self.x1)
            start_y = int(self.y1)
            width = int(self.width)
            height = int(self.height)

            if self.__window.origin in [0,2,4]:
                end_x = start_x + width
            else:
                end_x = start_x - width
                
            if self.__window.origin in [0,1]:
                end_y = start_y + height
            else:
                end_y = start_y - height

            if type(self.width) == str:
                self.end = (str(end_x),str(end_y))
            else:
                self.end = (end_x,end_y)
        
        #Display image
        sdl2.SDL_BlitSurface(self.__img,None,self.__window.surface,sdl2.SDL_Rect(start[0],start[1],end[0],end[1]))

#Check for overlap between two objects
def collision(object1, object2):
    overlap = True
    X1 = sorted([object1.x1,object1.x2])
    Y1 = sorted([object1.y1,object1.y2])
    X2 = sorted([object2.x1,object2.x2])
    Y2 = sorted([object2.y1,object2.y2])
    if X1[1] < X2[0] or X2[1] < X1[0]:
        overlap = False
    if Y1[1] < Y2[0] or Y2[1] < Y1[0]:
        overlap = False
    return(overlap)

#Move an object to the back of the displaying list (so it is in front of the screen)
def to_front(obj):
    all_shapes.remove(obj)
    all_shapes.append(obj)

#Move an object to the front of the displaying list (so it is at the back of the screen)
def to_back(obj):
    all_shapes.remove(obj)
    all_shapes.insert(0,obj)

#Delete an object
def delete(obj):
    try:
        all_shapes.remove(obj)
    except:
        pass

#ALL FUNCTIONS BELOW THIS POINT ARE NOT INTENDED TO BE USED OUTSIDE Of THE MODULE

#Turn static (px) or relative (%) coordinates in the user's origin system into static coordinates based on a top-left origin
def make_pos(window,pos):
    x,y = pos
    if type(x) == str:
        if window.origin in [0,2]:
            x = int(window.width * (float(x)) / 100)
        elif window.origin in [1,3]:
            x = int(window.width * ((100 - float(x)) / 100))
        elif window.origin == 4:
            x = int(window.width * ((50 + float(x)) / 100))
    else:
        if window.origin in [0,2]:
            pass
        elif window.origin in [1,3]:
            x = window.width - x
        elif window.origin == 4:
            x = window.width//2 + x
    
    if type(y) == str:
        if window.origin in [0,1]:
            y = int(window.height * (float(y)) / 100)
        elif window.origin in [2,3]:
            y = int(window.height * ((100 - float(y)) / 100))
        elif window.origin == 4:
            y = int(window.height * ((50 - float(y)) / 100))
    else:
        if window.origin in [0,1]:
            pass
        elif window.origin in [2,3]:
            y = window.height - y
        elif window.origin == 4:
            y = window.height//2 - y
    
    return((x,y))

#Turn static or relative width into static width
def make_height(window,height):
    if type(height) == str:
        height = int(window.height * (float(height) / 100))
    return(height)

#Turn static or relative height into static height
def make_width(window,width):
    if type(width) == str:
        width = int(window.width * (float(width) / 100))
    return(width)

#Turn static or relative width into relative width
rela_width = lambda window,width:str(int(100*(width/window.width)))

#Turn static of relative height into relative height
rela_height = lambda window,height:str(int(100*(height/window.height)))

#List of shapes to be displayed
all_shapes = []

#Loop through all key_status' and add corresponding key to a list (for easier, more python suitable access)
def keys(caps):
    keys = []
    keystatus = sdl2.SDL_GetKeyboardState(None)
    if keystatus[sdl2.SDL_SCANCODE_1]:
        keys.append("1")
    if keystatus[sdl2.SDL_SCANCODE_2]:
        keys.append("2")
    if keystatus[sdl2.SDL_SCANCODE_3]:
        keys.append("3")
    if keystatus[sdl2.SDL_SCANCODE_4]:
        keys.append("4")
    if keystatus[sdl2.SDL_SCANCODE_5]:
        keys.append("5")
    if keystatus[sdl2.SDL_SCANCODE_6]:
        keys.append("6")
    if keystatus[sdl2.SDL_SCANCODE_7]:
        keys.append("7")
    if keystatus[sdl2.SDL_SCANCODE_8]:
        keys.append("8")
    if keystatus[sdl2.SDL_SCANCODE_9]:
        keys.append("9")
    if keystatus[sdl2.SDL_SCANCODE_0]:
        keys.append("0")
    if keystatus[sdl2.SDL_SCANCODE_A]:
        keys.append("a")
    if keystatus[sdl2.SDL_SCANCODE_B]:
        keys.append("b")
    if keystatus[sdl2.SDL_SCANCODE_C]:
        keys.append("c")
    if keystatus[sdl2.SDL_SCANCODE_D]:
        keys.append("d")
    if keystatus[sdl2.SDL_SCANCODE_E]:
        keys.append("e")
    if keystatus[sdl2.SDL_SCANCODE_F]:
        keys.append("f")
    if keystatus[sdl2.SDL_SCANCODE_G]:
        keys.append("g")
    if keystatus[sdl2.SDL_SCANCODE_H]:
        keys.append("h")
    if keystatus[sdl2.SDL_SCANCODE_I]:
        keys.append("i")
    if keystatus[sdl2.SDL_SCANCODE_J]:
        keys.append("j")
    if keystatus[sdl2.SDL_SCANCODE_K]:
        keys.append("k")
    if keystatus[sdl2.SDL_SCANCODE_L]:
        keys.append("l")
    if keystatus[sdl2.SDL_SCANCODE_M]:
        keys.append("m")
    if keystatus[sdl2.SDL_SCANCODE_N]:
        keys.append("n")
    if keystatus[sdl2.SDL_SCANCODE_O]:
        keys.append("o")
    if keystatus[sdl2.SDL_SCANCODE_P]:
        keys.append("p")
    if keystatus[sdl2.SDL_SCANCODE_Q]:
        keys.append("q")
    if keystatus[sdl2.SDL_SCANCODE_R]:
        keys.append("r")
    if keystatus[sdl2.SDL_SCANCODE_S]:
        keys.append("s")
    if keystatus[sdl2.SDL_SCANCODE_T]:
        keys.append("t")
    if keystatus[sdl2.SDL_SCANCODE_U]:
        keys.append("u")
    if keystatus[sdl2.SDL_SCANCODE_V]:
        keys.append("v")
    if keystatus[sdl2.SDL_SCANCODE_W]:
        keys.append("w")
    if keystatus[sdl2.SDL_SCANCODE_X]:
        keys.append("x")
    if keystatus[sdl2.SDL_SCANCODE_Y]:
        keys.append("y")
    if keystatus[sdl2.SDL_SCANCODE_Z]:
        keys.append("z")
    if keystatus[sdl2.SDL_SCANCODE_GRAVE]:
        keys.append("`")
    if keystatus[sdl2.SDL_SCANCODE_MINUS]:
        keys.append("-")
    if keystatus[sdl2.SDL_SCANCODE_SEMICOLON]:
        keys.append(";")
    if keystatus[sdl2.SDL_SCANCODE_APOSTROPHE]:
        keys.append("'")
    if keystatus[sdl2.SDL_SCANCODE_SLASH]:
        keys.append("/")
    if keystatus[sdl2.SDL_SCANCODE_COMMA]:
        keys.append(",")
    if keystatus[sdl2.SDL_SCANCODE_PERIOD]:
        keys.append(".")
    if keystatus[sdl2.SDL_SCANCODE_SLASH]:
        keys.append("?")
    if keystatus[sdl2.SDL_SCANCODE_KP_LEFTBRACE]:
        keys.append("[")
    if keystatus[sdl2.SDL_SCANCODE_KP_RIGHTBRACE]:
        keys.append("]")
    if keystatus[sdl2.SDL_SCANCODE_BACKSLASH]:
        keys.append("\\")
    if keystatus[sdl2.SDL_SCANCODE_SPACE]:
        keys.append(" ")

    #Same for command keys
    comms = []
    if keystatus[sdl2.SDL_SCANCODE_CAPSLOCK]:
        comms.append("CAPS")
    if keystatus[sdl2.SDL_SCANCODE_KP_ENTER]:
        comms.append("ENTER")
    if keystatus[sdl2.SDL_SCANCODE_LSHIFT] or keystatus[sdl2.SDL_SCANCODE_RSHIFT]:
        comms.append("SHIFT")
    if keystatus[sdl2.SDL_SCANCODE_LCTRL] or keystatus[sdl2.SDL_SCANCODE_RCTRL]:
        comms.append("CTRL")
    if keystatus[sdl2.SDL_SCANCODE_ESCAPE]:
        comms.append("ESCAPE")
    if keystatus[sdl2.SDL_SCANCODE_F1]:
        comms.append("F1")
    if keystatus[sdl2.SDL_SCANCODE_F2]:
        comms.append("F2")
    if keystatus[sdl2.SDL_SCANCODE_F3]:
        comms.append("F3")
    if keystatus[sdl2.SDL_SCANCODE_F4]:
        comms.append("F4")
    if keystatus[sdl2.SDL_SCANCODE_F5]:
        comms.append("F5")
    if keystatus[sdl2.SDL_SCANCODE_F6]:
        comms.append("F6")
    if keystatus[sdl2.SDL_SCANCODE_F7]:
        comms.append("F7")
    if keystatus[sdl2.SDL_SCANCODE_F8]:
        comms.append("F8")
    if keystatus[sdl2.SDL_SCANCODE_F9]:
        comms.append("F9")
    if keystatus[sdl2.SDL_SCANCODE_F10]:
        comms.append("F10")
    if keystatus[sdl2.SDL_SCANCODE_F11]:
        comms.append("F11")
    if keystatus[sdl2.SDL_SCANCODE_F12]:
        comms.append("F12")
    if keystatus[sdl2.SDL_SCANCODE_F13]:
        comms.append("F13")
    if keystatus[sdl2.SDL_SCANCODE_F14]:
        comms.append("F14")
    if keystatus[sdl2.SDL_SCANCODE_F15]:
        comms.append("F15")
    if keystatus[sdl2.SDL_SCANCODE_F16]:
        comms.append("F16")
    if keystatus[sdl2.SDL_SCANCODE_F17]:
        comms.append("F17")
    if keystatus[sdl2.SDL_SCANCODE_F18]:
        comms.append("F18")
    if keystatus[sdl2.SDL_SCANCODE_F19]:
        comms.append("F19")
    if keystatus[sdl2.SDL_SCANCODE_F20]:
        comms.append("F20")
    if keystatus[sdl2.SDL_SCANCODE_F21]:
        comms.append("F21")
    if keystatus[sdl2.SDL_SCANCODE_F22]:
        comms.append("F22")
    if keystatus[sdl2.SDL_SCANCODE_F23]:
        comms.append("F23")
    if keystatus[sdl2.SDL_SCANCODE_F24]:
        comms.append("F24")
    if keystatus[sdl2.SDL_SCANCODE_DELETE]:
        comms.append("DEL")
    if keystatus[sdl2.SDL_SCANCODE_TAB]:
        comms.append("TAB")
    if keystatus[sdl2.SDL_SCANCODE_LALT] or keystatus[sdl2.SDL_SCANCODE_RALT]:
        comms.append("ALT")
    if keystatus[sdl2.SDL_SCANCODE_LEFT]:
        comms.append("LEFT")
    if keystatus[sdl2.SDL_SCANCODE_RIGHT]:
        comms.append("RIGHT")
    if keystatus[sdl2.SDL_SCANCODE_UP]:
        comms.append("UP")
    if keystatus[sdl2.SDL_SCANCODE_DOWN]:
        comms.append("DOWN")
    if keystatus[sdl2.SDL_SCANCODE_BACKSPACE]:
        comms.append("BACKSPACE")

    #If caps key down add capital equivalent of key
    if caps or "SHIFT" in comms:
        upper = []
        for key in keys:
            upper.append(uppercase[key])
        keys = upper

    return((keys,comms))

#Capital equivalents
uppercase = {
    "a":"A","b":"B","c":"C","d":"D","e":"E","f":"F","g":"G","h":"H","i":"I","j":"J","k":"K","l":"L","m":"M","n":"N","o":"O","p":"P","q":"Q","r":"R","s":"S","t":"T","u":"U","v":"V","w":"W","x":"X","y":"Y","z":"Z",
    
    "1":"!","2":"@","3":"#","4":"$","5":"%","6":"^","7":"&","8":"*","9":"(","0":")",
    
    "-":"_","=":"+","\\":"|",";":":","'":"\"","[":"{","]":"}",",":"<",".":">","/":"?"," ":" ","`":"~",
}