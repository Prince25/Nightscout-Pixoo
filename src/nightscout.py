from urllib.parse import urljoin
from config import NIGHTSCOUT_URL
from connection_helper import check_connection, make_request, with_retry_on_connection_failure


# Nightscout API Client
class NightscoutClient:
    def __init__(self, base_url: str = NIGHTSCOUT_URL):
        self.base_url = base_url

    def check_connection(self):
        return check_connection(
            self._build_api_url(),
            'Nightscout',
            timeout=5,
            verify=False,
        )

    def _build_api_url(self) -> str:
        return urljoin(self.base_url, '/api/v1/entries/sgv.json?count=2')

    @with_retry_on_connection_failure
    def get_latest_sgv(self):
        response = make_request(self._build_api_url(), verify=False, timeout=10)
        response.raise_for_status()

        data = response.json()
        if not isinstance(data, list) or len(data) < 2:
            raise ValueError('Nightscout response did not contain at least two entries.')

        current = data[0]
        previous = data[1]
        current_sgv = str(current['sgv'])
        current_direction = str(current.get('direction', ''))
        time = current['dateString']
        delta_value = int(current['sgv'] - previous['sgv'])
        delta = f"{'+' if delta_value > 0 else ''}{delta_value}"

        return current_sgv, current_direction, delta, time
