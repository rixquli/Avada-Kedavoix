class UIEventListener:
    def __init__(self, eventCallback):
        self.eventCallback = eventCallback

    def handle_event(self, event):
        self.enventCallback(event)
