import tkinter as tk
import tkinter.colorchooser as tkc
from tkinter import ttk
from tkinter import filedialog
import json
import os
from extractor import *
from PIL import Image, ImageTk

colour_labels=["colour_bg", "colour_fg"]
for i in range(16):
    colour_labels.append("colour_{0}".format(i))

def load_json(file_name):
    return json.load(file_name)

class MainApp:
    def __init__(self, root):
        self.root=root
        self.app=PyPalette(master=self.root)
    def run(self):
        self.app.mainloop()

class PyPalette(tk.Frame):
    def __init__(self, master):
        super().__init__(master)

        self.pack(expand=True, fill='both')
        self.create_widgets(master)

    def create_widgets(self, master):
        self.notebook=ttk.Notebook(self)
        self.colours_page=ColoursPage(self)
        #self.colours_render=ColourRenderer(self, self.colours_page)
        self.notebook.add(self.colours_page, text="Colours Page")
        self.notebook.add(ImageLoader(self, self.colours_page), text='Image Loader')
        #self.notebook.add(self.colours_render, text="Colours Render")
        self.notebook.pack(expand=True, fill='both')
        #self.notebook.grid(row=0, column=0, sticky='news')
        #self.notebook.rowconfigure(0, weight=1)
        #self.notebook.columnconfigure(0, weight=1)

