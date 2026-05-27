import requests
from integrations.logger import log

# Hide TLS warnings for all shared requests made by this module
requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)


# Return a function that makes an HTTP request with the specified method, URL, timeout, and SSL verification settings
def make_request(url: str, method: str = 'get', timeout: float = 5, verify: bool = True, **kwargs):
    try:
        request_func = getattr(requests, method.lower())
    except AttributeError:
        raise ValueError(f'Unsupported request method: {method}')

    return request_func(url, timeout=timeout, verify=verify, **kwargs)


# Verify connection
def check_connection(url: str, service_name: str, timeout: float = 5, verify: bool = True):
    try:
        response = make_request(url, timeout=timeout, verify=verify)
        if response.status_code != 200:
            raise Exception(f'{service_name} returned status {response.status_code}')

        log(f'Trying to connect to {service_name} at "{url}" ... OK.')
        return True
    except Exception as e:
        log(f'{service_name} connection failed: {e}')
        raise


# Decorator to retry an operation if connection is lost.
# The wrapped function should be a bound method on an object with a `check_connection` method.
def with_retry_on_connection_failure(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as error:
            log(f'Operation failed: {error}')

            client = args[0] if args else None
            if client is None:
                raise Exception(f'Operation failed and no client instance was available. Original error: {error}')

            try:
                client.check_connection()
            except Exception:
                raise Exception(f'Connection lost and cannot be re-established. Original error: {error}')

            try:
                log('Retrying operation...')
                return func(*args, **kwargs)
            except Exception as retry_error:
                raise Exception(f'Operation failed on retry: {retry_error}')

    return wrapper
