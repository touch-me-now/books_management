from .settings import *  # noqa


REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"] = {
    'anon': '10000/day',
    'user': '10000/day'
}
