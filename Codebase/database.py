from msilib.schema import Binary
import mysql.connector      # needs pip install mysql-connector-python

def saveCodeCharts(imageFilePath, eye_position_x, eye_position_y):
    # connect to mysql server   !!! works only within the TU Chemnitz network or via VPN Connection !!!
    conn = mysql.connector.connect(host = "mysql.hrz.tu-chemnitz.de", user = "Eyetracking_GR03_rw", passwd = "Duciev4j", database="Eyetracking_GR03")
    mycursor = conn.cursor()
    
    # create table
    mycursor.execute("CREATE TABLE IF NOT EXISTS CodeCharts (id int NOT NULL PRIMARY KEY AUTO_INCREMENT, image LONGBLOB NOT NULL, eye_position_x JSON, eye_position_y JSON)")

    # convert picture into BLOB
    with open(imageFilePath, "rb") as File:
        binaryData = File.read()
    
    # convert arrays to strings
    string_x = ",".join(map(str,eye_position_x))
    string_y = ",".join(map(str,eye_position_y))

    # execute sql commands
    mycursor.execute("INSERT INTO CodeCharts (image,eye_position_x,eye_position_y) VALUES (%s,%s,%s)", (binaryData, string_x, string_y))
    conn.commit()

    
def saveBubbleView(imageFilePath, eye_position_x, eye_position_y, timestamps, filter_used, geometry_used):
    # connect to mysql server
    conn = mysql.connector.connect(host = "mysql.hrz.tu-chemnitz.de", user = "Eyetracking_GR03_rw", passwd = "Duciev4j", database="Eyetracking_GR03")
    mycursor = conn.cursor()

    # create table
    mycursor.execute("CREATE TABLE IF NOT EXISTS BubbleView (id int NOT NULL PRIMARY KEY AUTO_INCREMENT, image LONGBLOB NOT NULL, eye_position_x JSON, eye_position_y JSON, timestamps JSON, filter_used JSON, geometry_used JSON)")

    # convert picture into BLOB
    with open(imageFilePath, "rb") as File:
        binaryData = File.read()
    
    # convert arrays to strings
    string_x = ",".join(map(str,eye_position_x))
    string_y = ",".join(map(str,eye_position_y))
    string_time = ",".join(map(str,timestamps))

    # execute sql commands
    mycursor.execute("INSERT INTO BubbleView (image,eye_position_x,eye_position_y,timestamps, filter_used, geometry_used) VALUES (%s,%s,%s,%s,%s,%s)", (binaryData, string_x, string_y, string_time, filter_used, geometry_used))
    conn.commit()


def getCodeCharts():
    # connect to mysql server
    conn = mysql.connector.connect(host = "mysql.hrz.tu-chemnitz.de", user = "Eyetracking_GR03_rw", passwd = "Duciev4j", database="Eyetracking_GR03")
    mycursor = conn.cursor()
    mycursor.execute("SELECT * FROM CodeCharts")

    # initialize return object
    result=[]

    # get Data from server
    row = mycursor.fetchone()
        
    while row is not None:
        id = row[0]                         # row is array
        image_data = row[1]
        string_x = row[2]
        string_x = string_x.decode("utf-8") # decode data from byte-like to string
        string_y = row[3]
        string_y = string_y.decode("utf-8")

        # convert strings to string arrays
        array_x = string_x.split(",")
        array_y = string_y.split(",")

        # convert string arrays to int arrays
        eye_position_x = [int(array_x) for array_x in array_x]
        eye_position_y = [int(array_y) for array_y in array_y]

        my_row = [id, image_data, eye_position_x, eye_position_y]
        result.append(my_row)

        row = mycursor.fetchone()
    
    return result


def getBubbleView():
    # connect to mysql server
    conn = mysql.connector.connect(host = "mysql.hrz.tu-chemnitz.de", user = "Eyetracking_GR03_rw", passwd = "Duciev4j", database="Eyetracking_GR03")
    mycursor = conn.cursor()
    mycursor.execute("SELECT * FROM BubbleView")

    # initialize return object
    result = []

    # get Data from server
    row = mycursor.fetchone()
        
    while row is not None:
        id = row[0]                                 # row is array of columns
        image_data = row[1]
        string_x = row[2]
        string_x = string_x.decode("utf-8")         # decode data from byte-like type to string
        string_y = row[3]
        string_y = string_y.decode("utf-8")
        string_time = row[4]
        string_time = string_time.decode("utf-8")
        filter_used = row[5]
        filter_used = filter_used.decode("utf-8")
        geometry_used = row[6]
        geometry_used = geometry_used.decode("utf-8")

        # convert strings to string arrays
        array_x = string_x.split(",")
        array_y = string_y.split(",")
        array_time = string_time.split(",")

        # convert string arrays to int or float arrays
        eye_position_x = [int(array_x) for array_x in array_x]
        eye_position_y = [int(array_y) for array_y in array_y]
        timestamps = [float(array_time) for array_time in array_time]

        my_row = [id, image_data, eye_position_x, eye_position_y, timestamps, filter_used, geometry_used]
        result.append(my_row)

        row = mycursor.fetchone()
    
    return result
