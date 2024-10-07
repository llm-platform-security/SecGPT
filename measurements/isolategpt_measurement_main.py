import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

from helpers.utilities.setup_envoironment import setup_environment
from helpers.configs.configuration import Configs
import json

from langchain_benchmarks import registry

import multiprocessing
import time
import csv
import os

import redis

import sys
from tqdm import tqdm



def main(user_id, task, debug=True, functionalities_path=None, test_queries=None):
    r = redis.Redis(host='localhost', port=6379, db=0) #Configs.db_port
    r.flushall()
    # Get the mode from the configuration file
    Configs.set_debug_mode(False) #debug
    Configs.set_user_id(user_id)
    
    if functionalities_path:
        Configs.set_functionalities_path(functionalities_path)
    
    # Set up all necessary API_KEY
    setup_environment()
    
    # Initialize Hub
    from hub.hub_measurement import Hub
    hub = Hub(task)
    results = dict()
    
    if debug:  
        for question in test_queries:
            response = hub.query_process(question) 
            results[question] = response
        
    else:
        while True:
            query = input("Message SecGPT (enter 'exit' to end the conversation)...")
            if query.lower() == "exit":
                break
            hub.query_process(query)
            
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
    secgpt_results_dir = configs["secgpt_results_dir"]
    task_name = configs["task_name"]
    task = registry[task_name]
    
    test_queries = get_dataset_questions(dataset_path) #["dictionary"], 
    
    
    # "do bob and alice live in the same city?"
    run_time_results_path = os.path.join(secgpt_results_dir, "runtime.csv") 
    with open(run_time_results_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Question", "Hub_Memory", "Hub_Planning", "Spoke_Memory", "Spoke_Planning", "Spoke_Execution", "Total"])

    pbar = tqdm(total=len(test_queries), desc="Processing queries", ncols=100, file=sys.stdout)

    for question in test_queries:

        # question = query['question']
        running_query_path = "/home/isolategpt/Desktop/SecGPT-IsolateGPT-AE/measurements/results/isolategpt/running.txt"
        with open(running_query_path, 'w') as f:
            f.write(question+":"+secgpt_results_dir+":0:0:0:0:0:0:0:0")

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


        with open("/home/isolategpt/Desktop/SecGPT-IsolateGPT-AE/measurements/results/isolategpt/running.txt", 'r') as f:
            data = f.read()
            question, results_path, hub_memory_time, hub_planning_time, spoke_init_time, spoke_memory_time, spoke_total_time, spoke_action_time, adt_hub_memory_time, file_time = data.strip().split(":")
            
            # Convert all variables except question and results_path to float
            hub_memory_time = float(hub_memory_time)
            hub_planning_time = float(hub_planning_time)
            spoke_init_time = float(spoke_init_time)
            spoke_memory_time = float(spoke_memory_time)
            spoke_total_time = float(spoke_total_time)
            spoke_action_time = float(spoke_action_time)
            adt_hub_memory_time = float(adt_hub_memory_time)
            file_time = float(file_time)

        total_runtime = total_runtime - file_time
        spoke_planning_time = spoke_total_time - spoke_action_time - spoke_memory_time - spoke_init_time - adt_hub_memory_time

        hub_memory_time = hub_memory_time + adt_hub_memory_time
        
        with open(run_time_results_path, 'a', newline='') as f:
            writer = csv.writer(f)            
            writer.writerow([question, hub_memory_time, hub_planning_time, spoke_memory_time, spoke_planning_time, spoke_action_time, total_runtime]) 

        pbar.update(1)
    
    pbar.close()
