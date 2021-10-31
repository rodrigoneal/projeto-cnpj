import asyncio
import functools

from captcha_breaker import Breakers


def run_in_executor(f):
    @functools.wraps(f)
    def inner(*args, **kwargs):
        loop = asyncio.get_running_loop()
        return loop.run_in_executor(None, lambda: f(*args, **kwargs))

    return inner


@run_in_executor
def captcha(image):
    captcha = Breakers()
    token = captcha.image_captcha(image=image)
    return token