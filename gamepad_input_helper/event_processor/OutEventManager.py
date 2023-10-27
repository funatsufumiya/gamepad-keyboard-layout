from ..DebugState import DebugState

class OutEventManager:
    def __init__(self):
        self.out_events = []

    def add_event(self, event):
        self.out_events.append(event)

    def process_events(self):
        for oev in self.out_events:
            if DebugState.is_debug():
                print(f"{oev}")
            oev.execute()

        self.out_events.clear()