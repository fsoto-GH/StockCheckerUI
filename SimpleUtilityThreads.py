import winsound
from threading import Thread


class BeepThread(Thread):
    def __init__(self, ms: int = 3000):
        super(BeepThread, self).__init__()
        self.daemon = True
        self.name = "beep-thread"
        self.ms = ms

    def run(self) -> None:
        winsound.Beep(3060, self.ms)


class EmailThread(Thread):
    def __init__(self, p_name, url):
        super(EmailThread, self).__init__()
        self.p_name = p_name
        self.daemon = True
        self.name = "email-thread"
        self.url = url

    def run(self) -> None:
        raise NotImplementedError()


class PushThread(Thread):
    def __init__(self, p_name, url):
        super(PushThread, self).__init__()
        self.p_name = p_name
        self.daemon = True
        self.name = "sms-thread"
        self.url = url

    def run(self) -> None:
        raise NotImplementedError()
