import datetime
import random

from dateutil.relativedelta import relativedelta
from randomuser import RandomUser


class User():
    def __init__(self, id, c_user):
        self.username = toSQLString(c_user.get_username())
        self.password = toSQLString(c_user.get_login_md5())
        self.email = toSQLString(c_user.get_email())
        self.first_name = toSQLString(c_user.get_first_name())
        self.last_name = toSQLString(c_user.get_last_name())
        self.birthday = toSQLString(c_user.get_dob())
        self.subscribed = bool(random.getrandbits(1))
        self.address = toSQLString(c_user.get_street())
        self.phone_number = toSQLString(c_user.get_phone())
        self.id = id
        self.name = toSQLString(c_user.get_first_name() + " " + c_user.get_last_name())

def toSQLString(entry):
    return '"' + str(entry) + '"'


column_type_map = {"subscribed": "BOOL",
                   "id": "INT NOT NULL PRIMARY KEY",
                   "order_date": "DATETIME",
                   "orderedBy": "INT",
                   "birthday": "DATETIME"}


def end_of_values_format(output_string):
    return output_string[:-2] + ";\n\n"


def end_of_line_format(output_string):
    return output_string[:-2] + "),\n"


def insert_into(columns, table_name):
    output_columns = ','.join(columns)
    output_string = "INSERT INTO " + table_name + f" ({output_columns}) VALUES\n"
    return output_string


def line_format(input_string):
    return input_string + ", "


def generate_users(count=10):
    users = []
    user_list = RandomUser.generate_users(count, {"nat": "dk"})
    g_id = 0
    for c_user in user_list:
        id = g_id + 1
        g_id = g_id + 1
        users.append(User(id, c_user))
    return users


def create_table(table_name, column_type: [str]):
    output_string = "CREATE TABLE " + table_name + "("
    for column_name in column_type:
        if column_name in column_type_map:
            output_string = generate_row_creation(output_string, column_name, column_type_map[column_name])
        else:
            output_string = generate_row_creation(output_string, column_name, "VARCHAR(256)")
    output_string = remove_last_comma(output_string)
    output_string = output_string + "\n);"

    print(output_string)


def remove_last_comma(output_string):
    return output_string[:-1]


def generate_row_creation(output_string, column_name, column_type):
    output_string = output_string + "\n  "
    return output_string + column_name + " " + column_type + ","


def populate_table_from_users(table_name, users: [User], columns: [str], user_properties: [str]):
    output_string = insert_into(columns, table_name)
    for user in users:
        output_string = output_string + "  ("
        for property in user_properties:
            output_string = apply_user_data(property, output_string, user)
        output_string = end_of_line_format(output_string)
    output_string = end_of_values_format(output_string)
    print(output_string)


def apply_user_data(key, output_string, user):
    return output_string + line_format(str(getattr(user, key)))


def populate_table_from_functions(table_name, functions: [], columns: [str], count: int, id_first=True):
    output_string = insert_into(columns, table_name)

    for i in range(count):
        output_string = output_string + "("
        if id_first:
            output_string = print_id(i, output_string)
        for f in functions:
            output_string = apply_function(f, output_string)
        output_string = end_of_line_format(output_string)
    output_string = end_of_values_format(output_string)
    print(output_string)


def apply_function(f, output_string):
    result = f()
    if isinstance(result, tuple):
        output_string = output_string + line_format(result[0]) + line_format(result[1])
    else:
        output_string = output_string + line_format(str(result))
    return output_string


def print_id(i, output_string):
    return output_string + line_format(str(i + 1))


def get_random_user_id(users: [User]):
    return random.randint(0, len(users) - 1) + 1


def get_random_user_address(users: [User]):
    return users[random.randint(0, len(users) - 1)].address


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


def define_all_tables(count=10):
    users = generate_users(count)
    user_table_name = "users"
    newsletter_table_name = "newsletter"
    orders_table_name = "orders"
    user_columns = ["id", "Username", "Password", "Name", "Address"]
    newsletter_columns = ["id", "email", "subscribed"]
    orders_columns = ["id", "products", "order_date", "delivery_address", "orderedBy"]

    order_functions = [lambda: get_random_product(),
                       lambda: random_date(),
                       lambda: get_random_adress_and_ordered_by(users)]

    create_table(user_table_name, user_columns)
    create_table(newsletter_table_name, newsletter_columns)
    create_table(orders_table_name, orders_columns)

    populate_table_from_users(user_table_name, users, user_columns, ["id", "username", "password", "name", "address"])
    populate_table_from_users(newsletter_table_name, users, newsletter_columns, ["id", "email", "subscribed"])
    populate_table_from_functions(orders_table_name, order_functions, orders_columns, count * 5)


if __name__ == "__main__":
    define_all_tables(20)
