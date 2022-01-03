from multiprocessing import Process

import interface
import app

def main():
    # Create threads for server and window (interface)
    p_server = Process(target=app.serve)
    p_window = Process(target=interface.main)

    # Set all threads as Deamon thread (die on program termination)
    p_server.daemon = True
    p_window.daemon = True

    # Start server
    p_server.start()

    # Start window
    p_window.start()

    # Wait for window to close
    p_window.join()

if __name__ == "__main__":
    main()    