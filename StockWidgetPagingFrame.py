from tkinter import *

from Constants import APP_BUTTON_COLOR, APP_TEXT_COLOR


class StockWidgetPagingFrame(Frame):
    """
    This widget represent a paging controller.
    This widget expects a left page and right page callback to report to upon the click
    of the arrows. In addition, the total pages and the current page must also be callable
    methodically.
    """

    def __init__(self, parent, page_left_callback, page_right_callback, curr_page_callback, page_count_callback):
        super(StockWidgetPagingFrame, self).__init__(parent)
        self.pleft_callback = page_left_callback
        self.pleft_callback = page_left_callback
        self.pright_callback = page_right_callback
        self.cpages_callback = curr_page_callback
        self.tpages_callback = page_count_callback

        self.__page_count = 1
        self.__curr_page = 1
        self.lbl_page = Label(self, anchor=E)
        self.lbl_page.config(width=10)
        self.lbl_page.grid(row=0, column=0, sticky=E)
        self.lbl_page.config(background=APP_BUTTON_COLOR, foreground=APP_TEXT_COLOR)

        # paging buttons
        self.btn_left = Button(self, text="<", command=self.page_left)
        self.btn_left.config(background=APP_BUTTON_COLOR, foreground=APP_TEXT_COLOR)
        self.btn_left.config(width=3)
        self.btn_left.grid(row=0, column=1, sticky=E)

        self.btn_right = Button(self, text=">", command=self.page_right)
        self.btn_right.config(width=3)
        self.btn_right.grid(row=0, column=2, sticky=E)
        self.btn_right.config(background=APP_BUTTON_COLOR, foreground=APP_TEXT_COLOR)

        self.update_details()

    def page_left(self):
        """
        This triggers when the left arrow is clicked.
        """
        if self.pleft_callback():
            self.btn_right.config(state=NORMAL)
        else:
            self.btn_left.config(state=DISABLED)

        self.update_details()

    def page_right(self):
        """
        This triggers when the right arrow is clicked.
        """
        if self.pright_callback():
            self.btn_left.config(state=NORMAL)
        else:
            self.btn_right.config(state=DISABLED)

        self.update_details()

    def update_details(self):
        """
        This is a callable method to update the details of the page.
        This should be called when a page has been added, removed, or changed.
        """
        if self.cpages_callback() == 1:
            self.btn_left.config(state=DISABLED)
        else:
            self.btn_left.config(state=NORMAL)

        if self.cpages_callback() == self.tpages_callback():
            self.btn_right.config(state=DISABLED)
        else:
            self.btn_right.config(state=NORMAL)

        self.lbl_page.config(text=f"{self.cpages_callback()} / {self.tpages_callback()}")
