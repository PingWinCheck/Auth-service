from auth.models import User
from core.dao import BaseDAO


class UserDAO(BaseDAO):
    model = User
