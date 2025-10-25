import data
from index import get_calls_for_number
from data_load import normalize_phone


def _in_range(call, start_dt, end_dt):
    if start_dt and call.start < start_dt:
        return False
    if end_dt and call.start > end_dt:
        return False
    return True


def get_history_for(number, start_dt = None, end_dt = None):

    num = normalize_phone(number)
    calls = get_calls_for_number(data.call_index, num)
    result = []
    for c in calls:
        if not _in_range(c, start_dt, end_dt):
            continue
        direction = 'OUT' if c.caller == num else 'IN'
        result.append((c, direction))
    return result


def get_history_between(a, b, start_dt = None, end_dt = None):

    a_num = normalize_phone(a)
    b_num = normalize_phone(b)
    calls_a = get_calls_for_number(data.call_index, a_num)
    result = []
    for c in calls_a:
        if not _in_range(c, start_dt, end_dt):
            continue
        if (c.caller == a_num and c.callee == b_num) or (c.caller == b_num and c.callee == a_num):
            result.append(c)
    return result


def format_call(call, focus_number = None):

    tag = ""
    if focus_number is not None:
        num = normalize_phone(focus_number)
        tag = "[OUT]" if call.caller == num else "[IN]"
        tag += " "
    return f"{tag}{call.start} | {call.format_duration()} | {call.caller} → {call.callee}"


def prompt_and_show_history_for():

    try:
        number = input("Enter number: ").strip()
        hist = get_history_for(number)
        print("\nHistory:")
        for call, _direction in hist:
            print(format_call(call, focus_number=number))
        if not hist:
            print("  (no calls found)")
    except KeyboardInterrupt:
        print("\nCancelled.")


def prompt_and_show_history_between():

    try:
        a = input("Enter first number: ").strip()
        b = input("Enter second number: ").strip()
        hist = get_history_between(a, b)
        print("\nHistory between:")
        for call in hist:
            print(format_call(call))
        if not hist:
            print("  (no calls found)")
    except KeyboardInterrupt:
        print("\nCancelled.")
