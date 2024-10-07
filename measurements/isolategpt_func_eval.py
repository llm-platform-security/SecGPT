
import os
from helpers.utilities.setup_envoironment import setup_environment


from langchain_benchmarks import registry
from langsmith.client import Client
from langchain_benchmarks import clone_public_dataset
from langchain.schema import AgentAction, AgentFinish, OutputParserException

import uuid
import pickle
import re

import json

# Set up all necessary API_KEY
setup_environment()

experiment_uuid = uuid.uuid4().hex[:4]

configs_path = "/home/isolategpt/Desktop/SecGPT-IsolateGPT-AE/measurements/data/relational.json"

with open(configs_path, 'r') as f:
    configs = json.load(f)

task_name = configs["task_name"]
task = registry[task_name]

results_dir = configs["secgpt_results_dir"]

results = dict()
files = os.listdir(results_dir)
for file in files:
    if file == "runtime.csv" or file == "0" or file == "1" or file == "2" or file == "runtime_test.csv" or file == "runtime_test_test.csv":
        continue
    path = os.path.join(results_dir, file)
    with open(path, 'rb') as f:
        data = pickle.load(f) # pickle
    results[file] = data


for item in results:

    # convert the results[item] to a dictionary from string
    # results[item] = json.loads(results[item])
    intermediate_steps = results[item]['intermediate_steps']
    actual_steps = []
    for action, _ in intermediate_steps:
        if action.tool == "message_spoke":
            match = re.search(r"'input':\s*['\"]([^'\"\(]+)\(", action.tool_input)
            if match:
                actual_tool = match.group(1)
                action.tool = actual_tool
        actual_steps.append((action, _))
        
    results[item] = {'output': results[item]['output'], 'intermediate_steps': actual_steps}


def my_model(inputs):
    question = inputs['question']
    return results[question]


model = "gpt-4"
client = Client()
clone_public_dataset(task.dataset_id, dataset_name=task.name) 
test_run = client.run_on_dataset(
    dataset_name=task.name,
    llm_or_chain_factory=my_model,
    evaluation=task.get_eval_config(),
    verbose=True,
    project_name=f"relational-{model}-{experiment_uuid}", #multiverse-math
    tags=[model],
    project_metadata={
        "model": model,
        "arch": "isolategpt",
        "id": experiment_uuid,
    },
)
