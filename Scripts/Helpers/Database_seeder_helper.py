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
        self.subscribed = get_rand_bool()
        self.address = toSQLString(c_user.get_street())
        self.phone_number = toSQLString(c_user.get_phone())
        self.id = user_id
        self.name = toSQLString(c_user.get_first_name() + " " + c_user.get_last_name())
        self.created_at = random_date(10)


class Purpose:
    def __init__(self, name, ttl, target_table, target_column, origin, start_time, legally_required):
        self.legally_required = legally_required
        self.start_time = toSQLString(start_time)
        self.origin = toSQLString(origin)
        self.target_column = toSQLString(target_column)
        self.target_table = toSQLString(target_table)
        self.ttl = toSQLString(ttl)
        self.name = toSQLString(name)


select_user_creation_date = "SELECT Creation_date,users.id as uid FROM users JOIN user_metadata um on users.id = um.user_id JOIN gdpr_metadata gm on gm.id = um.metadata_id"
select_last_order_date = "SELECT max(order_date) as Creation_date, orderedBy as uid FROM orders GROUP BY orderedBy"


def get_purposes():
    purpose1 = Purpose("Marketing", "2y", "newsletter", "email", "local", select_user_creation_date, False)
    purpose2 = Purpose("Bookkeeping", "5y", "newsletter", "email", "local", select_last_order_date, True)
    purposes = [purpose1, purpose2]
    return purposes


purposes = get_purposes()


def get_rand_bool():
    return bool(random.getrandbits(1))


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


def get_random_order_information(users: [User]) -> (str, str, str):
    user = users[random.randint(0, len(users) - 1)]
    date = random_date(10, first_date=fromSQLStringToDate(user.created_at))
    address = user.address
    user_id = user.id
    return str(date), str(address), str(user_id)


def random_date(years=10, first_date=None, as_string=True):
    current_date = datetime.datetime.now()
    if first_date:
        old_date = current_date - (current_date - first_date)
    else:
        old_date = current_date - relativedelta(years=years)
    """
    This function will return a random datetime between two datetime 
    objects.
    """
    delta = current_date - old_date
    int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
    random_second = random.randrange(int_delta)
    random_time = current_date - datetime.timedelta(seconds=random_second)
    if as_string:
        return toSQLString(random_time.strftime('%Y-%m-%d %H:%M'))
    else:
        return random_time


def purpose_table_generator(start_count=1):
    output = ""
    for purpose in purposes:
        output += "("
        output += value_seperator(start_count)
        output += value_seperator(purpose.name)
        output += value_seperator(purpose.ttl)
        output += value_seperator(purpose.target_table)
        output += value_seperator(purpose.target_column)
        output += value_seperator(purpose.origin)
        output += value_seperator(purpose.start_time)
        output += value_seperator(purpose.legally_required)
        output = remove_last_comma(output.rstrip())
        output += "), \n"
        start_count += 1
    output = remove_last_comma(output)
    output = end_of_values_format(output)

    return output


def generate_purpose_rows(users: [User], start_count=1):
    output = ""
    for user in users:
        for i in range(1, len(purposes) + 1):
            output += "("
            output += value_seperator(start_count)
            output += value_seperator(str(user.id))
            output += value_seperator(str(i))
            output += value_seperator(get_rand_bool())
            output += value_seperator(get_rand_bool())
            output = remove_last_comma(output.rstrip())
            output += "), \n"
            start_count += 1
    output = remove_last_comma(output)
    output = end_of_values_format(output)
    return output


def get_random_user_id(users: [User]):
    return random.randint(0, len(users) - 1) + 1


def get_random_user_address(users: [User]):
    return users[random.randint(0, len(users) - 1)].address


def generate_extra_newsletters(users: [User]):
    user = users.pop()

    return user.email, user.subscribed


def get_random_user(users):
    return users[random.randint(0, len(users) - 1)]
