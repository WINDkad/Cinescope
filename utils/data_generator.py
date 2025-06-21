from faker import Faker
import string
import random
faker = Faker()

class DataGenerator:

    @staticmethod
    def generate_random_email():
        random_string = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        return f"kek{random_string}@gmail.com"

    @staticmethod
    def generate_random_name():
        return f"{faker.first_name()} {faker.last_name()}"

    @staticmethod
    def generate_random_password():
        import string
        import random

        special_chars = "?@#$%^&*_\\-+()[]{}><\\/|\"'.,:;"
        all_chars = string.ascii_letters + string.digits + special_chars
        password = random.choice(string.ascii_letters) + random.choice(string.digits)
        remaining = random.choices(all_chars, k=random.randint(6, 18))
        password += ''.join(remaining)
        return ''.join(random.sample(password, len(password)))
