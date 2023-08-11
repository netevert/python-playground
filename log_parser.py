"""
Simple python log parser. Parses logs adhering to common log format. 

Tested using log sample available here:
https://github.com/adityarkelkar/python-log-parser/blob/master/log
"""

import argparse

class LogEntry:
    """Object to parse CLF log lines into a common data structure 

    Attributes: 
        ip_address(string): The ip address field within the log line
        timestamp(string): The timestamp field within the log line
        http_request(string): The HTTP request field within the log line
        http_response_code(string): The HTTP response code within the log line
        object_size(string): The object size within the log line
        url(string): The origin URL within the log line
        user_agent(string): The User Agent field within the log line

    Methods:
        match_ip(target_ip): Checks if a target ip matches the LogEntry ip_address attribute
    """
    def __init__(self, entry):
        # Loads log line and parses it into LogEntry data structure
        self.entry = entry
        self.ip_address = self.entry.split("- -")[0].strip()
        self.timestamp = self.entry.split("- -")[1].split("] ")[0].strip()[1:]
        self.http_request = self.entry.split("- -")[1].split("] ")[1].split('"')[1]
        self.http_response_code = self.entry.split("- -")[1].split("] ")[1].split('"')[2].split()[0]
        self.object_size = self.entry.split("- -")[1].split("] ")[1].split('"')[2].split()[1]
        self.url = self.entry.split("- -")[1].split("] ")[1].split('"')[3]
        self.user_agent = self.entry.split("- -")[1].split("] ")[1].split('"')[5]

    def __str__(self):
        """Returns a string representation of the LogEntry object"""
        return """Log entry:
    ip_address: {}
    timestamp: {}
    http_request: {}
    http_response_code: {}
    object_size: {}
    user_agent: {}
    """.format(self.ip_address, self.timestamp, self.http_request, self.http_response_code, self.object_size, self.user_agent)

    def match_ip(self, target_ip):
        """Method to check if a target ip matches the LogEntry ip_address attribute
           Returns false if a match is not found, otherwise true

           Parameters:
               target_ip(str)
           """
        if target_ip != self.ip_address:
            return False
        return True
    
class LogParser:
    """Object to parse CLF logs and run searches for specific entries

    Attributes: 
        file_path(string): A CLF log file to be parsed by object's methods

    Methods:
        search_ip(target_ip): searches for entries in a CLF log that match target ip
    """
    def __init__(self, file_path):
        self.file_path = file_path

    def search_ip(self, target_ip):
        """Method to search for entries in a CLF log that match a target ip.
           Prints all matches to the console
           
           Parameters:
               target_ip(str)
           """
        
        # Attempt to open and process file
        try:

            # Iterate over log file lines
            with open(self.file_path) as file:
                for line in file.readlines():
                    
                    # Parse log line
                    parsed_line = LogEntry(line)

                    # Check if target ip matches. If yes print line
                    if parsed_line.match_ip(target_ip):
                        print(parsed_line)

        # Catch and report any file opening errors
        except Exception as e:
            print("Error:Could not open file:{}".format(e))

def main():
    """Main program entry point"""
    
    # setup command line parameters
    parser = argparse.ArgumentParser(description="Simple python parser for CLF logs")
    parser.add_argument("-f", "--file", help="Target log file to be searched", required=True)
    parser.add_argument("-ip", "--ip_address", help="Search log file for entries matching ip address", required=True)

    # parse arguments
    args = parser.parse_args()

    # Initiate LogParser object and run search
    LogParser(args.file).search_ip(args.ip_address)

if __name__ == "__main__":
    main()
