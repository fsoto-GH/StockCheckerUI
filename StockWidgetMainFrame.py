from tkinter import *

from Constants import APP_XPAD, APP_YPAD, STK_WDT_VGAP
from StockWidgetContainerFrame import StockWidgetContainerFrame
from StockWidgetPagingFrame import StockWidgetPagingFrame
from TrackedItem import BBTrackedItem


class StockWidgetMainFrame(Frame):
    def __init__(self, parent=None):
        """
        This is a widget that displays the status of a particular product.
        This is automatically added to the master on the given row.

        :param parent: the parent of the control
        """
        super().__init__(parent)
        self.grid(padx=APP_XPAD, pady=APP_YPAD)

        # content
        self.content = StockWidgetContainerFrame(self)
        self.content.grid(row=1, column=0, columnspan=2)

        # pager
        self.pager = StockWidgetPagingFrame(self, self.content.go_left, self.content.go_right,
                                            self.content.get_curr_page, self.content.total_pages)
        self.pager.config()
        self.pager.grid(row=0, column=1, sticky=E, pady=STK_WDT_VGAP)

        # testing button
        self.btn_test = Button(self, text="TEST", command=self.test)
        self.btn_test.grid(row=0, column=0)

    def update_content(self):
        self.pager.update_details()

    def test(self):
        p_name = "Ryzen 5 5600X"
        sku = '6438943'
        web_url = 'https://www.bestbuy.com/site/amd-ryzen-5-5600x-4th-gen-6-core-12-threads-unlocked-desktop-processor-with-wraith-stealth-cooler/6438943.p?skuId=6438943'
        x_path = '/html/body/div[3]/main/div[2]/div[3]/div[2]/div/div/div[14]/div[2]/div/div/div/button'

        item = BBTrackedItem(p_name, sku, web_url, x_path, )
        self.content.add_widget(item)


if __name__ == '__main__':
    t = StockWidgetMainFrame()
    t.pack()
    t.mainloop()
