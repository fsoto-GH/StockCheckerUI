from tkinter import *

from Constants import APP_XPAD, APP_YPAD, APP_GEO, RESIZABLE_WIDTH, RESIZABLE_HEIGHT
from Constants import APP_BACKGROUND_COLOR, APP_TEXT_COLOR
from StockWidgetMainFrame import StockWidgetMainFrame


class Application(Frame):
    def __init__(self, master=None, width=None, height=None):
        super().__init__(master, width=width, height=height)
        self.grid(padx=APP_XPAD, pady=APP_YPAD)
        self.config(background='BLACK')
        self.master.config(background='BLACK')
        # stock widget canvas
        self.main_container = StockWidgetMainFrame(parent=self)
        self.main_container.grid(row=1, column=0, pady=APP_YPAD)

        self.widget_count = 0
        self.curr_page = 0


if __name__ == '__main__':
    import os

    # change to file directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    root = Tk()
    root.geometry(APP_GEO)
    app = Application(root)
    root.minsize(*APP_GEO.split('x'))
    root.title("Best Buy Stock Checker")
    root.resizable(RESIZABLE_WIDTH, RESIZABLE_HEIGHT)
    root.tk_setPalette(background=APP_BACKGROUND_COLOR, foreground=APP_TEXT_COLOR)
    app.pack(expand=False)
    root.mainloop()
