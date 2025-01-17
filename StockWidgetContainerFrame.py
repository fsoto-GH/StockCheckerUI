from csv import DictReader
from tkinter import *

from Constants import STK_WDT_VGAP, AUTO_ATC, BROWSER_ONLY, NOTHING, APP_BACKGROUND_COLOR, WIDGETS_P_THREAD
from StockWidget import StockWidget
from TrackedItem import BBTrackedItem, TrackedItem


class StockWidgetContainerFrame(Frame):
    """
    This widget is a StockWidget container.
    """

    def __init__(self, master=None):
        super(StockWidgetContainerFrame, self).__init__(master)
        self.config(background=APP_BACKGROUND_COLOR)
        self.widgets = []
        self.__curr_page = 1
        self.load_widgets()
        self.display()

    def get_curr_page(self):
        """
        :returns: the current page being displayed
        """
        return self.__curr_page

    def load_widgets(self):
        """
        This method loads all the items being tracked and listed in the
        trackedItems.txt.
        """
        with open("trackedItems.txt") as f:
            csv_reader = DictReader(f, delimiter='\t')
            for item_line in csv_reader:
                try:
                    if item_line['is_bb'].lower() == 'y':
                        # for a BB item, a path takes place of the web_url
                        item = BBTrackedItem(item_line['p_name'], item_line['api_url'],
                                             item_line['web_url'], item_line['x_path'])
                    else:
                        item = TrackedItem(item_line['p_name'], item_line['api_url'],
                                           item_line['web_url'], item_line['x_path'])

                    if item_line['launch_mode'] == AUTO_ATC:
                        launch_mode = AUTO_ATC
                    elif item_line['launch_mode'] == BROWSER_ONLY:
                        launch_mode = BROWSER_ONLY
                    else:
                        launch_mode = NOTHING

                    do_beep = item_line['do_beep'] == 'y'
                    do_double = item_line['do_double'] == 'y'
                    do_email = item_line['do_email'] == 'y'
                    freq = int(item_line['freq'])
                    widget = StockWidget(self, item, self.remove_update, launch_mode=launch_mode,
                                         freq=freq, do_beep=do_beep, do_double=do_double,
                                         do_email=do_email)
                    self.widgets.append(widget)
                except Exception as e:
                    print(f"Error parsing: {item_line}")
                    print(e)

    def add_widget(self, item: TrackedItem):
        """
        This method adds a particular item to the widgets.

        :param item: item to append a tracker for
        """
        self.widgets.append(StockWidget(self, item, self.remove_update))
        self.master.update_content()
        self.remove_widgets()
        self.display()

    def remove_update(self, item):
        """
        This method removes a particular item and then adjusts the
        page being views and pages.

        :param item: item to append a tracker for
        """
        # remove widget from list and remove from grid
        self.widgets.remove(item)
        item.grid_forget()

        # check if there are no widgets on the current page (to change page)
        # also if there is any widgets to even display
        if len(self.visible_widgets()) == 0 and len(self.widgets) > 0:
            self.__curr_page -= 1

        self.remove_widgets()
        self.master.update_content()
        self.display()

    def remove_widgets(self):
        """
        This method removes all the visible StockWidget widgets.
        """
        for widget in self.visible_widgets():
            self.children[widget].grid_forget()

    def visible_widgets(self):
        """
        :return: all visible StockWidget widgets
        """
        return list(filter(lambda x: isinstance(self.children[x], StockWidget) and self.children[x].winfo_ismapped(),
                           self.children))

    def display(self):
        """
        This appends three StockWidgets belonging to the particular
        current page.
        """
        if 1 <= self.__curr_page <= self.total_pages():
            index = (self.__curr_page - 1) * WIDGETS_P_THREAD
            for i in range(index, index + WIDGETS_P_THREAD):
                if i < len(self.widgets):
                    self.widgets[i].grid(row=self.grid_size()[1], column=0, columnspan=2, pady=STK_WDT_VGAP)

    def total_pages(self):
        """
        This returns the total pages in the widget--given that three widgets
        are displayed at once.
        """
        return (len(self.widgets) // WIDGETS_P_THREAD + (1 if len(self.widgets) % WIDGETS_P_THREAD else 0)) or 1

    def has_left(self):
        """
        :return: whether there is a previous page
        """
        return 0 < self.__curr_page - 1

    def has_right(self):
        """
        :return: whether there is a next page
        """
        return self.__curr_page + 1 <= self.total_pages()

    def go_left(self):
        """
        This performs the logic for paging to the left.
        :return: whether going left is possible
        """
        if self.has_left():
            self.remove_widgets()
            self.__curr_page -= 1
            self.display()
            return True
        else:
            return False

    def go_right(self):
        """
        This performs the logic for paging to the right.
        :return: whether going right is possible
        """
        if self.has_right():
            self.remove_widgets()
            self.__curr_page += 1
            self.display()
            return True
        else:
            return False
