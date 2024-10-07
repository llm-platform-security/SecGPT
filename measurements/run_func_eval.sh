#!/bin/bash

# Define the output file
OUTPUT_FILE="./results/func_compare.txt"

# Function to print a decorative line
print_separator() {
  echo "===================================================================="
}

# Function to print a header in the terminal
print_header() {
  echo -e "\033[1;34m$1\033[0m"  # Bold blue text
}

# Function to print a success message
print_success() {
  echo -e "\033[1;32m$1\033[0m"  # Bold green text
}

# Function to print a warning message
print_warning() {
  echo -e "\033[1;33m$1\033[0m"  # Bold yellow text
}

# Clear the output file or create it if it doesn't exist
> $OUTPUT_FILE

# --- VanillaGPT Experiment ---
print_separator
print_header "🚀 Running functionality correctness analysis for VanillaGPT..."
echo "---------------------------- VanillaGPT ----------------------------" | tee -a $OUTPUT_FILE

# Run the first Python program, display output in terminal and append to the log file, suppressing warnings
python vanillagpt_func_eval.py 2> >(grep -v 'warning' > /dev/null) | tee -a $OUTPUT_FILE

# Add a double newline for separation
echo -e "\n\n" | tee -a $OUTPUT_FILE

print_success "VanillaGPT functionality correctness analysis completed and results appended to $OUTPUT_FILE."

# --- IsolateGPT Experiment ---
print_separator
print_header "🚀 Running functionality correctness analysis for IsolateGPT..."
echo "---------------------------- IsolateGPT ----------------------------" | tee -a $OUTPUT_FILE

# Run the second Python program, display output in terminal and append to the log file, suppressing warnings
python isolategpt_func_eval.py 2> >(grep -v 'warning' > /dev/null) | tee -a $OUTPUT_FILE

print_success "IsolateGPT functionality correctness analysis completed and results appended to $OUTPUT_FILE."

# --- Results Location ---
print_separator
print_warning "📂 Functionality comparison results are saved in: $OUTPUT_FILE"
print_separator
