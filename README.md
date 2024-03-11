# SecGPT

SecGPT is an LLM-based system that secures the execution of LLM apps via isolation. The key idea behind SecGPT is to isolate the execution of apps and to allow interaction between apps and the system only through well-defined interfaces with user permission. SecGPT can defend against multiple types of attacks, including app compromise, data stealing, inadvertent data exposure, and uncontrolled system alteration. The architecture of SecGPT is shown in the figure below. Learn more about SecGPT in our [paper](https://arxiv.org/abs/2403.04960).


<p align="center"><img src="figure/architecture.bmp" alt="workflow" width="400"></p>

We develop SecGPT using [LangChain](https://github.com/langchain-ai/langchain), an open-source LLM framework. We use LangChain because it supports several LLMs and apps and can be easily extended to include additional LLMs and apps. We use [Redis](https://redis.io/) database to keep and manage memory. We implement SecGPT as a personal assistant chatbot, which the users can communicate with using text messages. 

<a href='https://arxiv.org/abs/2403.04960'><img src='https://img.shields.io/badge/Paper-Arxiv-red'></a> 
[![LICENSE](https://img.shields.io/badge/license-MIT-green?style=flat-square)](LICENSE)

## Table of Contents
- [SecGPT](#secgpt)
  - [Installation](#installation)
  - [Setup](#setup)
  - [Running](#Running)
  - [Case Studies](#case-studies)
  - [Contribution and Support](#contribution-and-support)
  - [Research Team](#research-team)
  - [Citation](#citation)
  - [Project Structure](#project-structure)


## Installation
To set up the environment, we suggest using Conda to install all necessary packages. Conda installation instructions can be found [here](https://docs.anaconda.com/free/miniconda/miniconda-install/). The following setup assumes Conda is installed and is running on a Linux/macOS system (though Windows should work too).

First, create the conda environment: 

```sh
conda create -n secgpt python=3.9
```

and activate the conda environment:

```sh
conda activate secgpt
```

Next, clone the SecGPT repository and use pip to install the required packages:

```sh
git clone https://github.com/llm-platform-security/SecGPT
cd SecGPT
pip install -r requirements.txt
```

## Setup
Before running SecGPT, you need to set the API key for the used LLM (GPT4 by default), select apps to enable, and authorize apps that require authorization. 

First, specify your API key for the LLM in `data/env_variables.json`:

```json
{
    "OPENAI_API_KEY" : ""
}
```
Next, specify the root path of the local SecGPT repository with an absolute path in `helpers/configs/configuration.py`:

```python
root_path = ""
```

Then, set enabled functionalities/toolkits/annotations in `data/functionalities.json`. For example, if you want to enable Google Drive and Gmail App, select the corresponding functionality names from `available_functionalities` and specify them in `installed_functionalities`.

```json
{
    "installed_functionalities": [
        "google_drive_retrieve"
    ]
}
```

Finally, some apps require authorization. To authorize these apps, please follow their documentation. For example, see the steps for setting up Google Drive [here](https://python.langchain.com/docs/integrations/retrievers/google_drive) and Gmail [here](https://python.langchain.com/docs/integrations/toolkits/gmail). Note that the `credentials.json` file should be stored at the `data/credentials.json` path. For more app settings, such as token storage path, please refer to `helpers/configs/configuration.py`.

**Troubleshooting:** If you encounter the `NameError: name 'Callbacks' is not defined` when using the Google Drive tool, please modify the function definition of `get_relevant_documents` in the library `...langchain_core/retrievers.py`:
```python
def get_relevant_documents(
    self,
    query: str,
    *,
    callbacks: Any = None, # Replace "Callbacks" with "Any"
    tags: Optional[List[str]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    run_name: Optional[str] = None,
    **kwargs: Any,
) -> List[Document]:
```

**Add More Apps:** If you want to add more apps, please initialize them in `helpers/tools/tool_importer.py`, add their specifications to `helpers/tools/specifications`, and enable them in `data/functionalities.json`. For more details, please refer to the code and settings of existing apps.

**Advanced Setup:** We isolate the execution of the spokes and the hub by running them in separate processes. We leverage the seccomp (for Linux) and setrlimit (see [here](https://healeycodes.com/running-untrusted-python-code) for more details) system utilities to restrict access to system calls and set limits on the resources a process can consume. Specifically, we allow access to needed system calls and limit the CPU time, maximum virtual memory size, and maximum size of files that can be created, within a process. Additionally, the network requests from an app are restricted to their root domain (i.e., eTLD+1). All these settings can be modified in `helpers/sandbox/sandbox.py`.

## Running
To use SecGPT, you can simply run the `secgpt_main.py` script, where you can set the user ID and debug mode in the `main` function.

```python
main('0', debug=False) # user id 0, normal running mode
```

Similarly, you can also use a baseline non-isolated system that we developed, named VanillaGPT by running the `vanillagpt_main.py` script.

## Case Studies
SecGPT's goals are to: 
1. Protect the apps from getting compromised by/through other apps 
2. Protect stealing of app and system data by/through other apps
3. Avoid the ambiguity and imprecision of natural language inadvertently compromising app functionality
4. Avoid the ambiguity and imprecision of natural language inadvertently exposing user data

To demonstrate protection against these attacks, we implement them in four case studies. For each case study, you can run `python secgpt_case_studies.py` and `python vanillagpt_case_studies.py` and compare their intermediate steps and outputs. For example, you can run the `secgpt_case_studies` script, which prompts you to select the case study you want to run:

```plaintext
Select a case study to run:
1: App Compromise
2: Data Stealing
3: Inadvertent Data Exposure
4: Uncontrolled System Alteration
Enter your choice (1-4):
```  
You can make a selection accordingly and check the output of the case study.

## Contribution and Support
We welcome contributions to the project, e.g., through pull requests. For issues and feature requests, please open a GitHub issue. Please also feel free to reach out to us if you have questions about the project and if you would like to contribute. 

## Research Team 
[Yuhao Wu](https://yuhao-w.github.io) (Washington University in St. Louis)  
[Franziska Roesner](https://www.franziroesner.com/) (University of Washington)  
[Tadayoshi Kohno](https://homes.cs.washington.edu/~yoshi/) (University of Washington)  
[Ning Zhang](https://cybersecurity.seas.wustl.edu/) (Washington University in St. Louis)  
[Umar Iqbal](https://umariqbal.com) (Washington University in St. Louis)  

## Citation
```plaintext
@article{wu2024secgpt,
  title={{SecGPT: An Execution Isolation Architecture for LLM-Based Systems}}, 
  author={Wu, Yuhao and Roesner, Franziska and Kohno, Tadayoshi and Zhang, Ning and Iqbal, Umar},
  journal={arXiv preprint arXiv:2403.04960},
  year={2024},
}
```

## Project Structure
```
├── data
│   ├── env_variables.json
│   ├── functionalities.json
│   └── perm.json
├── evaluation
│   ├── ambiguity
│   │   ├── inadvertent_data_exposure.json
│   │   └── uncontrolled_system_alteration.json
│   └── attacker
│       ├── app_compromise.json
│       └── data_stealing.json
├── figure
│   └── architecture.bmp
├── helpers
│   ├── configs
│   │   └── configuration.py
│   ├── isc
│   │   ├── message.py
│   │   └── socket.py
│   ├── memories
│   │   └── memory.py
│   ├── permission
│   │   └── permission.py
│   ├── sandbox
│   │   └── sandbox.py
│   ├── templates
│   │   └── prompt_templates.py
│   ├── tools
│   │   ├── specifications
│   │   │   ├── create_gmail_draft.json
│   │   │   ├── creative_muse.json
│   │   │   ├── delete_gmail_message.json
│   │   │   ├── get_gmail_message.json
│   │   │   ├── get_gmail_thread.json
│   │   │   ├── google_drive_retrieve.json
│   │   │   ├── health_companion.json
│   │   │   ├── metro_hail.json
│   │   │   ├── quick_ride.json
│   │   │   ├── search_gmail.json
│   │   │   ├── send_gmail_message.json
│   │   │   ├── symptom_solver.json
│   │   │   └── travel_mate.json
│   │   └── tool_importer.py
│   └── utilities
│       ├── database.py
│       └── setup_envoironment.py
├── hub
│   ├── hub.py
│   ├── hub_operator.py
│   └── planner.py
├── spoke
│   ├── output_parser.py
│   ├── shell_spoke.py
│   ├── spoke.py
│   └── spoke_operator.py
├── vanillagpt
│   └── vanillagpt.py
├── LICENSE
├── README.md
├── requirements.txt
├── secgpt_case_studies.py
├── secgpt_main.py
├── vanillagpt_case_studies.py
└── vanillagpt_main.py
```
