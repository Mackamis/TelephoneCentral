from __future__ import annotations
import time
from datetime import datetime
from typing import Optional

from call import Call, _format_mmss
import data
from data_load import normalize_phone, append_call_to_file
from index import add_call_sorted
from popularity_graph import update_on_call
from nonblocking_process import KeyboardThread



def start_live_call(caller: str, callee: str) -> Optional[Call]:

	caller_num = normalize_phone(caller)
	callee_num = normalize_phone(callee)

	#Blocked check
	if caller_num in data.blocked or callee_num in data.blocked:
		print(f"[BLOCKED] Cannot start call: {caller_num} → {callee_num} (blocked number)")
		return None

	start_dt = datetime.now()
	start_ts = time.time()
	print(f"Starting live call: {caller_num} → {callee_num}")
	print("Press Enter to end the call…")

	done = {"value": False}

	def on_key(_inp: str):
		done["value"] = True

	KeyboardThread(on_key)

	last_shown = -1
	try:
		while not done["value"]:
			elapsed = int(time.time() - start_ts)
			if elapsed != last_shown:
				print(f"Duration: {_format_mmss(elapsed)}", end="\r", flush=True)
				last_shown = elapsed
			time.sleep(0.2)
	except KeyboardInterrupt:
		print("\nCancelled by user.")
		return None

	duration_secs = max(1, int(time.time() - start_ts))
	print("\nEnding call…")

	call = Call(caller_num, callee_num, start_dt, duration_secs)
	# Update data structures
	add_call_sorted(call, data.calls, data.call_index)
	update_on_call(call)
	
	# Append to calls.txt
	append_call_to_file(call)

	print(f"[OK] {call}")
	return call


def prompt_and_start_live_call() -> Optional[Call]:

	try:
		caller = input("Enter caller number: ").strip()
		callee = input("Enter callee number: ").strip()
		return start_live_call(caller, callee)
	except KeyboardInterrupt:
		print("\nCancelled.")
		return None

