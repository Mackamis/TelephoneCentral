from datetime import datetime

def _format_mmss(seconds: int) -> str:
    minutes = seconds // 60
    sec = seconds % 60
    return f"{minutes:02d}:{sec:02d}"

class Call:
    def __init__(self, caller, callee, start, duration: int):
        self.caller = caller
        self.callee = callee
        self.start = start
        self.duration = int(duration)

    def format_duration(self, duration=None) -> str:
        if duration is None:
            duration = self.duration
        return _format_mmss(duration)

    def __repr__(self):
        return f"Call({self.caller} → {self.callee} at {self.start} for {self.format_duration()})"