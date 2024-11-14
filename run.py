from server import run_flask
from agent import PollingAgent
from config import check_config

import time
import multiprocessing

# This should only be executed in a child process.
def start_agent(run_counter):
    agent = PollingAgent()

    while True:
        agent.poll_apis()
        agent.alert_manager()
        run_counter.value += 1
        time.sleep(10)

# Required for multiprocessing to start correctly.
if __name__ == "__main__":
    if (not check_config()): 
        print("Config file check failed.")
        exit()
    
    # Multiprocessing setup. The main process starts the flask server and upkeeps the Polling Agent.
    multiprocessing.set_start_method("spawn")
    
    run_counter = multiprocessing.Value('i', 0)
    p = multiprocessing.Process(target=start_agent, args=(run_counter,))
    p.start()

    flask_p = multiprocessing.Process(target=run_flask)
    flask_p.start()

    # Kinda untested but in theory this should mean that if the monitoring process stops or fails
    # it will automatically be joined and then restarted.
    while True:
        time.sleep(20)
        if (run_counter.value < 1):
            p.join()

            p = multiprocessing.Process(target=start_agent, args=(run_counter,))

            p.start()
            print("Polling Agent stopped due to an unhandled exception.")

        run_counter.value = 0