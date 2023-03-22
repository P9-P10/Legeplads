import datetime


def toSQLString(entry):
    return "'" + str(entry) + "'"


def fromSQLStringToDate(entry: str):
    return datetime.datetime.strptime(entry.replace("'", ''), '%Y-%m-%d %H:%M')


def apply_user_data(key, output_string, user):
    return output_string + value_seperator(str(getattr(user, key)))


def generate_row_creation(output_string, column_name, column_type):
    output_string = output_string + "\n  "
    return output_string + column_name + " " + column_type + ","


def remove_last_comma(output_string):
    return output_string[:-1]


def value_seperator(input_string):
    return str(input_string) + ", "


def end_of_line_format(output_string):
    return output_string[:-2] + "),\n"


def insert_into(columns, table_name):
    output_columns = ','.join(columns)
    output_string = "INSERT INTO " + table_name + f" ({output_columns}) VALUES\n"
    return output_string


def end_of_values_format(output_string):
    return output_string[:-2] + ";\n\n"


def print_id(i, output_string, start_with_paran=False):
    if start_with_paran:
        return output_string + "(" + value_seperator(str(i + 1))
    return output_string + value_seperator(str(i + 1))
