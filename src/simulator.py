import random
import threading
import time
from datetime import datetime, timedelta

import data
from call import Call
from data_load import append_call_to_file
from index import add_call_sorted
from popularity_graph import update_on_call


def run_overload_simulation(duration_seconds = 60, enable_controls = True):

    print(f"\n{'='*60}")
    print(f"STARTING OVERLOAD SIMULATION")
    if enable_controls:
        print("Controls: [p]ause  [r]esume  [q]uit")
    print(f"{'='*60}\n")
    
    all_numbers = list(data.phonebook.keys())
    
    if len(all_numbers) < 2:
        print("[ERROR] Need at least 2 contacts in phonebook to simulate calls.")
        return
    
    total_generated = 0
    successful_calls = 0
    blocked_calls = 0

    sim_stats = {}

    def _bump_incoming(num, dur):
        st = sim_stats.setdefault(num, {"incoming_count": 0, "outgoing_count": 0, "incoming_duration": 0})
        st["incoming_count"] += 1
        st["incoming_duration"] += int(dur)

    def _bump_outgoing(num):
        st = sim_stats.setdefault(num, {"incoming_count": 0, "outgoing_count": 0, "incoming_duration": 0})
        st["outgoing_count"] += 1


    start_wall = datetime.now()
    current_time = start_wall.replace(second=0, microsecond=0)

    start_mono = time.monotonic()
    paused_total = 0.0
    paused_started: float | None = None

    paused = {"value": False}
    stop = {"value": False}

    def _input_loop():
        while True:
            try:
                cmd = input().strip().lower()
            except EOFError:
                return
            if cmd == 'p':
                paused["value"] = True
                print("\n[PAUSED]")
            elif cmd == 'r':
                if paused["value"]:
                    print("[RESUMED]")
                paused["value"] = False
                if nonlocal_vars["paused_started"] is not None:
                    nonlocal_paused = time.monotonic() - nonlocal_vars["paused_started"]
                    nonlocal_vars["paused_total"] += nonlocal_paused
                    nonlocal_vars["paused_started"] = None
            elif cmd == 'q' or cmd == '':
                stop["value"] = True
                print("\n[STOP REQUESTED]")
                return

    nonlocal_vars = {"paused_total": paused_total, "paused_started": paused_started}

    if enable_controls:
        threading.Thread(target=_input_loop, name="sim-input", daemon=True).start()
    
    print("Generating calls...", end="", flush=True)
    
    i = 0
    while not stop["value"]:
        paused_total = nonlocal_vars["paused_total"]
        now_mono = time.monotonic()
        elapsed = now_mono - start_mono - paused_total
        if elapsed >= duration_seconds:
            break

        while paused["value"] and not stop["value"]:
            if nonlocal_vars["paused_started"] is None:
                nonlocal_vars["paused_started"] = time.monotonic()
            time.sleep(0.05)
        total_generated += 1
        i += 1
        
        if (i + 1) % 100 == 0:
            print(f" {i + 1}", end="", flush=True)
        
        caller = random.choice(all_numbers)
        callee = random.choice(all_numbers)
        
        while callee == caller:
            callee = random.choice(all_numbers)
        
        if caller in data.blocked or callee in data.blocked:
            blocked_calls += 1
            continue  

        duration = random.randint(10, 300)

        offset_sec = random.randint(0, max(0, duration_seconds - 1))
        call_time = current_time + timedelta(seconds=offset_sec)

        call = Call(
            caller=caller,
            callee=callee,
            start=call_time,
            duration=duration
        )

        add_call_sorted(call, data.calls, data.call_index)
        update_on_call(call)

        append_call_to_file(call)

        _bump_outgoing(caller)
        _bump_incoming(callee, duration)

        successful_calls += 1
    
    print(" Done!\n")

    total_incoming_duration = sum(st["incoming_duration"] for st in sim_stats.values())
    avg_duration_secs = (total_incoming_duration // successful_calls) if successful_calls else 0
    avg_h = avg_duration_secs // 3600
    avg_m = (avg_duration_secs % 3600) // 60
    avg_s = avg_duration_secs % 60


    scored = []
    for number, st in sim_stats.items():
        score = st["incoming_count"] * 2.0 + (st["incoming_duration"] / 60.0) + st["outgoing_count"] * 0.5
        scored.append((number, score))
    scored.sort(key=lambda x: x[1], reverse=True)
    top5 = scored[:5]

    print(f"{'='*60}")
    print("SIMULATION COMPLETE")
    print(f"{'='*60}")
    print(f"Total calls generated:  {total_generated}")
    print(f"Successful (OK) calls:  {successful_calls}")
    print(f"Blocked calls:          {blocked_calls}")
    print(f"Average duration (OK):  {avg_h:02d}:{avg_m:02d}:{avg_s:02d}")
    print("Top 5 popular numbers (this run):")
    if top5:
        for i, (num, score) in enumerate(top5, start=1):
            st = sim_stats.get(num, {"incoming_count": 0, "outgoing_count": 0, "incoming_duration": 0})
            print(f"  {i}. {num}  score={score:.2f}  in={st['incoming_count']} out={st['outgoing_count']} dur={st['incoming_duration']}s")
    else:
        print("  (none)")
    print(f"{'='*60}\n")
