from faker import Faker
import random
import string
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
    def generate_random_int(min, max):
        return faker.random_int(min=min, max=max)

    @staticmethod
    def generate_random_sentence(count):
        return faker.sentence(nb_words=count)

    @staticmethod
    def generate_random_str(count):
        return ''.join(faker.random_letters(count))

    @staticmethod
    def generate_random_boolean():
        return faker.boolean()

    @staticmethod
    def generate_random_password():
        letters = random.choice(string.ascii_letters)
        digits = random.choice(string.digits)
        special_chars = "?@#$%^&*|:"
        all_chars = string.ascii_letters + string.digits + special_chars
        remaining_length = random.randint(6, 18)
        remaining_chars = ''.join(random.choices(all_chars, k=remaining_length))
        password = list(letters + digits + remaining_chars)
        random.shuffle(password)

        return ''.join(password)