class ColoursPage(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.load_text=tk.StringVar()
        self.load_text.set(os.path.abspath('.')+"/")
        self.create_widgets()

    def create_widgets(self):
        colours={}
        self.labels={}
        for colour in colour_labels:
            self.labels[colour]=ColourPicker(self, colour, "#ffffff")
        self.labels["colour_bg"].grid(row=0, column=0, sticky='news')
        self.labels["colour_fg"].grid(row=0, column=1, sticky='news')
        for i in range(16):
            c=1
            if i<8: c=0
            r = i+1
            if i>7: r=i-7
            self.labels["colour_{0}".format(i)].grid(row=r, column=c, sticky='news')
        
        self.file_box=tk.Entry(self, textvariable=self.load_text)
        self.file_box.grid(row=9, column=0, columnspan=2, sticky="news")
        self.loadbutton=tk.Button(self, text="Load file", command=self.load_scheme)
        self.loadbutton.grid(row=10, column=0)
        self.savebutton=tk.Button(self, text="Save file", command=self.save_scheme)
        self.savebutton.grid(row=10, column=1)
        self.colour_renderer=ColourRenderer(self, self)
        self.colour_renderer.grid(row=0, column=3, rowspan=11, sticky="news")
        self.reset_button=tk.Button(self, text="Reset Colours", command=self.reset_colours)
        self.reset_button.grid(row=12, column=3)
        self.set_light=tk.Button(self, text="Set Lighter Colours to Darker", command=self.set_lighter_darker)
        self.set_light.grid(row=13, column=3)
        for i in range(11): 
            self.rowconfigure(i, weight=1) 
        for i in range(2):
            self.columnconfigure(i, weight=1)

    def load_scheme(self, *args):
        cols=None

        p=os.path.expanduser(self.load_text.get())
        n=os.path.basename(p)
        p=os.path.dirname(p)
        with filedialog.askopenfile(initialdir=p, initialfile=n) as f:
            cols=load_json(f)
        if cols is not None:
            for key in cols:
                self.labels[key].colour.set(cols[key])
        self.colour_renderer.update_self()

    def save_scheme(self, *args):
        pathname=os.path.expanduser(self.load_text.get())
        pathstrip=os.path.dirname(pathname)
        n=os.path.basename(pathname)
        if os.path.exists(pathstrip):
            cols={}
            for key in self.labels:
                cols[key]=self.labels[key].colour.get()
            with filedialog.asksaveasfile(initialdir=pathstrip, initialfile=n) as f:
                json.dump(cols, f)
                print("Saved to {0}".format(pathname))

    def reset_colours(self, *args):
        for key in self.labels:
            self.labels[key].colour.set("#ffffff")

    def set_lighter_darker(self, *args):
        for i in range(8):
            self.labels['colour_{0}'.format(i+8)].colour.set(self.labels['colour_{0}'.format(i)].colour.get())

class ColourPicker(tk.Frame):
    def __init__(self, master, label, colour="#FFFFFF", *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.colour=tk.StringVar()
        self.colour.set(colour)
        self.create_widgets(label)
        self.colour.trace('w', self.set_box_colour)
        self.set_box_colour()
        
    def create_widgets(self, label):
        self.label=tk.Label(self, text=label)
        self.label.grid(row=0, column=0, sticky='nswe')
        self.button=tk.Button(self, textvariable=self.colour)
        self.button["command"]=self.colour_helper
        self.text_box=tk.Entry(self, textvariable=self.colour)
        self.button.grid(row=1, column=0, sticky="nswe")
        self.text_box.grid(row=2, column=0, sticky='nswe')
        self.columnconfigure(0, weight=1)
        for i in range(3):
            self.rowconfigure(i, weight=1)

    def colour_helper(self):
        try:
            returncol=tkc.askcolor(self.colour.get())[1]
        except:
            returncol=tkc.askcolor('#ffffff')[1]
        if returncol!=None:
            self.colour.set(returncol)

    def set_box_colour(self, *args):
        try:
            self.button["bg"]=self.colour.get()
        except:
            self.button["bg"]="#FFFFFF"

class ColourRenderer(tk.Frame):
    def __init__(self, master, colours_page, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.canvas_c=(500, 500)
        self.colours_page=colours_page.labels
        self.canvas=tk.Canvas(self, width=self.canvas_c[0], height=self.canvas_c[1], bg='#ffffff')
        self.canvas.place()
        self.canvas.grid(row=0, column=0, sticky='news')
        self.button=tk.Button(self, text='Generate', command=self.update_self)
        self.button.grid(row=1, column=0, sticky='news')
        self.update_self()

    def update_self(self):
        self.canvas.delete('all')
        box_height=self.canvas_c[1]/9.  
        third_height=box_height/3.
        box_width=self.canvas_c[0]/9.
        half_width=box_width/2.

        self.canvas.create_rectangle(0, 0, self.canvas_c[0], box_height, fill=self.colours_page['colour_bg'].colour.get())
        bgcol=self.colours_page['colour_bg'].colour.get()
        fgcol=self.colours_page['colour_fg'].colour.get()
        self.canvas.create_text(half_width, third_height, text=bgcol, fill=bgcol)
        self.canvas.create_text(half_width, 2*third_height, text=fgcol, fill=fgcol)
        for j in range(8):
            col_bg=self.colours_page['colour_{0}'.format(j)].colour.get()
            col_fg=self.colours_page['colour_{0}'.format(j+8)].colour.get()
            self.canvas.create_text((j+1)*box_width+half_width, third_height, text=col_bg, fill=col_bg)
            self.canvas.create_text(half_width+box_width*(j+1), third_height*2, text=col_fg, fill=col_fg)

        for i in range(8):
            self.canvas.create_rectangle(0, box_height*(i+1), self.canvas_c[0], box_height*(i+2), fill=self.colours_page['colour_{0}'.format(i)].colour.get())
            self.canvas.create_text(half_width, third_height+box_height*(i+1), text=bgcol, fill=bgcol)
            self.canvas.create_text(half_width, third_height*2+box_height*(i+1), text=fgcol, fill=fgcol)
            for j in range(8):
                col_bg=self.colours_page['colour_{0}'.format(j)].colour.get()
                col_fg=self.colours_page['colour_{0}'.format(j+8)].colour.get()
                self.canvas.create_text((j+1)*box_width+half_width, third_height+box_height*(i+1), text=col_bg, fill=col_bg)
                self.canvas.create_text(half_width+box_width*(j+1), third_height*2+box_height*(i+1), text=col_fg, fill=col_fg)

class ImageLoader(tk.Frame):
    def __init__(self, master, colours_page, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.cp=colours_page
        self.load_text=tk.StringVar()
        self.load_text.set(os.path.abspath('.')+"/")

        self.create_widgets()


    def create_widgets(self):
        self.canvas=tk.Canvas(self, width=600, height=600)
        self.entry=tk.Entry(self, textvariable=self.load_text)
        self.load18=tk.Button(self, text="Load Image 18 colours", command=self.load_image_18)
        self.load9=tk.Button(self, text="Load Image 9 colours", command=self.load_image_9)
        self.canvas.grid(row=0, column=0, columnspan=1, sticky='news')
        self.entry.grid(row=1, column=0, columnspan=1, sticky='news')
        self.load18.grid(row=2, column=0)
        self.load9.grid(row=3, column=0)

    def load_image_18(self, *args):
        pilimage=Image.open(os.path.expanduser(self.load_text.get()))
        pilimage.thumbnail((600, 600))
        self.photo=ImageTk.PhotoImage(pilimage)
        self.canvas.delete('all')
        self.canvas.create_image(300, 300, image=self.photo)
        cols=prepare_pypalette(os.path.expanduser(self.load_text.get()))
        for key in self.cp.labels:
            self.cp.labels[key].colour.set(cols[key])

    def load_image_9(self, *args):
        pilimage=Image.open(os.path.expanduser(self.load_text.get()))
        pilimage.thumbnail((600, 600))
        self.photo=ImageTk.PhotoImage(pilimage)
        self.canvas.delete('all')
        self.canvas.create_image(300, 300, image=self.photo)
        cols=prepare_pypalette_9(os.path.expanduser(self.load_text.get()))
        for key in cols:
            self.cp.labels[key].colour.set(cols[key])


