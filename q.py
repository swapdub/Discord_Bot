from validation import validate
class Q(validate):
    def __init__(self) -> None:
        super().__init__()
        # thinking of making 1 Q instance for each server
        self.music_q = []
        pass

    def build_entry(self):
        pass

    def add_to_queue(self):
        pass