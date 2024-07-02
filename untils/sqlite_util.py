import sqlite3
from dataclasses import dataclass, fields


def create_table_from_dataclass(connection, dataclass_type):
    table_name = dataclass_type.__name__.lower()
    field_definitions = []

    for field in fields(dataclass_type):
        if field.type == int:
            field_type = "INTEGER"
        elif field.type == float:
            field_type = "REAL"
        elif field.type == str:
            field_type = "TEXT"
        elif field.type == bool:
            field_type = "BOOLEAN"
        elif field.type == set:
            continue
        else:
            raise TypeError(f"Unsupported field type: {field.type}")
        definition = f"{field.name} {field_type}"
        if field.name == 'item_id':
            definition += ' primary key'
        field_definitions.append(definition)

    field_definitions_str = ", ".join(field_definitions)
    create_table_sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({field_definitions_str})"

    cursor = connection.cursor()
    cursor.execute(create_table_sql)
    connection.commit()


def insert_dataclass_instance(connection, instance):
    table_name = instance.__class__.__name__.lower()
    field_names = [field.name for field in fields(instance)]

    cols = []
    vals = []
    for name in field_names:
        v = getattr(instance, name)
        if v is None:
           continue
        cols.append(name)
        vals.append(f"'{str(v)}'")

    insert_sql = f"INSERT INTO {table_name} ({', '.join(cols)}) VALUES ({', '.join(vals)})"
    cursor = connection.cursor()
    cursor.execute(insert_sql, instance.__dict__)
    connection.commit()

