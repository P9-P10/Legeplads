
def apply_user_data(key, output_string, user):
    return output_string + line_format(str(getattr(user, key)))

def generate_row_creation(output_string, column_name, column_type):
    output_string = output_string + "\n  "
    return output_string + column_name + " " + column_type + ","

def remove_last_comma(output_string):
    return output_string[:-1]

def line_format(input_string):
    return input_string + ", "

def end_of_line_format(output_string):
    return output_string[:-2] + "),\n"


def insert_into(columns, table_name):
    output_columns = ','.join(columns)
    output_string = "INSERT INTO " + table_name + f" ({output_columns}) VALUES\n"
    return output_string

def end_of_values_format(output_string):
    return output_string[:-2] + ";\n\n"



def print_id(i, output_string):
    return output_string + line_format(str(i + 1))

