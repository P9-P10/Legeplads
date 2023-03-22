import time

from Scripts.Helpers.Database_seeder_helper import *
from Scripts.Helpers.database_seeder_formatters import *

column_type_map = {"subscribed": "BOOL",
                   "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
                   "order_date": "DATETIME",
                   "orderedBy": "INT",
                   "birthday": "DATETIME",
                   "objection": "BOOL",
                   "automated_decisionmaking": "BOOL"}

API_LIMIT = 5000
SLEEP_TIME = 5


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
        output_string = apply_functions_and_format_values(functions, i, id_first, output_string)

    output_string = end_of_values_format(output_string)
    return output_string


def apply_functions_once_without_formatting(table_name, functions, columns):
    output_string = insert_into(columns, table_name)
    output_string = apply_functions_without_formatting(functions, output_string)
    return output_string


def apply_functions_without_formatting(functions, output_string: str):
    for f in functions:
        output_string = apply_function(f, output_string)
        output_string = remove_last_comma(output_string.rstrip())
    return output_string


def apply_functions_and_format_values(functions, i, id_first, output_string):
    output_string = output_string + "("
    if id_first:
        output_string = print_id(i, output_string)
    for f in functions:
        output_string = apply_function(f, output_string)
    output_string = end_of_line_format(output_string)
    return output_string


def apply_function(f, output_string):
    result = f()
    if isinstance(result, tuple):
        for i in result:
            output_string += value_seperator(str(i))
    else:
        output_string += value_seperator(str(result))
    return output_string


def drop_table(table):
    return "DROP TABLE IF EXISTS " + table + "; \n"


def define_all_tables(count=10, should_drop_table=False, verbose=True):
    users = []
    second_user_list = []
    if count > API_LIMIT:
        steps = round(count / API_LIMIT)

        if verbose:
            print(
                f"The process will fetch {steps} * {API_LIMIT}, each step will take approximately {SLEEP_TIME * 2} seconds.")

        for i in range(0, steps):
            if len(users) >= count:
                continue
            if verbose:
                print(f"Fetching {i + 1} out of {steps} in batches of 5000 users.")

            users.extend(generate_users(API_LIMIT))
            time.sleep(SLEEP_TIME)
            second_user_list.extend(generate_users(API_LIMIT))
            time.sleep(SLEEP_TIME)

    else:
        users = generate_users(count)
        second_user_list = generate_users(count)

    user_table_name = "users"
    newsletter_table_name = "newsletter"
    orders_table_name = "orders"
    metadata_table_name = "gdpr_metadata"
    user_metadata_table_name = "user_metadata"
    user_columns = ["id", "Username", "Password", "Name", "Address", "Creation_date"]
    newsletter_columns = ["id", "email", "subscribed"]
    orders_columns = ["id", "products", "order_date", "delivery_address", "orderedBy"]
    metadata_columns = ["id", "purpose", "ttl", "target_table", "target_column", "origin", "start_time",
                        "legally_required"]
    user_metadata_columns = ["id", "user_id", "metadata_id", "objection", "automated_decisionmaking"]

    function_output = ""

    order_functions = [lambda: get_random_product(),
                       lambda: get_random_order_information(users)]

    user_metadata_functions = [lambda: generate_purpose_rows(users)]
    metadata_functions = [lambda: purpose_table_generator()]

    newsletter_functions = [lambda: generate_extra_newsletters(second_user_list)]

    if should_drop_table:
        function_output += drop_table(user_table_name)
        function_output += drop_table(newsletter_table_name)
        function_output += drop_table(orders_table_name)
        function_output += drop_table(metadata_table_name)
        function_output += drop_table(user_metadata_table_name)

    function_output += create_table(user_table_name, user_columns)
    function_output += create_table(newsletter_table_name, newsletter_columns)
    function_output += create_table(orders_table_name, orders_columns)
    function_output += create_table(user_metadata_table_name, user_metadata_columns)
    function_output += create_table(metadata_table_name, metadata_columns)

    function_output += populate_table_from_users(user_table_name, users, user_columns,
                                                 ["id", "username", "password", "name", "address", "created_at"])
    function_output += populate_table_from_users(newsletter_table_name, users, newsletter_columns,
                                                 ["id", "email", "subscribed"])
    function_output += populate_table_from_functions(orders_table_name, order_functions, orders_columns, count * 5)
    # The below call ensures that there are more entries into newsletter than there are in users
    function_output += populate_table_from_functions(newsletter_table_name, newsletter_functions, newsletter_columns,
                                                     count,
                                                     start_id=count + 1)

    function_output += apply_functions_once_without_formatting(user_metadata_table_name, user_metadata_functions,
                                                               user_metadata_columns)

    function_output += apply_functions_once_without_formatting(metadata_table_name, metadata_functions,
                                                               metadata_columns)

    return function_output


if __name__ == "__main__":
    should_print = False
    filepath = "sqlite.sql"
    output = define_all_tables(100, True)
    if should_print:
        print(output)
    else:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(output)
