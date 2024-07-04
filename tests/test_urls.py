import subprocess

# Define the function to check if a URL returns a 200 OK status
def check_url_status(url):
    print(f"Checking URL: {url}")
    command = f'curl -s -o /dev/null -w "%{{http_code}}\n" -H "Accept: application/json" "{url}"'
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    status = result.stdout.strip()
    print(f"Status code: {status}")
    return status == "200"

# List of URLs to check (very small batch)
url_list_small_1 = [
    'http://api.worldbank.org/v2/country/all/indicator/SP.POP.TOTL?format=json'
]

# Check the status of each URL in the very small batch
valid_urls_small_1 = []
for url in url_list_small_1:
    if check_url_status(url):
        valid_urls_small_1.append(url)

print("Valid URLs returning JSON response (200 OK):")
for valid_url in valid_urls_small_1:
    print(valid_url)
