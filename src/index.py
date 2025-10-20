from typing import List, Dict
from bisect import bisect_left, bisect_right, insort_right
from call import Call

def build_call_index(calls: List[Call]) -> Dict[str, List[Call]]:
    """
    Build an index mapping phone numbers to their sorted call history (by start time).
    Both incoming and outgoing calls are indexed.
    """
    index: Dict[str, List[Call]] = {}
    for call in calls:
        for number in [call.caller, call.callee]:
            if number not in index:
                index[number] = []
            index[number].append(call)

    return index

def get_calls_for_number(index: Dict[str, List[Call]], number: str) -> List[Call]:

    return index.get(number, [])

def get_calls_in_time_range(index: Dict[str, List[Call]], number: str, start_dt, end_dt) -> List[Call]:

    calls = index.get(number, [])

    left = bisect_left(calls, start_dt, key=lambda c: c.start)
    right = bisect_right(calls, end_dt, key=lambda c: c.start)
    return calls[left:right]

def add_call_sorted(call: Call, calls: List[Call], index: Dict[str, List[Call]]) -> None:
    """
    Insert a call into the global calls list (kept sorted by start) and update
    the per-number index lists for both caller and callee, also kept sorted.
    """
    # Insert into global sorted list
    if not calls or call.start >= calls[-1].start:
        calls.append(call)
    else:
        insort_right(calls, call, key=lambda c: c.start)

    # Insert into per-number index for caller and callee
    for number in (call.caller, call.callee):
        lst = index.setdefault(number, [])
        if not lst or call.start >= lst[-1].start:
            lst.append(call)
        else:
            insort_right(lst, call, key=lambda c: c.start)
