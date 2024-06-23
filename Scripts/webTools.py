import requests
import pandas as pd
import os
import pytz

from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urlparse, urljoin

class webTools:
    def __init__(self, base_url):
        # Convert URLs to a List if only one was passed
        if isinstance(base_url, str):
            self.base_urls  = [base_url]

        elif isinstance(base_url, list):
            self.base_urls  = base_url

        self.base_url       = base_url
        ###

        # Create a directory to store the data
        self.output_dir = 'Output'

        if os.path.exists(self.output_dir) == False:
            os.mkdir(self.output_dir)
        ###
            
        # Validate the URLs
        if self._validateURLs() == False:
            return None


    def GetURLMap(self, export_output=True, mode='all'):
        """
        Gets a list of all URLs on the page
        """

        # Check if the mode is valid
        if mode not in ['all', 'unique', 'check urls']:
            print(f"Error: {mode} is not a valid mode ('all' or 'unique')")
            return None

        data = []

        if mode == 'all':
            filename = 'URLMap'
        
        elif mode == 'unique':
            filename = 'UniqueURLs'

        elif mode == 'check urls':
            filename = 'CheckURLs'

        # Create the output file
        output_file = f'{self.output_dir}/{mode}_{self.getCurrentDateStr()}.csv'
        os.makedirs(self.output_dir, exist_ok=True)
        ###

        # Loop through each URL and get the links + counts

        for base_url in self.base_urls:
            try:
                response = requests.get(base_url)
                soup = BeautifulSoup(response.text, 'html.parser')
            except Exception as e:
                print(f'Error: {e}')
                return None

            for link in soup.find_all('a'):

                try:
                    relative_url = link.get('href')
                    # print(base_url, relative_url)

                    if relative_url.startswith(':'):
                        relative_url = relative_url.replace(':', '/')
                    absolute_url = urljoin(base_url, relative_url)
                except Exception as e:
                    print(f"Error: {e}. URL: {url}") 
                    url = e
                
                try:
                    text = link.text
                except Exception as e:
                    text = e
                
                data.append({'URL': base_url, 'Linked URL': absolute_url, 'Link Text': text})
        ###
                
        df = pd.DataFrame(data).replace('\n', '', regex=True)
        
        if mode == 'all':
            # Convert the data to a DataFrame
            url_counts = df['Linked URL'].value_counts()
            df['Count'] = df['Linked URL'].map(url_counts)
            ###

        elif mode == 'unique':
            # Get the unique URLs
            df = df['Linked URL'].unique()
            ###

            df = pd.DataFrame(df, columns=['Linked URL'])

        elif mode == 'check urls':
            try:
                # Get the unique URLs
                df = df['Linked URL'].unique()
                ###

                df = pd.DataFrame(df, columns=['Linked URL'])
                df['Status'], df['Latency'] = zip(*df['Linked URL'].map(self._get_status_and_latency))

            except Exception as e:
                print(f"Error: {e}")
                return None

        # Save the data to a CSV if requested
        if export_output == True:
            df.to_csv(output_file, index=False)
            print("Data saved to:", output_file)
        ###

        return df

    ########################################
    # HELPER FUNCTIONS
    ########################################

    def getCurrentDateStr(self):
        now = datetime.now(pytz.timezone('US/Eastern'))
        output = now.strftime('%Y-%m-%d_%H-%M-%S_%Z')
        
        return output
    
    def _validateURLs(self):
        """
        Validates the URLs
        """
        # Check if the URL is valid
        for url in self.base_urls:
            if 'http' not in url:
                print(f"Error: {url} is not a valid URL")
                return False
        ###
            
        # Request each URL to see if it is valid
        for url in self.base_urls:
            try:
                response = requests.get(url)
                
                if response.status_code != 200:
                    print(f"Error: {url} is not a valid URL")
                    return False
            
            except Exception as e:
                print(f"Error: {url} is not a valid URL")
                return False
        ###
        
        return True
    
    def _get_status_and_latency(self, url):
        """
        Gets the status and latency of a URL
        """
        try:
            response = requests.get(url)
            status = response.status_code
            latency = response.elapsed.total_seconds()
        except Exception as e:
            status = e
            latency = e
        ###
        
        return status, latency