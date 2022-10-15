import random
import re
import string
import textwrap
import datetime
from datetime import datetime, date


class OfflineValidation:
    """OfflineValidation Class for determining whether the offline App is valid or not."""

    def __init__(self, length, date, num):
        """
       Args:
           length: is the length of the random string
           date: the validation date of the assistant.
           num: the number that will be added to encrypt the date.
       """
        self.length = length
        self.date = date
        self.num = num
        self.random_string = self.get_random_string()
        self.encrypt_the_date = self.encrypt_the_date()

    def join_str(self, data) -> str:
        join = ''.join(data)
        return join

    def datetime_process(self, data) -> date:
        date_format = datetime.strptime(data, "%d%m%Y").date()
        return date_format

    def split_date(self, data) -> list:
        return str(data).split()[0].split('-')

    def two_digits_date(self, data) -> list:
        get_date = self.datetime_process(data)
        return self.split_date(get_date)

    def single_digit_date(self, data) -> list:
        zfill = str(data)
        get_date = [int(zfill[idx: idx + 2]) for idx in range(0, len(zfill), 2) if len(zfill) == 8]
        return get_date

    def modify_date(self, data):
        modify_date = [str(idx).zfill(2) for idx in data]
        return modify_date

    def get_random_string(self) -> list:
        letters = string.ascii_lowercase
        result_str = self.join_str(random.choice(letters) for i in range(self.length))
        text_str = textwrap.wrap(result_str, 9)
        return text_str
