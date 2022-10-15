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
