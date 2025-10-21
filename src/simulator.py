import random
from datetime import datetime, timedelta
from typing import List

import data
from call import Call
from data_load import append_call_to_file
from index import add_call_sorted
from popularity_graph import update_on_call


def run_overload_simulation(num_calls: int = 1000) -> None:

    print(f"\n{'='*60}")
    print(f"STARTING OVERLOAD SIMULATION: {num_calls} calls")
    print(f"{'='*60}\n")
    
    all_numbers = list(data.phonebook.keys())
    
    if len(all_numbers) < 2:
        print("[ERROR] Need at least 2 contacts in phonebook to simulate calls.")
        return
    
    total_generated = 0
    successful_calls = 0
    blocked_calls = 0
    
    current_time = datetime.now()
    
    print("Generating calls...", end="", flush=True)
    
    for i in range(num_calls):
        total_generated += 1
        
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
        
        call_time = current_time + timedelta(seconds=i * 0.06)
        
        call = Call(
            caller=caller,
            callee=callee,
            start=call_time,
            duration=duration
        )
        
        add_call_sorted(call, data.calls, data.call_index)
        update_on_call(call)
        
        append_call_to_file(call)
        
        successful_calls += 1
    
    print(" Done!\n")
    
    print(f"{'='*60}")
    print("SIMULATION COMPLETE")
    print(f"{'='*60}")
    print(f"Total calls generated:  {total_generated}")
    print(f"Successful (OK) calls:  {successful_calls}")
    print(f"Blocked calls:          {blocked_calls}")
    print(f"{'='*60}\n")
