import psycopg2


class getInstanceDBConnection:
    con = None

    def getConnectionInstance(self):
        if self.con == None:
            self.con = psycopg2.connect(
                host="127.0.0.1",
                database="AutomaticGymTrainerLocal",
                user="postgres",
                password="012net")
        return self.con


con = getInstanceDBConnection().getConnectionInstance()


def getAllExerciseInstructionData(exerciseId):
    cur = con.cursor()
    cur.execute('''select e.exercise_instruction_id,e.instruction_id,e.alert_id,e.deviation_positive,e.deviation_negative,
    e.instruction_stage,e.exercise_instruction_type,e.alert_deviation_trigger, e.alert_extended_id
    from exercises_instructions as e
    where e.exercise_id = %s''', str(exerciseId))
    res = cur.fetchall()
    cur.close()
    return res


def getAllExerciseStages(exerciseId):
    # QUERY 2: getting exercise's stages number
    cur = con.cursor()
    cur.execute('select num_of_stages from exercises where exercise_id = %s', str(exerciseId))
    res = cur.fetchall()
    cur.close()
    return res


def getAllInstructionData(exerciseId):
    cur = con.cursor()
    # QUERY 3: getting all instruction's data of the exercise
    cur.execute('''select i.instruction_id,i.vertex1,i.vertex2,i.vertex3,i.angle,i.description,i.instruction_axis
    from instructions as i
    inner join exercises_instructions as ei on i.instruction_id=ei.instruction_id
    where ei.exercise_id = %s''', str(exerciseId))
    res = cur.fetchall()
    cur.close()
    return res


def getAllAlertsData(exerciseId):
    cur = con.cursor()
    # QUERY 4: getting all alert's data of the exercise
    cur.execute('''select a.alert_id,a.instruction_id,a.alert_text,a.alert_wrong_posture_image_link
    from alerts as a
    inner join exercises_instructions as ei on a.instruction_id=ei.instruction_id
    where ei.exercise_id = %s''', str(exerciseId))
    res = cur.fetchall()
    cur.close()
    return res


def getExerciesNamesAndTarget():
    cur = con.cursor()
    # QUERY 5: geting exercie id name and target in order to fill a table
    cur.execute('''select exercise_id,exercise_name,main_target from exercises''')
    res = cur.fetchall()
    cur.close
    return res


def insertIntoUsers(password, first_name, last_name, email, phoneNumber):
    try:
        cur = con.cursor()
        # QUERY 6: insert new trainee user
        sql = '''INSERT INTO users (password, first_name, last_name, email, type, "phoneNumber")
    VALUES (%s,%s,%s,%s,%s,%s);'''
        cur.execute(sql, (password, first_name, last_name, email, "trainee", phoneNumber))
        con.commit()
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


def isEmailExist(email):
    try:
        cur = con.cursor()
        # QUERY 7: check if the email address is already in use
        # sql = 'Select count(email) from users where email = %s'
        cur.execute("Select count(email) from users where email = %s", (email,))
        res = cur.fetchall()
        cur.close()
        return res[0][0]
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


def checkLoginData(email, password):
    try:
        con = getInstanceDBConnection().getConnectionInstance()
        cur = con.cursor()
        # QUERY 8: check id user login input is correct
        cur.execute("select password from users where email = %s ", (email,))
        res = cur.fetchall()
        cur.close()
        return res[0][0]
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


def checkIfAlreadyLogedin(email):
    try:
        con = getInstanceDBConnection().getConnectionInstance()
        cur = con.cursor()
        # QUERY 9: check if this email is logein
        cur.execute("select logged_in from users where email = %s", (email,))
        res = cur.fetchall()
        cur.close()
        return res
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


def changeToLoggedIn(email):
    try:
        cur = con.cursor()
        # QUERY 10: change logged_in to 1
        cur.execute("UPDATE users SET logged_in = 0 WHERE email = %s;", (email,)) #''' OFIRRRRRRRRRRRRRRRRRRR ALON OFIR'''
        con.commit()
        cur.close()
        return True
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


def getUser(email):
    try:
        cur = con.cursor()
        # QUERY 11: get user data
        cur.execute(
            "select user_id, password, first_name, last_name, email, type, phone_number from users where email = %s;",
            (email,))
        res = cur.fetchall()
        cur.close()
        return res
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


def getExerciseImages(exerciseId):
    cur = con.cursor()
    # QUERY 12: get all images for specific exercise
    # sql = 'select image from stage_images where stage_images.exercise_id = '1''
    cur.execute('''select image from stage_images where stage_images.exercise_id = %s''', str(exerciseId))
    res = cur.fetchall()
    cur.close()
    return res


def logOutCurrentUser(user_id):
    try:
        cur = con.cursor()
        # QUERY 13: change logged_in to 0
        cur.execute("UPDATE users SET logged_in = 0 WHERE user_id = %s;", (user_id,))
        con.commit()
        cur.close()
        return True
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


def getVideoId(exercise_id):
    try:
        cur = con.cursor()
        # QUERY 14: get Youtube video id
        cur.execute("select video from exercises where exercise_id = %s;", str(exercise_id))
        res = cur.fetchall()
        cur.close()
        return res[0][0]
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


def getExerciseDescription(exercise_id):
    try:
        cur = con.cursor()
        # QUERY 15: get user data
        cur.execute("select description from exercises where exercise_id = %s;", str(exercise_id))
        res = cur.fetchall()
        cur.close()
        return res[0][0]
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


def closeConnection():
    con.close()
