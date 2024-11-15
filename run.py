from server import run_flask
from agent import PollingAgent
from config import check_config
from pathlib import Path

import time
import multiprocessing
import logger, logging

# This should only be executed in a child process.
def start_agent(run_counter):
    agent = PollingAgent()

    while True:
        agent.poll_apis()
        agent.alert_manager()
        run_counter.value += 1
        time.sleep(10)

# Required for multiprocessing to start correctly.
# At some point this should be modified so that the config file is only polled from one location (this 
# file.) The info can then be passed as needed to the other methods and classes that require it without
# repeat polling of the data.
if __name__ == "__main__":
    Path("./logs").mkdir(parents=True, exist_ok=True)
    logger.init("main")
    log = logging.getLogger(__name__)
    log.setLevel(logging.INFO)
    
    if (not check_config()): 
        print("EXITING: CONFIG CHECK FAILED")
        log.critical("CONFIG CHECK FAILED")
        exit()

    log.info("Config check succeeded.")
    
    # Multiprocessing setup. The main process starts the flask server and upkeeps the Polling Agent.
    multiprocessing.set_start_method("spawn")
    
    run_counter = multiprocessing.Value('i', 0)
    p = multiprocessing.Process(target=start_agent, args=(run_counter,))
    p.start()
    log.info("Agent thread started successfully.")

    flask_p = multiprocessing.Process(target=run_flask)
    flask_p.start()
    log.info("Flask server started successfully.")

    # Kinda untested but in theory this should mean that if the monitoring process stops or fails
    # it will automatically be joined and then restarted.
    while True:
        time.sleep(20)
        if (run_counter.value < 1):
            log.error("Agent has hung or crashed. Restarting Agent.")
            p.join()

            p = multiprocessing.Process(target=start_agent, args=(run_counter,))

            p.start()
            log.info("Agent has been restarted.")

        run_counter.value = 0