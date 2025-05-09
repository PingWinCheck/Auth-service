class CustomAuthException(Exception):
    pass


class UserAlreadyExistsException(CustomAuthException):
    pass


class TokenInvalidException(CustomAuthException):
    pass


class InvalidLoginOrPasswordException(CustomAuthException):
    pass


class UserDoesNotExistsException(CustomAuthException):
    pass
