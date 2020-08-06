import requests
import logging


class PrometheusClient:
    def __init__(self, prometheus_url):
        self.prometheus_url = prometheus_url

    def query(self, query):
        query_url = f'{self.prometheus_url}/api/v1/query'

        response = requests.get(query_url, params=dict(query=query))

        data = response.json()

        if data['status'] != 'success':
            logging.error(f'Prometheus API returned error: {data}')

        return data['data']['result']
