from helpers.utilities.setup_environment import setup_environment
from helpers.configs.configuration import Configs

def main(user_id, debug=True, functionalities_path=None, test_queries=None):
    # Get the mode from the configuration file
    Configs.set_debug_mode(debug)
    Configs.set_user_id(user_id)
    
    if functionalities_path:
        Configs.set_functionalities_path(functionalities_path)
    
    # Set up all necessary environment variables and perform initializations
    setup_environment()
    
    # Initialize Hub
    from hub.hub import Hub
    hub = Hub()
    
    if debug:  
        for query in test_queries:
            hub.query_process(query)
        
    else:
        print("Message SecGPT (enter '/exit' to end the conversation)...")
        while True:
            query = input("You: ")
            if query.lower() == "/exit":
                break
            hub.query_process(query)
            

if __name__=='__main__':
    main('0', debug=False)
