'''
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

This software is the ground station GUI software that will be used to view and
analyze flight data while also be able to configure the custom flight computer
built by the students of SEDS@IIT.

The goal is to make the software compatable with multiple OS enviroments with
minimal additional packages and easy to use for users unfamiliar with the
software.

TO DO:
# - fix bug on static plot need to move plot to see plotted data
# - have matplotlib plots appear in the gui window in quadrants
- have a performance metric bar on the side of the GUI
- be able to communicate with STM32F4 over USB (COM)
- have a window to print output of USB device
'''

### IMPORT START ###
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import matplotlib.animation as animation
from matplotlib import style
from matplotlib import pyplot as plt

import tkinter as tk
from tkinter import TOP, Canvas, Label, ttk
from tkinter.filedialog import askopenfilename

from PIL import ImageTk, Image

import pandas as pd
import numpy as np

import os
import sys

import settings
### IMPORT END ###

### STYLING START ###
LARGE_FONT = ("Verdona", 12)
style.use("ggplot")

live_plot = Figure(figsize=(5,5), dpi=100)
live_plot_subplot1 = live_plot.add_subplot(221)
live_plot_subplot2 = live_plot.add_subplot(222)
live_plot_subplot3 = live_plot.add_subplot(223)
live_plot_subplot4 = live_plot.add_subplot(224)

static_plot = Figure(figsize=(5,5), dpi=100)
static_plot_subplot1 = static_plot.add_subplot(221)
static_plot_subplot2 = static_plot.add_subplot(222)
static_plot_subplot3 = static_plot.add_subplot(223)
static_plot_subplot4 = static_plot.add_subplot(224)

### STYLING END ###

### GLOBAL VARIABLES START ###
PATH = os.path.dirname(__file__)
if sys.platform == "linux" or sys.platform == "linux2":
    PLATFORM = "linux"
elif sys.platform == "darwin":
    PLATFORM = "macOS"
elif sys.platform == "win32":
    PLATFORM = "windows"
else:
    print("WARNING: Unrecognized platform")
    quit()
    
PATH_DATAFILE = os.path.join(PATH, 'data', 'Init.csv')
PATH_LIVEDATA = os.path.join(PATH, 'data', 'TestData.csv') # placeholder

### GLOBAL VARIABLES END ###

### CLASS START ###
class GSApp(tk.Tk):
    def __init__(self, *args, **kwargs):
        
        tk.Tk.__init__(self, *args, **kwargs)
                
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        menubar = tk.Menu(container)
        
        # File Menu 
        fileMenu = tk.Menu(menubar, tearoff=0)
        fileMenu.add_command(label="Save Settings", command = lambda: tk.messagebox.showinfo("Information","Not supported yet!"))
        fileMenu.add_command(label="Open", command= lambda: select_file())
        fileMenu.add_separator()
        fileMenu.add_command(label="Exit", command = lambda: quit()) # Fixed?
        menubar.add_cascade(label="File", menu=fileMenu)

        # Page Menu
        pageMenu = tk.Menu(menubar, tearoff=0)
        pageMenu.add_command(label="Home", command = lambda: self.show_frame(HomePage))
        pageMenu.add_separator()
        pageMenu.add_command(label="Data Analysis", command = lambda: self.show_frame(DataAnalysis))
        pageMenu.add_command(label="FC Config", command = lambda: self.show_frame(FCConfig))
        pageMenu.add_command(label="Live Flight Data", command = lambda: self.show_frame(LiveFlight))
        menubar.add_cascade(label="Page", menu=pageMenu)

        # Settings Menu
        settingsMenu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Settings", menu=settingsMenu)

        # Help Menu
        helpMenu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=helpMenu)

        tk.Tk.config(self, menu=menubar)

        self.frames = {}

        # Load all pages initially
        for page in (HomePage, DataAnalysis, FCConfig, LiveFlight):

            frame = page(container, self)

            self.frames[page] = frame

            frame.grid(row=0, column=0, sticky="nsew")
        
        self.show_frame(HomePage)

    # Show frame that is requested
    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()

# Individual Pages Start

class HomePage(tk.Frame):
    def __init__(self, parent, controller):
        # Create multiple widgets in a frame to make organization easier

        # title
        tk.Frame.__init__(self, parent)
        label = ttk.Label(self, text=("Ad Astra Per Aspera"), font=LARGE_FONT)
        label.pack()
        label.place(relx=0.5, rely=0.1, anchor="n")
        
        # menu
        button = ttk.Button(self, text="Data Analysis",
                            command=lambda: controller.show_frame(DataAnalysis))
        button.pack()
        button.place(relx=0.3, rely=0.2, anchor="n")

        button2 = ttk.Button(self, text="Flight Computer Configure",
                            command=lambda: controller.show_frame(FCConfig))
        button2.pack()
        button2.place(relx=0.5, rely=0.2, anchor="n")

        button3 = ttk.Button(self, text="Live Flight Data",
                            command=lambda: controller.show_frame(LiveFlight))
        button3.pack()
        button3.place(relx=0.7, rely=0.2, anchor="n")
        
        # image

        filepath_logo_nobg = os.path.join(PATH, 'images', 'SEDSIIT-logo_noBG.png')

        render = ImageTk.PhotoImage(Image.open(filepath_logo_nobg))
        img = ttk.Label(self, image=render)
        img.image = render
        img.pack()
        img.place(relx=0.5, rely=0.3, anchor="n")
        


