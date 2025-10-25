from bisect import bisect_left, bisect_right, insort_right


def build_call_index(calls):

    index = {}
    for call in calls:
        for number in [call.caller, call.callee]:
            if number not in index:
                index[number] = []
            index[number].append(call)

    return index


def get_calls_for_number(index, number):

    return index.get(number, [])


def get_calls_in_time_range(index, number, start_dt, end_dt):

    calls = index.get(number, [])

    left = bisect_left(calls, start_dt, key=lambda c: c.start)
    right = bisect_right(calls, end_dt, key=lambda c: c.start)
    return calls[left:right]


def add_call_sorted(call, calls, index) -> None:

    if not calls or call.start >= calls[-1].start:
        calls.append(call)
    else:
        insort_right(calls, call, key=lambda c: c.start)

    for number in (call.caller, call.callee):
        lst = index.setdefault(number, [])
        if not lst or call.start >= lst[-1].start:
            lst.append(call)
        else:
            insort_right(lst, call, key=lambda c: c.start)
