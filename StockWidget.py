import webbrowser
from datetime import datetime, timedelta
from threading import Thread
from tkinter import *

import requests
from selenium import webdriver
from selenium.common.exceptions import NoSuchWindowException, WebDriverException

import TrackedItem
from Constants import APP_LABEL_FONT, APP_TEXT_FONT
from Constants import BROWSER_ONLY, AUTO_ATC, NOTHING, HEADERS, APP_TEXT_COLOR
from Constants import SOLD_OUT, IN_STOCK, NOT_NEARBY, UNKNOWN, ERROR
from Constants import STEP_SIZE, SCALE_SKIP, SCALE_MIN, SCALE_MAX
from Constants import STK_WDT_BORCOL, STK_WDT_SLT_CLR, STK_WDT_FG
from Constants import WIDGET_VGAP, WIDGET_HGAP, BTN_WIDTH, STOCK_WIDTH, P_NAME_WIDTH, MESSAGE_WIDTH
from SimpleUtilityThreads import BeepThread, EmailThread, PushThread
from TimeStamp import TimeStamp
from Utilities import launch_automation_browser


class StockWidget(Frame):
    def __init__(self, parent, item: TrackedItem, remove_callback,
                 launch_mode: str = None, freq: int = None, do_beep: bool = None,
                 do_double: bool = None, do_email: bool = None):
        """
        This is a widget that displays the status of a particular product.
        This is automatically added to the master on the given row.

        :param parent: the parent of the control
        :param item: the item whose status is being displayed.
        """
        super().__init__(parent)
        self.config(padx=10, pady=10)
        self.config(highlightbackground=STK_WDT_BORCOL, highlightthickness=2)

        self.remove_callback = remove_callback
        self.item = item

        # this is the actual widget setup
        self.lbl_p_name = Label(self, text=item.p_name, anchor=W, font=APP_TEXT_FONT)
        self.lbl_p_name.config(width=P_NAME_WIDTH)
        self.lbl_p_name.bind('<Button-1>', lambda *args: webbrowser.open_new(self.item.web_url))

        self.lbl_stock = Label(self, text="---", anchor=W, font=APP_TEXT_FONT)
        self.lbl_stock.config(width=STOCK_WIDTH)

        self.lbl_message = Label(self, text="---", anchor=E, font=APP_TEXT_FONT)
        self.lbl_message.config(width=MESSAGE_WIDTH)

        self.btn_state = Button(self, text="Turn on", command=self.toggle_command, font=APP_TEXT_FONT)
        self.btn_state.config(width=BTN_WIDTH)

        self.btn_done = Button(self, text="Done", command=self.done_command, font=APP_TEXT_FONT)
        self.btn_done.config(width=BTN_WIDTH)

        self.do_beep = BooleanVar(value=True if do_beep is None else do_beep)
        self.pull_rate = IntVar(value=1 if freq is None else freq)
        self.l_method = StringVar(value=NOTHING if launch_mode is None else launch_mode)
        self.do_email = BooleanVar(value=True if do_email is None else do_email)
        self.do_double = BooleanVar(value=True if do_double is None else do_double)

        self.pull_scale = Scale(self, from_=SCALE_MIN, to=SCALE_MAX, tickinterval=SCALE_SKIP, orient=HORIZONTAL,
                                variable=self.pull_rate, command=self.step_size)

        # grid it all up
        # row 0
        self.btn_state.grid(row=0, column=0, padx=WIDGET_HGAP, pady=WIDGET_VGAP)
        self.btn_done.grid(row=0, column=1, padx=WIDGET_HGAP, pady=WIDGET_VGAP)

        self.lbl_p_name.grid(row=0, column=2, padx=WIDGET_HGAP, pady=WIDGET_VGAP)
        self.lbl_stock.grid(row=0, column=3, padx=WIDGET_HGAP, pady=WIDGET_VGAP)
        self.lbl_message.grid(row=0, column=4, padx=WIDGET_HGAP, pady=WIDGET_VGAP)

        # options
        # row 1 - control labels
        Label(self, text="LAUNCH MODE", font=APP_LABEL_FONT).grid(row=1, column=0, sticky=W)
        Label(self, text="OPTIONS", font=APP_LABEL_FONT).grid(row=1, column=1, sticky=W)
        Label(self, text="PULL FREQUENCY LIMITER (ms)", font=APP_LABEL_FONT).grid(row=1, column=2, columnspan=2,
                                                                                  sticky=W)
        self.pull_scale.grid(row=2, padx=WIDGET_HGAP, column=2, columnspan=5, rowspan=2, sticky=W + E)

        Checkbutton(self, text="Beep Alert", variable=self.do_beep, selectcolor=STK_WDT_SLT_CLR). \
            grid(row=2, column=1, padx=WIDGET_HGAP, pady=WIDGET_VGAP, sticky=W)
        Checkbutton(self, text="Email", variable=self.do_email, selectcolor=STK_WDT_SLT_CLR). \
            grid(row=3, column=1, padx=WIDGET_HGAP, pady=WIDGET_VGAP, sticky=W)
        Checkbutton(self, text="Double Click", variable=self.do_double, selectcolor=STK_WDT_SLT_CLR). \
            grid(row=4, column=1, padx=WIDGET_HGAP, pady=WIDGET_VGAP, sticky=W)

        Radiobutton(self, text="Automate ATC", variable=self.l_method, value=AUTO_ATC, selectcolor=STK_WDT_SLT_CLR,
                    fg=STK_WDT_FG).grid(row=2, column=0, padx=WIDGET_HGAP, pady=WIDGET_VGAP, sticky=W)
        Radiobutton(self, text="Only Website", variable=self.l_method, value=BROWSER_ONLY,
                    selectcolor=STK_WDT_SLT_CLR, fg=STK_WDT_FG).grid(row=3, column=0, padx=WIDGET_HGAP,
                                                                     pady=WIDGET_VGAP, sticky=W)
        Radiobutton(self, text="Do nothing", variable=self.l_method, value=NOTHING,
                    selectcolor=STK_WDT_SLT_CLR, fg=STK_WDT_FG).grid(row=4, column=0, padx=WIDGET_HGAP,
                                                                     pady=WIDGET_VGAP, sticky=W)
        self.btn_wait = Button(self, text="Wait clickable", command=self.retry_click)
        self.btn_wait.grid(row=4, column=2, sticky=W, padx=10)
        self.btn_wait.config(width=BTN_WIDTH)

        self.btn_ckout = Button(self, text="Checkout", command=lambda *args: webbrowser.open_new(self.item.ckout_url))
        self.btn_ckout.grid(row=4, column=3, sticky=W, padx=10)
        self.btn_ckout.config(width=BTN_WIDTH)

        self.process_msg = Label(self)
        self.process_msg.grid(row=1, column=4, sticky=E, padx=WIDGET_HGAP, pady=WIDGET_VGAP)

        self.__thread = None
        self.is_on = False
        self._browser = None

        self.___thread = None

    def retry_click(self):
        if self.__thread is None:
            self.btn_wait.config(state=DISABLED)
            self.___thread = Thread(target=self._retry_click)
            self.process_msg.config(text="Waiting to click...")
            self.___thread.start()
        else:
            self.btn_wait.config(state=NORMAL)
            self.___thread = None
            self.process_msg.config(text="")

    def _retry_click(self):
        if self._browser is None:
            return
        try:
            self.item.wait_click(self._browser, self.do_beep.get())
        except:
            pass

    @property
    def _browser(self):
        return self.__browser

    @_browser.setter
    def _browser(self, v: webdriver):
        self.__browser = v

    def step_size(self, x):
        x = int(x)
        if x % STEP_SIZE < STEP_SIZE // 2:
            self.pull_rate.set((x // STEP_SIZE) * STEP_SIZE)
        else:
            self.pull_rate.set((x // STEP_SIZE) * STEP_SIZE + STEP_SIZE)

    @property
    def is_on(self):
        return self.__is_on

    @is_on.setter
    def is_on(self, v):
        self.__is_on = v
        if self.__is_on:
            self.btn_state.config(text="Turn off", state=NORMAL)
        else:
            self.btn_state.config(text="Turn on", state=NORMAL)

    def toggle_command(self):
        self.is_on = not self.is_on
        if self.is_on:
            self.__thread = StockCheckerThread(self)
            # ensure that you cannot toggle until after the thread has been started
            # this is an edge case that occurs after terminating the thread and
            # immediately attempting to restart the thread
            self.btn_state.config(state=DISABLED)
            self.__thread.start()
            self.btn_state.config(state=NORMAL)
        else:
            self.terminate_thread()

    def terminate_thread(self):
        if self.__thread is not None:
            self.btn_state.config(state=DISABLED)
            self.btn_done.config(state=DISABLED)

            self.is_on = False
            self.__thread.join()
            self.__thread = None

            self.btn_state.config(state=NORMAL)
            self.btn_done.config(state=NORMAL)

    def done_command(self):
        self.terminate_thread()
        self.remove_callback(self)

    def reset(self):
        self.__thread = None
        self.__is_on = False
        self.btn_state.config(text="Turn on", state=NORMAL)
        self.btn_done.config(state=NORMAL)
        self.process_msg.config(text="")


class StockCheckerThread(Thread):
    """
    This class/thread is to be used as part of StockWidgetThread.
    """

    def __init__(self, widget: StockWidget):
        """
        This creates an instance of StockWidgetThread which takes a StockWidget.
        Upon starting this thread, the thread will perform stock checking on the StockWidget's item.
        It will report the changes to the appropriate labels.

        :param widget: The widget for which this thread will control.
        """
        super().__init__()
        self.widget = widget

        self.name = f"{self.widget.item.p_name}-thread"
        self.daemon = True

        self.last_timestamp = 0

    def run(self):
        import time

        check_count = 0
        curr_check = 0
        prev_suc_check = 0
        threads = []

        while True:
            color = APP_TEXT_COLOR

            if not self.widget.is_on:
                break

            try:
                time.sleep((self.widget.pull_rate.get() - (datetime.now() - curr_check).microseconds // 100) / 10_000)
            except:
                pass

            try:
                # get data from api
                curr_check = datetime.now()
                r = requests.get(self.widget.item.api_url, headers=HEADERS)

                # determines the time since the last update
                delta = curr_check - prev_suc_check if check_count else timedelta()
                msg = f'{check_count:>9} - {curr_check.strftime("%I:%M:%S %p")} [{delta.seconds:>2}:{delta.microseconds:>06}]'
                prev_suc_check = curr_check

                result = self.widget.item.api_condition(r.text)
                if result == SOLD_OUT:
                    color = 'RED'
                elif result == IN_STOCK:
                    color = 'GREEN'
                elif result == NOT_NEARBY:
                    color = 'YELLOW'
                elif result == UNKNOWN:
                    color = 'GRAY'

                status = result if result else ERROR

                if self.widget.is_on:
                    self.widget.lbl_message.config(text=msg)
                    self.widget.lbl_stock.config(text=status, fg=color)

                if status == IN_STOCK:
                    if self.widget.do_beep.get():
                        threads.append(BeepThread())

                    if self.widget.do_email.get():
                        threads.append(EmailThread(self.widget.item.p_name, self.widget.item.web_url))

                    for thread in threads:
                        thread.start()

                    if self.widget.l_method.get() == AUTO_ATC:
                        self.widget.btn_state.config(state=DISABLED)
                        self.widget.btn_done.config(state=DISABLED)

                        browser = launch_automation_browser(self.widget.item)

                        if self.widget.is_on:
                            self.widget.process_msg.config(text=f"Waiting for {'first' if self.widget.do_double.get() else ''} click...")
                        self.widget.item.wait_click(browser, self.widget.do_beep.get())

                        if self.widget.do_double.get():
                            time.sleep(.5)
                            if self.widget.is_on:
                                self.widget.process_msg.config(text="Waiting for second click...")
                            self.widget.item.wait_click(browser, self.widget.do_beep.get())

                        self.widget._browser = browser

                        self.widget.btn_state.config(state=NORMAL)
                        self.widget.btn_done.config(state=NORMAL)
                    elif self.widget.l_method.get() == BROWSER_ONLY:
                        webbrowser.open_new(self.widget.item.web_url)

                    for thread in threads:
                        thread.join()

                    break

                check_count += 1
            except (NoSuchWindowException, WebDriverException):
                print('Selenium browser gone.')
                break
            except Exception as e:
                print(type(e))
                if self.widget.is_on:
                    self.widget.lbl_stock.config(text='ERROR')
                print(f"{self.widget.item.p_name}: {e}")
                if self.last_timestamp:
                    ex = f"{'':12}{self.last_timestamp.call_num} -> " \
                         f"{check_count} ({self.last_timestamp.call_num - check_count})"
                    print(ex)
                self.last_timestamp = TimeStamp(datetime.now(), check_count)
        # reset bool to indicate a finished run
        if self.widget.is_on:
            self.widget.reset()
