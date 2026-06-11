import logging

logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def divide_two_numbers(a, b):
    logger.info("op=divide_two_numbers a=%s b=%s", a, b)
    if a == 0 or b == 0:
        logger.warning("op=divide_two_numbers status=failed reason=one element is 0")
        return
    return a / b


def do_math(op, a, b):
    if op == "DIVIDE":
        result = divide_two_numbers(a, b)
        print(result + 10)
        return result


do_math("DIVIDE", 0, 10)
