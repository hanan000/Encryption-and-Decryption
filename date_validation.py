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

    def encrypt_the_date(self) -> str:
        year, month, day = self.split_date(self.date)
        date_process = [int(day) + self.num, int(month) + self.num, int(year[::-1]) - self.num]
        modify_date = self.modify_date(date_process)
        encoder = self.join_str([text + str(number) for text, number in list(zip(self.random_string, modify_date))])
        print(encoder)
        return encoder

    def decrypt_the_date(self) -> date:
        remove_char = re.sub('\D', '', self.encrypt_the_date)
        try:
            year, month, day = self.two_digits_date(remove_char)
        except:
            day, month, year, year_ = self.single_digit_date(remove_char)
            year = str(year) + str(year_)

        year = int(year) + self.num
        date_process = [int(day) - self.num, int(month) - self.num, str(year)[::-1]]
        decoder = self.join_str([str(number) for number in date_process])
        result = self.datetime_process(decoder)
        print(result)
        return result


if __name__ == '__main__':
    check_the_validation = OfflineValidation(27, '2024-12-29', 7)
    check_the_validation.decrypt_the_date()


