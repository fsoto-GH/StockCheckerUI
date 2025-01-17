class TimeStamp:
    def __init__(self, time, call_num):
        self.time = time
        self.call_num = call_num

    @property
    def time(self):
        return self.__time

    @time.setter
    def time(self, v):
        self.__time = v

    @property
    def call_num(self):
        return self.__call_num

    @call_num.setter
    def call_num(self, v):
        self.__call_num = v
