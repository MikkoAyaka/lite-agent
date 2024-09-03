import requests


class BingSearchAPI:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = 'https://api.bing.microsoft.com/v7.0/custom/search'

    def parse_results(self, search_results):
        """Extract useful information from the search results."""
        results = []
        if 'webPages' in search_results:
            for result in search_results['webPages']['value']:
                title = result['name']
                url = result['url']
                results.append({'title': title, 'url': url})
        return results

    def search(self, query, mkt='en-US'):
        """Send a search query to Bing and return the JSON response."""
        headers = {"Ocp-Apim-Subscription-Key": self.api_key}
        params = {'q': query, 'customconfig': '2fff75a7-96b4-43aa-89bb-d2adc81dcdc0', 'mkt': mkt}
        response = requests.get(self.base_url, headers=headers, params=params)
        # print("HTTP Status Code:", response.status_code)  # 打印HTTP响应状态码
        return self.parse_results(response.json())