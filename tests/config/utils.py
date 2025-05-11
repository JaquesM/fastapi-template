import random
import string

def random_string(length=10):
    return ''.join(random.choices(string.ascii_letters, k=length))
