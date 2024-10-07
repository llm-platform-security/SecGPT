
import os

from helpers.utilities.setup_envoironment import setup_environment

from langchain_benchmarks import registry
from langsmith.client import Client
from langchain_benchmarks import clone_public_dataset

import uuid
import pickle

import json

# Set up all necessary API_KEY
setup_environment()

experiment_uuid = uuid.uuid4().hex[:4]


configs_path = "/home/isolategpt/Desktop/SecGPT-IsolateGPT-AE/measurements/data/relational.json"

with open(configs_path, 'r') as f:
    configs = json.load(f)

task_name = configs["task_name"]
task = registry[task_name]

results_dir = configs["plaingpt_results_dir"]


results = dict()
files = os.listdir(results_dir)
for file in files:
    if file == "runtime.csv" or file == '0' or file == "1" or file == "-1" or file == "runtime_test.csv" or file == "runtime_test_test.csv":
        continue
    path = os.path.join(results_dir, file)
    with open(path, 'rb') as f:
        data = pickle.load(f)
    results[file] = data

for item in results:
    results[item] = {'output': results[item]['output'], 'intermediate_steps': results[item]['intermediate_steps']}

def my_model(inputs):
    question = inputs['question']
    return results[question]
    

model = "gpt-4"
client = Client()
clone_public_dataset(task.dataset_id, dataset_name=task.name) 
test_run = client.run_on_dataset(
    dataset_name=task.name,
    llm_or_chain_factory=my_model, #agent_factory,
    evaluation=task.get_eval_config(),
    verbose=True,
    project_name=f"relational-{model}-{experiment_uuid}",
    tags=[model],
    project_metadata={
        "model": model,
        "arch": "vanillagpt",
        "id": experiment_uuid,
    },
)

