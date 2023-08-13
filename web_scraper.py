"""
A simple python web scraper.

Rapidly scrapes indicators of compromise from a number of public
threat intelligence sources.
"""

import logging
import argparse, os, requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, wait

class WebScraper:
    """
    Extensible web scraping engine. Provides methods to
    scrape public IOC lists.

    Attributes:
        virusshare_url(string):URL for virusshare.com
        directory(string):Folder directory to store data
    """
    def __init__(self):
        self.virusshare_url = "https://virusshare.com/hashes"
        self.directory = 'ioc_data/'

        # Create directory to store data
        try:
            os.mkdir(self.directory)
        except FileExistsError:
            pass

    def scrape_malware_hashes(self):
        """Method to scrape malware MD5 hashes from virusshare.com"""

        # Print info message
        print("Starting scrape of {}".format(self.virusshare_url))

        # Connect to url
        try:
            response = requests.get(self.virusshare_url)
        except Exception as e:
            logging.info("Couldn't connect to {}".format(self.virusshare_url))

        # Grab HTML page
        soup = BeautifulSoup(response.text, 'html.parser')

        # Iterate through hyperlinks
        links = []
        for link in soup.table.p.find_all('a'):
            if "hashfiles/VirusShare" in link.get('href'):
                links.append('https://virusshare.com/' + link.get('href'))

        # Scrape hyperlinks concurrently
        engine = ConcurrencyEngine(len(links), links)
        engine.run_tasks(self.download_hash_file)

    def download_hash_file(self, hash_file_url):
        """Method to download individual MD5 hash file from virusshare.com"""
        
        # Create filename from URL, will contain a .txt extension
        filename = self.directory + hash_file_url.split('/')[4].split('.')[0]+".txt"

        # Scrape data
        try:
            hashes = requests.get(hash_file_url).text.split('\n')[6:]
        
        except Exception:
            logging.info("Failed to download data from {}".format(hash_file_url))
            pass

        # Create file for writing
        with open(filename, "a+") as file:
            
            # Scrape hash values, remove header and write to file
            for hash in hashes:
                file.write(hash + "\n")

        # Print message
        logging.info("Scraped {} hashes from {}".format(len(hashes), hash_file_url))


class ConcurrencyEngine:
    """Concurrency engine based on ThreadPoolExecutor to speed up scraping"""
    def __init__(self, max_threads, hash_file_urls):
        self.max_threads = max_threads
        self.hash_file_urls = hash_file_urls

    def run_tasks(self, scrape_task):
        """Object method to run ThreadPoolExecutor tasks"""
        
        # create the thread pool
        with ThreadPoolExecutor(self.max_threads) as executor:
            # dispatch tasks
            results = executor.map(scrape_task, self.hash_file_urls)
            
            # report results in order
            try:
                wait(results)
            except AttributeError:
                logging.info("Scrape complete")
                pass

def main():
    """Main program entry point"""

    # Set up logging level
    logging.basicConfig(level=logging.INFO, format='%(message)s')

    # Set up arguments
    parser = argparse.ArgumentParser(description="Simple python parser to rapidly scrape IOCs from public CTI sources")
    parser.add_argument("-m", "--malware_hashes", help="Scrapes virusshare.com for MD5 malware hashes", action='store_true')

    # Parse arguments
    args = parser.parse_args()

    # Launch scrape
    if args.malware_hashes:
        WebScraper().scrape_malware_hashes()
    else:
        # Print help menu if no flags are passed
        parser.print_usage()

if __name__ == "__main__":
    main()
