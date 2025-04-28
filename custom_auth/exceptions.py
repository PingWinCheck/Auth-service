class CustomAuthException(Exception):
    pass


class UserAlreadyExistsException(CustomAuthException):
    pass


class TokenInvalidException(CustomAuthException):
    pass


class InvalidLoginOrPassword(CustomAuthException):
    pass