class DataAnalysis(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = ttk.Label(self, text="Data Analysis", font=LARGE_FONT)
        label.pack(pady=10, padx=10)

        button_file_select = ttk.Button(self, text="Select File",
                                    command=lambda: select_file())
        button_file_select.pack(side=TOP)

        # static plot
        canvas = FigureCanvasTkAgg(static_plot, self)
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        canvas.draw()
        

        toolbar = NavigationToolbar2Tk(canvas, self)
        toolbar.update()
        canvas._tkcanvas.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

class FCConfig(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = ttk.Label(self, text="Flight Computer Configure", font=LARGE_FONT)
        label.pack(pady=10, padx=10)

        button1 = ttk.Button(self, text="Home",
                            command=lambda: controller.show_frame(HomePage))
        button1.pack()


class LiveFlight(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = ttk.Label(self, text="Telemetry Data", font=LARGE_FONT)
        label.pack(pady=10, padx=10)

        button1 = ttk.Button(self, text="Home",
                            command=lambda: controller.show_frame(HomePage))
        button1.pack()

        # Live Plot
        canvas = FigureCanvasTkAgg(live_plot, self)
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        canvas.draw()

        toolbar = NavigationToolbar2Tk(canvas,self)
        toolbar.update()
        canvas._tkcanvas.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

# Individual Pages End
### CLASS END ###


### FUNCTION DEFINE START ###
# Get window screen information to scale window properly
def get_win_dimensions(root):
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    window_width = int(screen_width * settings.window.scale_width)
    window_height = int(screen_height * settings.window.scale_height)

    window_dimensions = str(window_width) + "x" + str(window_height)
    
    if (settings.DEBUG.status == True):
        print("Window Stats:")
        print("screen width:", screen_width)
        print("window width scale:", settings.window.scale_width)
        print("window width:", window_width)
        print("screen height:", screen_height)
        print("window height scale:", settings.window.scale_height)
        print("window height:", window_height)
        print("window dimensions:", window_dimensions)
        print()

    return window_dimensions

# Used to animate a matplotlib figure
def animate_live_plot(i):
    data = pd.read_csv(PATH_LIVEDATA)
    data.drop(["Events"], axis=1)
    
    live_plot_subplot1.clear()
    live_plot_subplot2.clear()
    live_plot_subplot3.clear()
    live_plot_subplot4.clear()
    live_plot_subplot1.plot(data['Time'], data['Altitude'], color='k')
    live_plot.subplots_adjust(hspace = 0.3)
    live_plot_subplot2.plot(data['Time'], data['Velocity'], color='r')
    live_plot_subplot1.set_xlabel("Time (sec)")
    live_plot_subplot1.set_ylabel("AGL Altitude (ft)")
    live_plot_subplot2.set_xlabel("Time (sec)")
    live_plot_subplot2.set_ylabel("Velocity (ft/s)")
    live_plot_subplot3 
    live_plot_subplot4

def plot_static(): 
    data = pd.read_csv(PATH_DATAFILE)
    data.drop(["Events"], axis=1)
   
    static_plot_subplot1.clear()
    static_plot_subplot2.clear()
    static_plot_subplot3.clear()
    static_plot_subplot4.clear()
    static_plot_subplot1.plot(data['Time'], data['Altitude'], color='k')
    static_plot.subplots_adjust(hspace = 0.3)
    static_plot_subplot2.plot(data['Time'], data['Velocity'], color='r')
    static_plot_subplot1.set_xlabel("Time (sec)")
    static_plot_subplot1.set_ylabel("AGL Altitude (ft)")
    static_plot_subplot2.set_xlabel("Time (sec)")
    static_plot_subplot2.set_ylabel("Velocity (ft/s)")
    static_plot_subplot3 
    static_plot_subplot4

def select_file():
    global PATH_DATAFILE
    PATH_DATAFILE = askopenfilename()
    print("Selected data file path: %s" % (PATH_DATAFILE))
    plot_static()
    

### MAIN START ###
def main():
    ### SETUP START ###
    if (settings.DEBUG.status == True):
        print("Starting ground station GUI...")
        print()
    ### SETUP END ###

    app = GSApp()
    app.geometry(get_win_dimensions(app))
    app.minsize(600,400)
    app.title("Ground Station Application")

    filepath_icon_photo = os.path.join(PATH, 'images', 'SEDSIIT-logo.png')
    app.tk.call('wm','iconphoto',app._w,tk.Image("photo", file=filepath_icon_photo))

    ani = animation.FuncAnimation(live_plot, animate_live_plot, interval=500)
   
    app.mainloop()
### MAIN END ###
### FUNCTION DEFINE END ###

if __name__ == '__main__':
    main()