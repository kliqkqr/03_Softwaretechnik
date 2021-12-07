from mysql.connector import connect, Error


# Resources: https://realpython.com/python-mysql/#creating-altering-and-dropping-a-table
class Speicher():

    def __init__(self):
        try:
            # The user needs to be connected to the UNI network before
            # being able to access the database
            # mysql -h mysql.hrz.tu-chemnitz.de -u Eyetracking_GR03_rw -p Eyetracking_GR03
            with connect(
                host="mysql.hrz.tu-chemnitz.de",
                user="Eyetracking_GR03_rw",
                password="Eyetracking_GR03",
            ) as self.connection:
                # Insert creation of the tables here:
                create_cc_table_query = """
                    CREATE TABLE IF NOT EXISTS Eyetracking_GR03.CodeCharts (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        image_id INT, 
                        eye_position_x INT,
                        eye_position_y INT
                    )
                """
                with self.connection.cursor() as cursor:
                    cursor.execute(create_cc_table_query)
                    self.connection.commit()

                # Checkup
                show_table_query = "DESCRIBE Eyetracking_GR03.CodeCharts"
                with self.connection.cursor() as cursor:
                    cursor.execute(show_table_query)
                    # Fetch rows from last executed query
                    result = cursor.fetchall()
                    for row in result:
                        print(row)

            # connection is closed by the with statement
        except Error as e:
            print(e)


