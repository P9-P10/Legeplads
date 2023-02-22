import random
import datetime

from dateutil.relativedelta import relativedelta

from Scripts.database_seeder import User
from Scripts.Helpers.database_seeder_formatters import *




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
