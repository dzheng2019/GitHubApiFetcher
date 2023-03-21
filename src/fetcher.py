import requests

# Create an API request 
url = 'https://api.github.com/search/repositories?q=language:python&sort=stars'
response = requests.get(url)
print("Status code: ", response.status_code)
# In a variable, save the API response.
response_dict = response.json()
# Evaluate the results.
print(response_dict.keys())