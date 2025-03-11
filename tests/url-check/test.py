import csv
import os

def search(path_to_file, url):
    
    with open(path_to_file, mode = 'r', newline='', encoding='utf-8') as url_file:
       
        reader = csv.reader(url_file)
        
        for row in reader:
            if row[1] == url:
                print("Phishing Detected")
                return True
        
        print("URL not found in database")
        return False

filename = 'verified_online.csv'
inputted_url = input("Enter a URL to test: ")

search(os.path.join(os.getcwd(), filename), inputted_url)

input("Press Enter to exit...")