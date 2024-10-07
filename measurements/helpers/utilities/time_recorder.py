import time
# import fcntl
# import portalocker

def plaingpt_record(memory_time=None, planning_time=None, action_time=None):
    start_file_time = time.time()
    with open("/home/isolategpt/Desktop/SecGPT-IsolateGPT-AE/measurements/results/vanillagpt/running.txt", 'r') as f:
        # portalocker.lock(f, portalocker.LOCK_SH)
        # fcntl.flock(f, fcntl.LOCK_EX)
        data = f.read()
        # fcntl.flock(f, fcntl.LOCK_UN) 
    question, results_path, current_memory_time, current_planning_time, current_action_time, current_file_time = data.strip().split(":")
        
    
    if memory_time:
        current_memory_time = float(current_memory_time) + memory_time
    if planning_time:
        current_planning_time = float(current_planning_time) + planning_time
    if action_time:
        current_action_time = float(current_action_time) + action_time
        
    record_file_time = time.time() - start_file_time
    current_file_time = float(current_file_time) + record_file_time
        
    with open("/home/isolategpt/Desktop/SecGPT-IsolateGPT-AE/measurements/results/vanillagpt/running.txt", 'w') as f:
        # portalocker.lock(f, portalocker.LOCK_EX)
        # fcntl.flock(f, fcntl.LOCK_EX)
        f.write(":".join([question, results_path, str(current_memory_time), str(current_planning_time), str(current_action_time), str(current_file_time)])) 
        # fcntl.flock(f, fcntl.LOCK_UN) 
        # portalocker.unlock(f)  

    return question, results_path



def secgpt_record(hub_memory_time=None, hub_planning_time=None, spoke_init_time=None, spoke_memory_time=None, spoke_total_time=None, spoke_action_time=None, adt_hub_memory_time=None):
    start_file_time = time.time()
    with open("/home/isolategpt/Desktop/SecGPT-IsolateGPT-AE/measurements/results/isolategpt/running.txt", 'r') as f:
        # portalocker.lock(f, portalocker.LOCK_SH)
        # fcntl.flock(f, fcntl.LOCK_EX)
        data = f.read()
        # fcntl.flock(f, fcntl.LOCK_UN) 
    question, results_path, current_hub_memory_time, current_hub_planning_time, current_spoke_init_time, current_spoke_memory_time, current_spoke_total_time, current_spoke_action_time, current_adt_hub_memory_time, current_file_time = data.strip().split(":")
    
    if hub_memory_time:
        # print("hub_memory_time", hub_memory_time)
        current_hub_memory_time = float(current_hub_memory_time) + hub_memory_time
        
    if hub_planning_time:
        # print("hub_planning_time", hub_planning_time)
        current_hub_planning_time = float(current_hub_planning_time) + hub_planning_time
    
    if spoke_init_time:
        # print("spoke_init_time", spoke_init_time)
        current_spoke_init_time = float(current_spoke_init_time) + spoke_init_time
    
    if spoke_memory_time:
        # print("spoke_memory_time", spoke_memory_time)
        current_spoke_memory_time = float(current_spoke_memory_time) + spoke_memory_time
    
    if spoke_total_time:
        # print("spoke_total_time", spoke_total_time)
        current_spoke_total_time = float(current_spoke_total_time) + spoke_total_time
       
    if spoke_action_time:
        # print("spoke_action_time", spoke_action_time)
        current_spoke_action_time = float(current_spoke_action_time) + spoke_action_time
    
    if adt_hub_memory_time:
        # print("adt_hub_memory_time", adt_hub_memory_time)
        current_adt_hub_memory_time = float(current_adt_hub_memory_time) + adt_hub_memory_time
    
    record_file_time = time.time() - start_file_time
    current_file_time = float(current_file_time) + record_file_time
        
    with open("/home/isolategpt/Desktop/SecGPT-IsolateGPT-AE/measurements/results/isolategpt/running.txt", 'w') as f:
        # portalocker.lock(f, portalocker.LOCK_EX)
        # fcntl.flock(f, fcntl.LOCK_EX)
        f.write(":".join([question, results_path, str(current_hub_memory_time), str(current_hub_planning_time), str(current_spoke_init_time),str(current_spoke_memory_time), str(current_spoke_total_time), str(current_spoke_action_time), str(current_adt_hub_memory_time), str(current_file_time)])) 
        # fcntl.flock(f, fcntl.LOCK_UN) 
        # portalocker.unlock(f)  

    return question, results_path
