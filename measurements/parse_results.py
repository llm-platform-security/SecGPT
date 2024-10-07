import pandas as pd

task = "relational"

# Define the category names for output formatting
categories = ["Overall", "<3 Apps", "3-5 Apps"]

# Define column names for the table (including both systems)
columns = ['Query Category', '# Queries', 
           'VanillaGPT Planning', 'VanillaGPT Execution', 'VanillaGPT Memory', 'VanillaGPT Total',
           'IsolateGPT Hub Planning', 'IsolateGPT Hub Memory', 'IsolateGPT Spoke Planning', 
           'IsolateGPT Spoke Execution', 'IsolateGPT Spoke Memory', 'IsolateGPT Total']

# Initialize an empty list to store data for the table
table_data = []

# Create an empty dictionary to store data for both systems for each category
category_data = {category: {'vanillagpt': [], 'isolategpt': []} for category in categories}

query_counts = {}  # To store the query counts from isolategpt

for system in ["vanillagpt", "isolategpt"]:
    dataset = "./datasets/" + task + ".csv"
    df_dataset = pd.read_csv(dataset)

    # Calculate the number of apps by counting commas and adding 1
    df_dataset['Num_Apps'] = df_dataset['output_expected_steps'].apply(lambda x: x.count(',') + 1)

    runtime = "./results/" + system + "/" + task + "/runtime.csv"
    df_runtime = pd.read_csv(runtime)

    dataset_column = "input_question"
    runtime_column = "Question"

    # Merge dataset and runtime data
    matched_df = pd.merge(df_runtime, df_dataset, left_on=runtime_column, right_on=dataset_column)
    matched_df = matched_df.drop(columns=["input_question", "output_expected_steps", "output_order_matters", "output_reference"])

    # Split data into categories based on Num_Apps
    df_list = [
        ("Overall", matched_df),
        ("<3 Apps", matched_df[matched_df['Num_Apps'] <= 2]),
        ("3-5 Apps", matched_df[matched_df['Num_Apps'] > 2])
    ]


    # Collect data for each category
    for category_name, matched_df in df_list:
        if system == "isolategpt":
            
            # Calculate means for isolategpt
            runtime_mean = matched_df['Total'].mean()
            hub_memory_mean = matched_df['Hub_Memory'].mean()
            hub_planning_mean = matched_df['Hub_Planning'].mean()
            spoke_memory_mean = matched_df['Spoke_Memory'].mean()
            spoke_planning_mean = matched_df['Spoke_Planning'].mean()
            spoke_execution_mean = matched_df['Spoke_Execution'].mean()

            # Store isolategpt data in the dictionary
            category_data[category_name]['isolategpt'] = [
                hub_planning_mean, hub_memory_mean, spoke_planning_mean, 
                spoke_execution_mean, spoke_memory_mean, runtime_mean]
        
        elif system == "vanillagpt":
            query_counts[category_name] = len(matched_df)  # Get the number of queries
            # Calculate means for vanillagpt
            runtime_mean = matched_df['Total'].mean()
            memory_mean = matched_df['Memory'].mean()
            planning_mean = matched_df['Planning'].mean()
            execution_mean = matched_df['Execution'].mean()

            # Store vanillagpt data in the dictionary
            category_data[category_name]['vanillagpt'] = [
                planning_mean, execution_mean, memory_mean, runtime_mean]

# Now, combine the data from both systems into one row per category
for category_name in categories:
    # Get the row for the current category by combining data from vanillagpt and isolategpt
    query_count = query_counts.get(category_name, 0)  # Get the correct query count from isolategpt
    row = [category_name, query_count]  # Add the category name and query count
    row.extend(category_data[category_name]['vanillagpt'])  # Add vanillagpt data
    row.extend(category_data[category_name]['isolategpt'])  # Add isolategpt data

    # Append the row to the table data
    table_data.append(row)

# Create a Pandas DataFrame for the table
df_table = pd.DataFrame(table_data, columns=columns)

df_table.to_csv("./results/perf_compare.csv", index=False)

# Print the table
print(df_table)

