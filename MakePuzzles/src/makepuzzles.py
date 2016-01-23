from PIL import Image
import random
import io
from mysql.connector import MySQLConnection, Error
from python_mysql_dbconfig import read_db_config


def write_file(data, filename):
    with open(filename, 'wb') as f:
        f.write(data)

def update_blob(id, data):
    query = "UPDATE Puzzles " \
            "SET puzzledata = %s " \
            "WHERE puzzleid  = %s"
 
    args = (data, id)
    db_config = read_db_config()
 
    try:
        conn = MySQLConnection(**db_config)
        cursor = conn.cursor()
        cursor.execute(query, args)
        conn.commit()
    except Error as e:
        print(e)
    finally:
        cursor.close()
        conn.close()
        
def write_puzzle(x, y, im, name):
    w, h = im.size
    dx = int(w/x)
    dy = int(h/y)
    pieces = []
    for i in range(0,w-dx,dx):
        for j in range(0,h-dy,dy):
            pieces.append(im.crop((i, j, i+dx, j+dy)))
    #print(len(pieces))
    random.shuffle(pieces)
    random.shuffle(pieces)
    new_im = Image.new('RGB', (x*dx,y*dy))
    index = 0
    for i in range(0,w-dx,dx):
        for j in range(0,h-dy,dy):
            new_im.paste(pieces[index], (i , j))
            index+=1
    return new_im

def read_blob(puzzles):
    query = """ SELECT puzzleid, horizontalelements, verticalelements, picturedata
                FROM
                (
                SELECT *
                FROM
                (
                SELECT puzzleid, picture, complexity
                FROM Puzzles
                WHERE puzzleid IN (%s)) AS select1
                JOIN Complexity ON complexity=complexityid) AS select2
                JOIN Pictures ON picture=pictureid"""

    # read database configuration
    db_config = read_db_config()
 
    try:
        conn = MySQLConnection(**db_config)
        cursor = conn.cursor()
        in_p=', '.join(map(lambda x: '%s', puzzles))
        query = query % in_p
        cursor.execute(query, puzzles)
        for record in cursor:
            puzzleid, horizontalelements, verticalelements, picturedata = record
            filename = str(puzzleid) + ".jpg"
            write_file(picturedata, filename)
            puzzle = write_puzzle(horizontalelements, verticalelements, Image.open(io.BytesIO(picturedata)), puzzleid)
            imgByteArr = io.BytesIO()
            puzzle.save(imgByteArr, format='JPEG')
            imgByteArr = imgByteArr.getvalue()
            update_blob(puzzleid, imgByteArr)
 
    except Error as e:
        print(e)
 
    finally:
        cursor.close()
        conn.close()

############################################################

read_blob(list(range(10,11)))
print("ok")
#im = Image.open("10.jpg")
#x = 15
#y = 10
#write_puzzle(x, y, im, '10')