# Main menu

from tkinter import *
from PIL import Image, ImageTk, ImageDraw
import numpy as np
import time

from Graph import Grapher
import Plot

f = ('Times', 32, 'bold')

class Project(Grapher):
    """Tkinter window for the menu and graph"""
    
    def __init__(self, root=None) -> None:
        if root is None:
            root = Tk()
        super().__init__(root)

        self.root = root
        self.root.title('CSC Project')
        self.W = 960
        self.H = 600

        self.totFrames = 0
        self.startTime = time.time()

        # Frameless window centered on screen
        root.overrideredirect(True)
        offsetX = root.winfo_screenwidth()//2 - self.W//2
        offsetY = root.winfo_screenheight()//2 - self.H//2
        root.geometry("+{}+{}".format(offsetX, offsetY))
        root.lift()
        root.wm_attributes("-topmost", True)

        self.canvasItems = []

        self.window = 'Menu'

        self.BUTTON_SIZE = (self.W*3//8, self.W//7) # W, H

        # Open image assets
        bg = Image.open("Background.jpg")
        bg = bg.convert("RGBA").resize((self.W,self.H))
        self.background = np.array(bg, "float")

        title = Image.open("Title.png").resize((500, 200))
        self.title = np.array(title, "float")

        names = Image.open("Names.png").convert("RGBA").resize((400, 36))
        self.names = np.array(names, "float")
        
        button = Image.open("Button2.png").convert("RGBA").resize((500, 200))
        button = button.resize(self.BUTTON_SIZE)
        self.button = np.array(button, "float") * 1
        
        # Copy so we can change the intensity of each button individually
        self.buttons = [np.array(self.button),
                        np.array(self.button),
                        np.array(self.button),
                        np.array(self.button)]


    def start(self) -> None:
        """Starts"""
        self.makeWidgets()

        self.render()

        self.after(10, self.updateCanvas)


    def makeWidgets(self) -> None:
        self.grid(sticky=N+E+S+W)

        self.d = Canvas(self, width=self.W, height=self.H,
                        highlightthickness=0, highlightbackground="black")
        self.d.grid(row=0, column=0, sticky=N+E+S+W)
        self.d.config(background="#000")
        self.d.bind("<Button-1>", self.clicked)
        self.finalRender = self.d.create_image((self.W/2, self.H/2))


    def render(self) -> None:
        self.totFrames += 1
        
        # Darken background
        frame = self.background * 0.6
        
        # Blend in title and names
        self.blend(frame, self.title, (self.W//2, self.H//6))
        self.blend(frame, self.names, (self.W//2, self.H - 60), "add")

        # Blend in menu buttons
        self.blend(frame, self.buttons[0], (self.W//4, self.H-320), "screen")        
        self.blend(frame, self.buttons[1], (self.W//4, self.H-180), "screen")
        self.blend(frame, self.buttons[2], (self.W*3//4, self.H-320), "screen")        
        self.blend(frame, self.buttons[3], (self.W*3//4, self.H-180), "screen")

        # Convert numpy array to image
        frame[:,:,3] = 255
        frame = np.clip(frame, 0, 255)
        i = Image.fromarray(frame.astype("uint8"))
        self.cf = ImageTk.PhotoImage(i)
        self.d.itemconfigure(self.finalRender, image=self.cf)

        self.clearCanvas()
        # Add text to buttons
        self.text0 = self.d.create_text(self.W*1//4, self.H-320,
                                        text="Button", fill="#fff", font=f)
        
        self.text1 = self.d.create_text(self.W*1//4, self.H-180,
                                        text="Line Graph", fill="#fff", font=f)

        self.text2 = self.d.create_text(self.W*3//4, self.H-320,
                                        text="Scatter Graph", fill="#fff", font=f)
        
        self.text3 = self.d.create_text(self.W*3//4, self.H-180,
                                        text="Quit", fill="#fff", font=f)

        self.canvasItems = [self.text0, self.text1, self.text2, self.text3]



    def updateCanvas(self) -> None:
        x = self.d.winfo_pointerx() - self.d.winfo_rootx()
        y = self.d.winfo_pointery() - self.d.winfo_rooty()

        # Button updating
        self.updateButton(0, x, y, (100, 240, 380, 320))
        self.updateButton(1, x, y, (100, 380, 380, 460))
        self.updateButton(2, x, y, (500, 240, 780, 320))
        self.updateButton(3, x, y, (500, 380, 780, 460))

        # This takes the most time
        self.render()

        if self.window == 'Menu':
            self.after(12, self.updateCanvas)


    def updateButton(self, num, x, y, bounds):
        """Highlight a button if selected"""
        if self.selected(x, y, bounds):
            self.buttons[num] = 1.6 * self.button
        else:
            self.buttons[num] = 1.0 * self.button



    def clicked(self, evt) -> None:
        """Handle click events"""
        if self.window == 'Menu':
            if self.selected(evt.x, evt.y, (100, 240, 380, 320)):
                print("Button 0 pressed")
            if self.selected(evt.x, evt.y, (100, 380, 380, 460)):
                # print("Button 1 pressed")
                self.window = "Graph"
                
                self.clearCanvas()
                self.setupData()
                self.graphData()
                self.updateCanvasGraph()
                
            if self.selected(evt.x, evt.y, (500, 240, 780, 320)):
                # print("Button 2 pressed")
                Plot.showPlots()
                
            if self.selected(evt.x, evt.y, (500, 380, 780, 460)):
                # print("Button 3 pressed")
                print("Quit")
                self.root.destroy()
            

        elif self.window == 'Graph':
            if self.selected(evt.x, evt.y, (100, 480, 380, 550)):
                if self.country == 'C':
                    self.country = 'U'
                else:
                    self.country = 'C'
            
            if self.selected(evt.x, evt.y, (500, 480, 780, 550)):
                self.window = "Menu"
                
                self.clearCanvas()
                self.updateCanvas()


if __name__ == "__main__":
    a = Project()
    a.start()
    a.mainloop()
    print("FPS:", a.totFrames / (time.time() - a.startTime))
