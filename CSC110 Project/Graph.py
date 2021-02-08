#
# Grapher class
# Main project (Visualizer.py) inherits from Grapher
#

import data

from tkinter import *
from PIL import Image, ImageDraw, ImageTk, ImageFont
import numpy as np
from typing import List, Tuple
import time


def reScale(old: float, old_min: float, old_max: float,
            new_min: float, new_max: float) -> float:
    """Linearly rescales old value to new bounds"""
    return (old - old_min) / (old_max - old_min) \
           * (new_max - new_min) + new_min


f = ('Times', 15, 'bold')
g = ('Times', 22)

class Grapher(Frame):
    """Tkinter window that provides basic line graphing"""
    
    def __init__(self, root=None) -> None:
        """Initialize window and properties"""
        
        # This class can be run by itself or be subclassed
        if root is None:
            root = Tk()
        super().__init__(root)
        
        self.W = 960
        self.H = 600

        root.title("CSC Project")

        self.root = root

        self.BUTTON_SIZE = (self.W*3//8, self.W//7)
        button = Image.open("Button2.png").convert("RGBA")
        button = button.resize(self.BUTTON_SIZE)
        self._button = np.array(button, "float") * 1

        # Copy so we can change opacity value
        self.buttons = [np.array(self._button),
                        np.array(self._button)]

        self.canvasItems = []

        # 'C' or 'U' for Canada/USA
        self.country = 'C'

        self.window = 'Graph'


    def start(self):
        self.setupData()
        
        self.makeWidgets()

        self.graphData()

        self.updateCanvasGraph()

    def setupData(self) -> None:
        """Retrieve data from the data.py module"""        
        
        print("Importing data...")
        t = time.perf_counter()
        self.datU = data.UsaData().data
        self.datC = data.CanadaData().data
        print("Done in", time.perf_counter() - t)
        

    def makeWidgets(self) -> None:
        """Creates the Tkinter widgets for use"""
        self.grid(sticky=N+E+S+W)

        self.d = Canvas(self, width=self.W, height=self.H,
                        highlightthickness=0, highlightbackground="black")
        self.d.grid(row=0, column=0, sticky=N+E+S+W)
        self.d.config(background="#000")
        self.d.bind("<Button-1>", self.clicked)
        self.finalRender = self.d.create_image((self.W/2, self.H/2))

        self.d.focus_set()


    def clearCanvas(self) -> None:
        """Deletes items in self.canvasItems from the canvas self.d"""
        for i in self.canvasItems:
            self.d.delete(i)
    
    def graphData(self) -> None:
        """Draw a double line graph and axis labels"""
        self.clearCanvas()
        
        self.img = Image.new("RGBA", (self.W, self.H))

        bounds = (self.W//6, 10, self.W*2//3, self.H*3//5)

        if self.country == 'C':
            dat = self.datC
        else:
            dat = self.datU

        year_min = min(dat)
        year_max = max(dat)
        self.year_min = year_min
        self.year_max = year_max
        
        # Donation
        coords = [(year, dat[year]['Donation']) for year in dat]
        don_min = min(c[1] for c in coords)
        don_max = max(c[1] for c in coords)

        # Sort by year
        coords = sorted(coords)
        self.graph(coords, bounds, (192,128,0,255))

        # Emission
        coords = [(year, dat[year]['Emission']) for year in dat]
        emi_min = min(c[1] for c in coords)
        emi_max = max(c[1] for c in coords)

        # Sort by year
        coords = sorted(coords)
        self.graph(coords, bounds, (0,160,192,255))


        # Make axes
        axes = [(0,1),(0,0),(1,0),(1,1)]
        self.graph(axes, bounds, (255,255,255,255))

        # Make axis labels on Tk canvas
        # (too troublesome to wrangle PIL fonts across platforms)
        currency = 'CAD' if self.country == 'C' else 'USD'
        yd = self.d.create_text(self.W//6 - 10, 180, anchor='e',
                                text='Donations\n({})'.format(currency),
                                fill='#c80', font=f)
        ye = self.d.create_text(self.W*5//6 + 10, 180, anchor='w',
                                text='Emissions\n(MT CO2)',
                                fill='#0ac', font=f)


        ld = self.d.create_text(self.W//6 - 10, self.H*3//5 + 10, anchor='e',
                                text=str(don_min), fill='#c80', font=f)
        hd = self.d.create_text(self.W//6 - 10, 10, anchor='ne',
                                text=str(don_max), fill='#c80', font=f)

        le = self.d.create_text(self.W*5//6 + 10, self.H*3//5 + 10, anchor='w',
                                text=str(emi_min), fill='#0ac', font=f)
        he = self.d.create_text(self.W*5//6 + 10, 10, anchor='nw',
                                text=str(emi_max), fill='#0ac', font=f)

        year = self.d.create_text(self.W//2, self.H*3//5 + 20, anchor='n',
                                  text='Year', fill='#fff', font=f)
        y_low = self.d.create_text(self.W//6, self.H*3//5 + 20, anchor='nw',
                                  text=year_min, fill='#fff', font=f)
        y_high = self.d.create_text(self.W*5//6, self.H*3//5 + 20, anchor='ne',
                                  text=year_max, fill='#fff', font=f)

        self.canvasItems = [yd, ye, ld, hd, le, he, year, y_low, y_high]

        frame = np.array(self.img, dtype='int')
        self.blend(frame, self.buttons[0], (self.W//4, self.H-80), 'screen')
        self.blend(frame, self.buttons[1], (self.W*3//4, self.H-80), 'screen')
        frame[:,:,3] = 255
        frame = np.clip(frame, 0, 255)
        self.img1 = Image.fromarray(frame.astype('uint8'))
        
        button1 = self.d.create_text(self.W//4, self.H-80,
                                     text='Switch countries', fill='#fff', font=g)
        
        button2 = self.d.create_text(self.W*3//4, self.H-80,
                                     text='Back', fill='#fff', font=g)
    
        self.canvasItems.extend([button1, button2])

        # Update canvas image
        self.cf = ImageTk.PhotoImage(self.img1)
        self.d.itemconfigure(self.finalRender, image=self.cf)


    def graph(self, coords: List[Tuple[int,int]], bounds: Tuple[int,int,int,int],
              color: Tuple[int,int,int,int]) -> None:
        """Draw a line joining coords together within bounds
            Bounds is (x, y, width, height)
        """
        
        # Scale data to fit in (0,1)
        xy = np.array(coords, dtype="float")
        xy[:,1] *= -1
        x_max = np.max(xy[:,0])
        x_min = np.min(xy[:,0])
        y_max = np.max(xy[:,1])
        y_min = np.min(xy[:,1])

        xy[:,0] = (xy[:,0] - x_min) / (x_max-x_min)
        xy[:,1] = (xy[:,1] - y_min) / (y_max-y_min)

        # Scale data to fit in bounds
        xy[:,0] *= bounds[2]
        xy[:,0] += bounds[0]
        xy[:,1] *= bounds[3]
        xy[:,1] += bounds[1]

        # Draw data
        d = ImageDraw.Draw(self.img)
        d.line(xy.flatten().tolist(), fill=color, width=4)


    def updateCanvasGraph(self) -> None:
        """Main event loop"""
        self.graphData()
        
        x = self.d.winfo_pointerx() - self.d.winfo_rootx()
        y = self.d.winfo_pointery() - self.d.winfo_rooty()

        # Make lines if mouse is hovering
        if self.selected(x, y, (self.W//6, 10, self.W*5//6, self.H*3//5)):
            selected_year = reScale(x, self.W//6, self.W*5//6,
                                    self.year_min, self.year_max)
            selected_year = round(selected_year)
            new_xcoord = reScale(selected_year, self.year_min, self.year_max,
                                 self.W//6, self.W*5//6)
            
            vrule = self.d.create_line(new_xcoord, 10, new_xcoord, self.H*3//5,
                                       fill='#c0a', width=2)
            self.d.tag_raise(vrule)
            self.canvasItems.append(vrule)
            sel_year = self.d.create_text(self.W//2, self.H*3//5 + 40,
                                          anchor='n', text=str(selected_year),
                                          fill='#c0a', font=f)
            self.d.tag_raise(sel_year)
            self.canvasItems.append(sel_year)
        
        if self.selected(x, y, (100, 480, 380, 550)):
            self.buttons[0] = 1.5 * self._button
        else:
            self.buttons[0] = 0.9 * self._button
        if self.selected(x, y, (580, 480, 860, 550)):
            self.buttons[1] = 1.5 * self._button
        else:
            self.buttons[1] = 0.9 * self._button

        if self.window == 'Graph':
            self.after(12, self.updateCanvasGraph)
    
        
    def clicked(self, evt) -> None:
        """Handles mouse click events"""
        if self.selected(evt.x, evt.y, (100, 480, 380, 550)):
            if self.country == 'C':
                self.country = 'U'
            else:
                self.country = 'C'


    def selected(self, x, y, bounds) -> bool:
        """Return if (x,y) is inside bounds
            bounds = (left, up, right, down)
        """
        return bounds[0] < x < bounds[2] and bounds[1] < y < bounds[3]


    def blend(self, dest: np.array, source: np.array,
              coords: tuple, method="alpha") -> None:
        """Blend image source onto dest
            centered at coords (x, y)

            - method in {"alpha", "add", "screen"}
        """
        left = coords[0] - (source.shape[1]//2)
        right = left + source.shape[1]
        up = coords[1] - (source.shape[0]//2)
        down = up + source.shape[0]

        if method == "alpha":
            alpha = np.expand_dims(source[:,:,3], -1) / 255
            dest[up:down, left:right] = dest[up:down, left:right] * (1-alpha) \
                                        + source * alpha
        
        if method == "add":
            dest[up:down, left:right] = dest[up:down, left:right] + source
        
        if method == "screen":
            dest[up:down, left:right] = 255 - (255 - dest[up:down, left:right]) \
                                        * (255 - source) / 255


if __name__ == "__main__":
    a = Grapher()
    a.start()
    a.mainloop()
