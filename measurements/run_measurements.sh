#!/bin/bash

# Paths for Python library files that need to be instrumented
ORIGINAL_BASE="/home/isolategpt/miniconda3/envs/isolategpt/lib/python3.9/site-packages/langchain/chains/base.py"
ORIGINAL_AGENT="/home/isolategpt/miniconda3/envs/isolategpt/lib/python3.9/site-packages/langchain/agents/agent.py"

# Paths for instrumented Python library files for VanillaGPT and IsolateGPT
VANILLAGPT_BASE="/home/isolategpt/Desktop/SecGPT-IsolateGPT-AE/measurements/vanillagpt/base.py"
VANILLAGPT_AGENT="/home/isolategpt/Desktop/SecGPT-IsolateGPT-AE/measurements/vanillagpt/agent.py"
ISOLATEGPT_BASE="/home/isolategpt/Desktop/SecGPT-IsolateGPT-AE/measurements/spoke/base.py"  
ISOLATEGPT_AGENT="/home/isolategpt/Desktop/SecGPT-IsolateGPT-AE/measurements/spoke/agent.py" 

# Paths for the time recorder program and its destinations
TIME_RECORDER="/home/isolategpt/Desktop/SecGPT-IsolateGPT-AE/measurements/helpers/utilities/time_recorder.py"
TIME_RECORDER_DEST1="/home/isolategpt/miniconda3/envs/isolategpt/lib/python3.9/site-packages/langchain/agents/time_recorder.py"
TIME_RECORDER_DEST2="/home/isolategpt/miniconda3/envs/isolategpt/lib/python3.9/site-packages/langchain/chains/time_recorder.py"

RESULTS_DIR="/home/isolategpt/Desktop/SecGPT-IsolateGPT-AE/measurements/results"

# Function to print a separator
print_separator() {
  echo "===================================================================="
}

# Function to print a header
print_header() {
  echo -e "\033[1;34m$1\033[0m"  # Bold blue text
}

# Function to print a success message
print_success() {
  echo -e "\033[1;32m$1\033[0m"  # Bold green text
}

# Silently create backup of the original files (only if backups don't already exist)
[ ! -f "${ORIGINAL_BASE}.backup" ] && cp $ORIGINAL_BASE "${ORIGINAL_BASE}.backup"
[ ! -f "${ORIGINAL_AGENT}.backup" ] && cp $ORIGINAL_AGENT "${ORIGINAL_AGENT}.backup"
[ ! -f $TIME_RECORDER_DEST1 ] && cp $TIME_RECORDER $TIME_RECORDER_DEST1
[ ! -f $TIME_RECORDER_DEST2 ] && cp $TIME_RECORDER $TIME_RECORDER_DEST2

# ---VanillaGPT Experiment---
print_separator
print_header "🚀 Running performance analysis experiment for VanillaGPT..."

# Replace original files with VanillaGPT instrumented files (silent)
cp $VANILLAGPT_BASE $ORIGINAL_BASE
cp $VANILLAGPT_AGENT $ORIGINAL_AGENT

# Run VanillaGPT experiment (errors are silenced)
python vanillagpt_measurement_main.py 2>/dev/null

# Restore original files after the experiment (silent)
cp "${ORIGINAL_BASE}.backup" $ORIGINAL_BASE
cp "${ORIGINAL_AGENT}.backup" $ORIGINAL_AGENT

print_success "VanillaGPT experiment completed."

# ---IsolateGPT Experiment---
print_separator
print_header "🚀 Running performance analysis experiment for IsolateGPT..."

# Replace original files with IsolateGPT instrumented files (silent)
cp $ISOLATEGPT_BASE $ORIGINAL_BASE
cp $ISOLATEGPT_AGENT $ORIGINAL_AGENT

# Run IsolateGPT experiment (errors are silenced)
python isolategpt_measurement_main.py 2>/dev/null

# Restore original files after the experiment (silent)
cp "${ORIGINAL_BASE}.backup" $ORIGINAL_BASE
cp "${ORIGINAL_AGENT}.backup" $ORIGINAL_AGENT

print_success "IsolateGPT experiment completed."

# ---Parse and display results---
print_separator
print_header "📊 Parsing and displaying results..."

python parse_results.py 2>/dev/null

print_success "Results parsed and displayed successfully."

print_separator

echo -e "\033[1;33m📂 The results of the experiments are stored in: ${RESULTS_DIR}\033[0m"
print_separator

