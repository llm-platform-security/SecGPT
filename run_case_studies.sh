#!/bin/bash

# Create the results directory if it doesn't exist
mkdir -p ./results

# Function to print a decorative line
print_separator() {
  echo "==============================================================="
}

# Function to print section headers
print_header() {
  echo -e "\n$1"
}

# Loop over cases from 1 to 4
for case_number in {1..4}; do
  print_separator
  print_header "🚀 Starting Case Study $case_number"
  print_separator

  # Run the first Python program (VanillaGPT) and store output in a separate log file
  print_header "💻 Running VanillaGPT for Case $case_number"
  echo -e "\nLogging to ./results/vanillagpt_case${case_number}.txt\n"
  python vanillagpt_case_studies.py --case "$case_number" | tee >(sed 's/\x1b\[[0-9;]*m//g' > "./results/vanillagpt_case${case_number}.txt")
  echo -e "\nOutput for VanillaGPT with Case $case_number saved to ./results/vanillagpt_case${case_number}.txt\n"

  print_separator

  # Run the second Python program (IsolateGPT) and store output in a separate log file
  print_header "💻 Running IsolateGPT for Case $case_number"
  echo -e "\nLogging to ./results/isolategpt_case${case_number}.txt\n"
  python isolategpt_case_studies.py --case "$case_number" | tee >(sed 's/\x1b\[[0-9;]*m//g' > "./results/isolategpt_case${case_number}.txt")
  echo -e "\nOutput for IsolateGPT with Case $case_number saved to ./results/isolategpt_case${case_number}.txt\n"

  print_separator
  echo -e "\nCompleted Case Study $case_number"
  print_separator
done

# Print a message indicating all cases are completed
echo -e "\nAll case studies from 1 to 4 have been successfully completed!\n"
