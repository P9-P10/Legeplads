import datetime
import random

from dateutil.relativedelta import relativedelta
from randomuser import RandomUser

from Scripts.Helpers.database_seeder_formatters import *


class User:
    def __init__(self, user_id, c_user):
        self.username = toSQLString(c_user.get_username())
        self.password = toSQLString(c_user.get_login_md5())
        self.email = toSQLString(c_user.get_email())
        self.first_name = toSQLString(c_user.get_first_name())
        self.last_name = toSQLString(c_user.get_last_name())
        self.birthday = toSQLString(c_user.get_dob())
        self.subscribed = bool(random.getrandbits(1))
        self.address = toSQLString(c_user.get_street())
        self.phone_number = toSQLString(c_user.get_phone())
        self.id = user_id
        self.name = toSQLString(c_user.get_first_name() + " " + c_user.get_last_name())


def generate_users(count=10) -> [User]:
    users = []
    user_list = RandomUser.generate_users(count, {"nat": "dk"})
    g_id = 0
    for c_user in user_list:
        id = g_id + 1
        g_id = g_id + 1
        users.append(User(id, c_user))
    return users


def get_random_product():
    products = ["Chair", "Table", "Door", "FirstBook", "LOTR"]
    selector = random.randint(0, len(products) - 1)
    return toSQLString(products[selector])


def get_random_adress_and_ordered_by(users) -> (str, str):
    user = users[random.randint(0, len(users) - 1)]
    return str(user.address), str(user.id)


def random_date():
    current_date = datetime.datetime.now()
    old_date = current_date - relativedelta(years=10)
    """
    This function will return a random datetime between two datetime 
    objects.
    """
    delta = current_date - old_date
    int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
    random_second = random.randrange(int_delta)
    return toSQLString(current_date - datetime.timedelta(seconds=random_second))


def get_random_user_id(users: [User]):
    return random.randint(0, len(users) - 1) + 1


def get_random_user_address(users: [User]):
    return users[random.randint(0, len(users) - 1)].address



def generate_extra_newsletters(users:[User]):
    user = users.pop()

    return user.email, user.subscribed


def get_random_user(users):
    return users[random.randint(0, len(users) - 1)]
