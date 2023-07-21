import db
import functions

connection = db.connect()

db.create_table(connection)
db.initialize_users(connection)
db.make_usage_for_name(connection, functions.conf_name)
# db.import_data(connection)
# db.new_user_register(connection)

connection.commit()
connection.close()

