class CustomAuthException(Exception):
    pass


class UserAlreadyExists(CustomAuthException):
    pass
