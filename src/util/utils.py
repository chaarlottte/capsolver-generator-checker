import random, string

class utils():
    def get_password(x: int = 16):
        prefix = "chargen$$"
        prefix = ""
        x = x - len(prefix)
        return f"{prefix}{''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits + string.punctuation) for i in range(x))}"
