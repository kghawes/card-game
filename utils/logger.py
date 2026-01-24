from datetime import datetime

class Logger:
    def __init__(self, write_to_file=False):
        """
        Initialize a new Logger.
        """
        self.logs = []
        self.write_to_file = write_to_file
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def log(self, message, is_debug=False):
        """
        Add a new log entry.
        """
        if not is_debug:
            self.logs.append(message)
        if self.write_to_file:
            log_type = "DEBUG" if is_debug else "INFO"
            with open(f"logs/log_{self.timestamp}.txt", "a") as file:
                file.write(f"[{log_type}] {message}" + "\n")
        elif is_debug:
            print(f"[DEBUG] {message}")
    
    def get_combat_logs(self):
        """
        Retrieve all combat logs.
        """
        combat_log = self.logs[:]
        self.logs.clear()
        return combat_log