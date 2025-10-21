from data_load import parse_call_line, append_call_to_file
from call import Call
import data
from popularity_graph import update_on_call
from index import add_call_sorted

def call_from_file(filepath_callsim, blocked_nums):
	blocked_set = blocked_nums
	total = 0
	skipped = 0
	processed = 0
	with open(filepath_callsim, 'r', encoding='utf-8') as f:
		for line_num, line in enumerate(f, start=1):
			try:
				result = parse_call_line(line)
				if result is None:
					continue
				caller, callee, timestamp, duration_secs = result
				if caller in blocked_set or callee in blocked_set:
					print(f"[BLOCKED] Skipping call at line {line_num}: {caller} → {callee} (blocked number)")
					skipped += 1
					continue
				call = Call(caller, callee, timestamp, duration_secs)
				print(f"[OK] {call}")
				add_call_sorted(call, data.calls, data.call_index)
				update_on_call(call)
				append_call_to_file(call)
				processed += 1
			except Exception as e:
				print(f"[ERROR] Skipping line {line_num}: {e}")
				skipped += 1
			total += 1
	print(f"\nSummary: Processed {processed} calls, Skipped {skipped} calls (blocked or error), Total lines: {total}")

