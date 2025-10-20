from __future__ import annotations
import time
from datetime import datetime
from typing import Optional

from call import Call
import data
from data_load import normalize_phone
from index import add_call_sorted
from popularity_graph import update_on_call
from nonblocking_process import KeyboardThread



def _format_mmss(seconds: int) -> str:
	m, s = divmod(max(0, int(seconds)), 60)
	return f"{m:02d}:{s:02d}"


def start_live_call(caller: str, callee: str) -> Optional[Call]:
	"""
	Start a live call simulation between caller and callee using a non-blocking
	keyboard input thread. The call starts now and ends when the user hits Enter.

	Flow per TODO:
	1) Normalize and check if either number is blocked → if so, print [BLOCKED] and exit.
	2) Start timing; when finished, create Call and:
	   - update global calls (sorted) and per-number index
	   - update popularity graph
	"""
	caller_num = normalize_phone(caller)
	callee_num = normalize_phone(callee)

	# 1) Blocked check
	if caller_num in data.blocked or callee_num in data.blocked:
		print(f"[BLOCKED] Cannot start call: {caller_num} → {callee_num} (blocked number)")
		return None

	start_dt = datetime.now()
	start_ts = time.time()
	print(f"Starting live call: {caller_num} → {callee_num}")
	print("Press Enter to end the call…")

	# Use a simple flag set by the keyboard thread callback
	done = {"value": False}

	def on_key(_inp: str):
		# We end the call on first input (Enter)
		done["value"] = True

	# Launch the non-blocking keyboard listener
	KeyboardThread(on_key)

	# Show a tiny ticking timer until user ends the call
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
	# 2) Update data structures and graph
	add_call_sorted(call, data.calls, data.call_index)
	update_on_call(call)

	print(f"[OK] {call}")
	return call


def prompt_and_start_live_call() -> Optional[Call]:
	"""
	Interactive wrapper to prompt for caller/callee and then start the live call.
	"""
	try:
		caller = input("Enter caller number: ").strip()
		callee = input("Enter callee number: ").strip()
		return start_live_call(caller, callee)
	except KeyboardInterrupt:
		print("\nCancelled.")
		return None

