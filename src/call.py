from datetime import datetime

def _format_mmss(seconds: int) -> str:
    minutes = seconds // 60
    sec = seconds % 60
    return f"{minutes:02d}:{sec:02d}"

class Call:
    def __init__(self, caller, callee, start, duration_seconds: int):
        self.caller = caller
        self.callee = callee
        self.start = start
        self.duration = int(duration_seconds)

    def format_duration(self) -> str:
        return _format_mmss(self.duration)

    def __repr__(self):
        return f"Call({self.caller} → {self.callee} at {self.start} for {self.format_duration()})"