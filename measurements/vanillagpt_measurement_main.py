from helpers.utilities.setup_envoironment import setup_environment
from helpers.configs.configuration import Configs
import json
import multiprocessing
import time
import os
import csv

from langchain_benchmarks import registry

import redis

import sys
from tqdm import tqdm


def main(user_id, task, debug=True, functionalities_path=None, test_queries=None):
    r = redis.Redis(host='localhost', port=6379, db=0) #Configs.db_port
    r.flushall()
    # Get the mode from the configuration file
    Configs.set_debug_mode(debug)
    Configs.set_user_id(user_id)
    
    if functionalities_path:
        Configs.set_functionalities_path(functionalities_path)
    
    # Set up all necessary API_KEY
    setup_environment()
    
    # Initialize Hub
    from vanillagpt.vanillagpt_measurement import PlainGPT 
    plaingpt = PlainGPT(task)
    results = dict()
    
    if debug:  
        for question in test_queries:
            response = plaingpt.query_process(question) 
            results[question] = response
        
    else:
        while True:
            query = input("Message SecGPT (enter 'exit' to end the conversation)...")
            if query.lower() == "exit":
                break
            plaingpt.query_process(query)
            
    return results

def get_dataset_questions(path):
    queries = []

    if path.endswith('.csv'):
        with open(path, 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                query = row[0]
                queries.append(query)
        queries = queries[1:]
    
    else:
        with open(path, 'r') as f:
            data = json.load(f)
        for item in data:
            query = item["inputs"]
            queries.append(query['question'])
    return queries


if __name__=='__main__':    
    
    configs_path = "/home/isolategpt/Desktop/SecGPT-IsolateGPT-AE/measurements/data/relational.json"
    
    with open(configs_path, 'r') as f:
        configs = json.load(f)
    
    dataset_path = configs["dataset_path"]
    test_queries = get_dataset_questions(dataset_path) #["Is it likely that Donna is awake right now?"]


    task_name = configs["task_name"]
    task = registry[task_name]
    
    
    plaingpt_results_dir = configs["plaingpt_results_dir"]
    
    run_time_results_path = os.path.join(plaingpt_results_dir, "runtime.csv") 
    with open(run_time_results_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Question", "Memory", "Planning", "Execution", "Total"])
    

    pbar = tqdm(total=len(test_queries), desc="Processing queries", ncols=100, file=sys.stdout)


    for question in test_queries:

        running_query_path = "/home/isolategpt/Desktop/SecGPT-IsolateGPT-AE/measurements/results/vanillagpt/running.txt"
        with open(running_query_path, 'w') as f:
            f.write(question+":"+plaingpt_results_dir+":0:0:0:0")
            
        if task.name == "Tool Usage - Typewriter (26 tools)" or task.name == "Tool Usage - Typewriter (1 tool)":
            question = task.instructions+ ": "+question
        
        start_time = time.time()
        
        main_process = multiprocessing.Process(target=main, args=('0', task, True, configs_path, [question]))
        main_process.start()
        main_process.join()
        
        if main_process.is_alive():
            main_process.terminate()
            main_process.join()

        total_runtime = time.time() - start_time
        
        
        with open("/home/isolategpt/Desktop/SecGPT-IsolateGPT-AE/measurements/results/vanillagpt/running.txt", 'r') as f:
            data = f.read()
            question, results_path, memory_time, planning_time, action_time, file_time = data.strip().split(":")  
            
        total_runtime = total_runtime - float(file_time)
        
        with open(run_time_results_path, 'a', newline='') as f:
            writer = csv.writer(f)            
            writer.writerow([question, memory_time, planning_time, action_time, total_runtime])
        
        pbar.update(1)
    
    pbar.close()

