import time

from Scripts.Helpers.Database_seeder_helper import *
from Scripts.Helpers.database_seeder_formatters import *

column_type_map = {"subscribed": "BOOL",
                   "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
                   "order_date": "DATETIME",
                   "orderedBy": "INT",
                   "birthday": "DATETIME"}

API_LIMIT = 5000


def create_table(table_name, column_type: [str]):
    output_string = "CREATE TABLE " + table_name + "("
    for column_name in column_type:
        if column_name in column_type_map:
            output_string = generate_row_creation(output_string, column_name, column_type_map[column_name])
        else:
            output_string = generate_row_creation(output_string, column_name, "VARCHAR(256)")
    output_string = remove_last_comma(output_string)
    output_string = output_string + "\n); \n \n"

    return output_string


def populate_table_from_users(table_name, users: [User], columns: [str], user_properties: [str]):
    output_string = insert_into(columns, table_name)
    for user in users:
        output_string = output_string + "  ("
        for property in user_properties:
            output_string = apply_user_data(property, output_string, user)
        output_string = end_of_line_format(output_string)
    output_string = end_of_values_format(output_string)
    return output_string


def populate_table_from_functions(table_name, functions: [], columns: [str], count: int, id_first=True, start_id=0):
    output_string = insert_into(columns, table_name)

    count = start_id + count

    for i in range(start_id, count):
        output_string = output_string + "("
        if id_first:
            output_string = print_id(i, output_string)
        for f in functions:
            output_string = apply_function(f, output_string)
        output_string = end_of_line_format(output_string)
    output_string = end_of_values_format(output_string)
    return output_string


def apply_function(f, output_string):
    result = f()
    if isinstance(result, tuple):
        output_string += line_format(str(result[0])) + line_format(str(result[1]))
    else:
        output_string += line_format(str(result))
    return output_string


def drop_table(table):
    return "DROP TABLE IF EXISTS " + table + "; \n"


def define_all_tables(count=10, should_drop_table=False):
    users = []
    second_user_list = []
    if count > API_LIMIT:
        steps = round(count / API_LIMIT)

        for i in range(0, steps):
            if len(users) >= count:
                continue
            users.append(generate_users(API_LIMIT))
            second_user_list = get_random_user(API_LIMIT)
            time.sleep(1)

    else:
        users = generate_users(count)
        second_user_list = generate_users(count)

    user_table_name = "users"
    newsletter_table_name = "newsletter"
    orders_table_name = "orders"
    user_columns = ["id", "Username", "Password", "Name", "Address"]
    newsletter_columns = ["id", "email", "subscribed"]
    orders_columns = ["id", "products", "order_date", "delivery_address", "orderedBy"]
    output = ""

    order_functions = [lambda: get_random_product(),
                       lambda: random_date(),
                       lambda: get_random_adress_and_ordered_by(users)]

    newsletter_functions = [lambda: generate_extra_newsletters(second_user_list)]

    if should_drop_table:
        output += drop_table(user_table_name)
        output += drop_table(newsletter_table_name)
        output += drop_table(orders_table_name)

    output += create_table(user_table_name, user_columns)
    output += create_table(newsletter_table_name, newsletter_columns)
    output += create_table(orders_table_name, orders_columns)

    output += populate_table_from_users(user_table_name, users, user_columns,
                                        ["id", "username", "password", "name", "address"])
    output += populate_table_from_users(newsletter_table_name, users, newsletter_columns, ["id", "email", "subscribed"])
    output += populate_table_from_functions(orders_table_name, order_functions, orders_columns, count * 5)
    # The below call ensures that there are more entries into newsletter than there are in users
    output += populate_table_from_functions(newsletter_table_name, newsletter_functions, newsletter_columns, count,
                                            start_id=count)

    return output


if __name__ == "__main__":
    should_print = False
    filepath = "output.sql"
    output = define_all_tables(5000, True)
    if should_print:
        print(output)
    else:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(output)
