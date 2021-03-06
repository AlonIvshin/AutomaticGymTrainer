import psycopg2


class getInstanceDBConnection:
    con = None

    def getConnectionInstance(self):
        if self.con == None:
            self.con = psycopg2.connect(
                host="127.0.0.1",
                database="mytrainer",
                user="postgres",
                password="root")
        return self.con


con = getInstanceDBConnection().getConnectionInstance()


def closeConnection():
    con.close()


def getAllExerciseInstructionData(exerciseId):
    cur = con.cursor()
    cur.execute(f'''select e.exercise_instruction_id,e.instruction_id,e.alert_id,e.deviation_positive,e.deviation_negative,
    e.instruction_stage,e.exercise_instruction_type,e.alert_deviation_trigger, e.alert_extended_id
    from exercises_instructions as e
    where e.exercise_id = '{str(exerciseId)}'; ''')
    res = cur.fetchall()
    cur.close()
    return res


# QUERY 2: getting exercise's stages number
def getAllExerciseStages(exerciseId):
    cur = con.cursor()
    cur.execute('select num_of_stages from exercises where exercise_id = %s', str(exerciseId))
    res = cur.fetchall()
    cur.close()
    return res


# QUERY 3: getting all instruction's data of the exercise
def getAllInstructionData(exerciseId):
    cur = con.cursor()
    cur.execute('''select i.instruction_id,i.vertex1,i.vertex2,i.vertex3,i.angle,i.description,i.instruction_axis
    from instructions as i
    inner join exercises_instructions as ei on i.instruction_id=ei.instruction_id
    where ei.exercise_id = %s''', str(exerciseId))
    res = cur.fetchall()
    cur.close()
    return res


# QUERY 4: getting all alert's data of the exercise
def getAllAlertsData(exerciseId):
    cur = con.cursor()
    cur.execute(f'''select a.alert_id,a.instruction_id,a.alert_text,a.alert_wrong_posture_image_link
    from alerts as a
    inner join exercises_instructions as ei on a.instruction_id=ei.instruction_id
    where ei.exercise_id = '{str(exerciseId)}'; ''')
    res = cur.fetchall()
    cur.close()
    return res


# QUERY 5: geting exercie id name and target in order to fill a table
def getExerciesNamesAndTarget():
    cur = con.cursor()
    cur.execute('''select exercise_id,exercise_name,main_target from exercises''')
    res = cur.fetchall()
    cur.close
    return res


# QUERY 6: insert new trainee user
def insertIntoUsers(password, first_name, last_name, email, phone_number):
    try:
        cur = con.cursor()
        sql = '''INSERT INTO users (password, first_name, last_name, email, type, "phone_number")
    VALUES (%s,%s,%s,%s,%s,%s);'''
        cur.execute(sql, (password, first_name, last_name, email, "trainee", phone_number))
        con.commit()
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


# QUERY 7: check if the email address is already in use
def isEmailExist(email):
    try:
        cur = con.cursor()
        # sql = 'Select count(email) from users where email = %s'
        cur.execute("Select count(email) from users where email = %s", (email,))
        res = cur.fetchall()
        cur.close()
        return res[0][0]
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


# QUERY 8: check id user login input is correct
def checkLoginData(email, password):
    try:
        con = getInstanceDBConnection().getConnectionInstance()
        cur = con.cursor()
        cur.execute("select password from users where email = %s ", (email,))
        res = cur.fetchall()
        cur.close()
        return res[0][0]
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


# QUERY 9: check if this email is loged in
def checkIfAlreadyLogedin(email):
    try:
        con = getInstanceDBConnection().getConnectionInstance()
        cur = con.cursor()
        cur.execute("select logged_in from users where email = %s", (email,))
        res = cur.fetchall()
        cur.close()
        return res
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


# QUERY 10: change logged_in to 1
def changeToLoggedIn(email):
    try:
        cur = con.cursor()
        cur.execute("UPDATE users SET logged_in = 0 WHERE email = %s;",
                    (email,))  # ''' OFIRRRRRRRRRRRRRRRRRRR ALON OFIR'''
        con.commit()
        cur.close()
        return True
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


# QUERY 11: get user data
def getUser(email):
    try:
        cur = con.cursor()
        cur.execute(
            "select user_id, password, first_name, last_name, email, type, phone_number from users where email = %s;",
            (email,))
        res = cur.fetchall()
        cur.close()
        return res
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


# QUERY 12: get all images for specific exercise
def getExerciseImages(exerciseId):
    cur = con.cursor()
    # sql = 'select image from stage_images where stage_images.exercise_id = '1''
    cur.execute('''select stage_number,image from stage_images where stage_images.exercise_id = %s''', str(exerciseId))
    res = cur.fetchall()
    cur.close()
    return res


# QUERY 13: change logged_in to 0
def logOutCurrentUser(user_id):
    try:
        cur = con.cursor()
        cur.execute("UPDATE users SET logged_in = 0 WHERE user_id = %s;", (user_id,))
        con.commit()
        cur.close()
        return True
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


# QUERY 14: get Youtube video id
def getVideoId(exercise_id):
    try:
        cur = con.cursor()
        cur.execute("select video from exercises where exercise_id = %s;", str(exercise_id))
        res = cur.fetchall()
        cur.close()
        return res[0][0]
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


# QUERY 15: get user data
def getExerciseDescription(exercise_id):
    try:
        cur = con.cursor()
        cur.execute("select description from exercises where exercise_id = %s;", str(exercise_id))
        res = cur.fetchall()
        cur.close()
        return res[0][0]
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


# QUERY 16: get feedback score
def getFeedbackScore(feedback_id):  # OFIR
    try:
        cur = con.cursor()
        cur.execute(f"select score from feedbacks where feedback_id = {feedback_id};")
        res = cur.fetchall()
        cur.close()
        return res[0][0]
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


# QUERY 17: receiving all feedback log data during the workout session
def getFeedbackLogData(feedback_id):
    cur = con.cursor()
    cur.execute(f'''select alert_text,stage_number,rep_number from alerts as a 
                    Join feedbacks_logs as f on a.alert_id = f.alert_id where feedback_id = {feedback_id};''')
    res = cur.fetchall()
    cur.close
    return res


# QUERY 18: get all feedbacks data needed of the current user ordered by date
def getCurrentUserFeedbacks(current_user):
    try:
        cur = con.cursor()
        cur.execute('''select f.feedback_id, e.exercise_name, f.date, f.score, f.reps from feedbacks as f
                        join exercises as e on f.exercise_id = e.exercise_id
                        where user_id = %s order by date DESC;''', (current_user,))
        res = cur.fetchall()
        cur.close()
        return res
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


# QUERY 19: get how many workouts the user preformed
def getWorkoutsQuantity(current_user):
    try:
        cur = con.cursor()
        cur.execute('''select count(*) from feedbacks as f
                         join exercises as e on f.exercise_id = e.exercise_id
                         where user_id = %s;''', (current_user,))
        res = cur.fetchall()
        cur.close()
        return res[0][0]
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


# QUERY 20: get users workouts AVG
def getWorkoutsAVG(current_user):
    try:
        cur = con.cursor()
        cur.execute('''select cast(avg(score) as decimal(10,2)) from feedbacks as f
                         join exercises as e on f.exercise_id = e.exercise_id
                         where user_id = %s;''', (current_user,))
        res = cur.fetchall()
        cur.close()
        return res[0][0]
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


# QUERY 21: create new feedback
def createFeedBack(feedback):
    feedback_id = 0
    try:
        cur = con.cursor()
        sql = '''INSERT INTO feedbacks (user_id, exercise_id, date, score, reps)
    VALUES (%s,%s,%s,%s,%s) RETURNING feedback_id;'''
        cur.execute(sql, (
            feedback.user_id, feedback.exercise_id, feedback.date, feedback.score, feedback.reps))
        con.commit()
        feedback_id = int(cur.fetchall()[0][0])
        cur.close()
        return feedback_id
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


# QUERY 22: insert logs to feedback
def createNewFeedbackLogs(error_list_logs):
    # Pre-process data to a proper string format

    sql = "INSERT INTO feedbacks_logs (feedback_id, alert_id, stage_number, rep_number) VALUES "
    for item in error_list_logs:
        sql = sql + f"({item.feedback_id},{item.alert_id},{item.stage_number},{item.rep_number}),"
    sql = sql[:-1]  # to remove last ','
    try:
        cur = con.cursor()
        cur.execute(sql)
        con.commit()
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


# ALON - to change name
def getImageForFeedback(feedback_id):
    try:
        cur = con.cursor()
        cur.execute('''select s.image from stage_images as s
            join feedbacks as f on s.exercise_id = f.exercise_id where f.feedback_id = %s
            limit 1''', (feedback_id,))
        res = cur.fetchall()
        cur.close()
        return res[0][0]
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


# QUERY 23: Get exercise
def getExercise(eid):
    cur = con.cursor()
    cur.execute(f'''select * from exercises where exercise_id = {eid}''')
    res = cur.fetchall()
    cur.close
    return res


# QUERY 24: Insert new exercise
def addNewExercise(exercise):
    cur = con.cursor()
    sql = f'''INSERT INTO exercises (exercise_name, video, description, num_of_stages, main_target) 
        VALUES ('{exercise.exercise_name}','{exercise.video}','{exercise.description}','{exercise.num_of_stages}','{exercise.main_target}');'''
    cur.execute(sql)
    con.commit()
    cur.close
    return True  # for successes


# QUERY 25: Get max stage instruction in a given exercise
def getMaxStageInExercise(exercise_id):
    cur = con.cursor()
    sql = f'''select max(instruction_stage) from exercises_instructions where exercises_instructions.exercise_id = {exercise_id}; '''
    cur.execute(sql)
    res = cur.fetchall()
    if res[0][0] == None:
        return 0
    return res[0][0]


# QUERY 26: modify existing exercise
def modifyExercise(exercise):
    cur = con.cursor()
    sql = f'''UPDATE exercises SET exercise_name = '{exercise.exercise_name}', video = '{exercise.video}', description = '{exercise.description}', num_of_stages = '{exercise.num_of_stages}', main_target = '{exercise.main_target}' WHERE exercise_id = {exercise.exercise_id}; '''
    cur.execute(sql)
    con.commit()
    cur.close()
    return True


# QUERY 27: get all instructions
def getAllInstructions():
    cur = con.cursor()
    sql = '''select * FROM instructions'''
    cur.execute(sql)
    res = cur.fetchall()
    cur.close()
    return res


# QUERY 28: get specific instruction
def getInstruction(instruction_id):
    cur = con.cursor()
    sql = f'''select * FROM instructions where instruction_id = {instruction_id}'''
    cur.execute(sql)
    res = cur.fetchall()
    cur.close()
    return res


# QUERY 29: get specific instruction
def addNewInstruction(instruction):
    cur = con.cursor()
    sql = f'''INSERT INTO instructions (vertex1, vertex2, vertex3, angle, description,instruction_axis) 
           VALUES ('{instruction.vertex1}','{instruction.vertex2}','{instruction.vertex3}','{instruction.angle}','{instruction.description}','{instruction.instructionAxis}');'''
    cur.execute(sql)
    con.commit()
    cur.close
    return True  # for successes


# QUERY 30: check if instruction exist
def checkIfInstructionExist(instruction):
    cur = con.cursor()
    sql = f'''SELECT * from instructions where vertex1='{instruction.vertex1}' and vertex2='{instruction.vertex2}' and 
    vertex3 ='{instruction.vertex3}' and angle = '{instruction.angle}' and description = '{instruction.description}' and
    instruction_axis = '{instruction.instructionAxis}' '''
    cur.execute(sql)
    res = cur.fetchall()
    cur.close
    return res != []


# QUERY 31: modify existing instruction
def modifyInstruction(instruction):
    cur = con.cursor()
    sql = f'''UPDATE instructions SET vertex1='{instruction.vertex1}', vertex2='{instruction.vertex2}', 
    vertex3 ='{instruction.vertex3}', angle = '{instruction.angle}', description = '{instruction.description}',
    instruction_axis = '{instruction.instructionAxis}' WHERE instruction_id = {instruction.instructionId}; '''
    cur.execute(sql)
    con.commit()
    cur.close()
    return True


# QUERY 32: get all the alerts of the desired instruction
def getAlertsOfInstruction(instruction_id):
    cur = con.cursor()
    sql = f'''select * from alerts where instruction_id = {instruction_id}'''
    cur.execute(sql)
    res = cur.fetchall()
    cur.close()
    return res


# QUERY 33: Adds new alert
def addNewAlert(instruction_id, txt, link):
    cur = con.cursor()
    sql = f'''INSERT INTO alerts (instruction_id, alert_text, alert_wrong_posture_image_link) 
           VALUES ('{instruction_id}','{txt}','{link}');'''
    cur.execute(sql)
    con.commit()
    cur.close
    return True  # for successes


# QUERY 34: checks if this instruction exist
def checkIfInstructionExistAlerts(instruction_id):
    cur = con.cursor()
    sql = f'''SELECT * from instructions where instruction_id='{instruction_id}'  '''
    cur.execute(sql)
    res = cur.fetchall()
    cur.close
    return res == []


# QUERY 35: checks if this alert exist for particular instruction
def checkIfAlertExist(instruction_id, alert_text, link):
    cur = con.cursor()
    sql = f'''SELECT * from alerts where instruction_id='{instruction_id}' and alert_text='{alert_text}' and 
        alert_wrong_posture_image_link ='{link}' '''
    cur.execute(sql)
    res = cur.fetchall()
    cur.close
    return res != []


# QUERY 37 drops row from alerts
def delAlert(alert_id):
    cur = con.cursor()
    sql = f'''DELETE FROM alerts WHERE alert_id = '{alert_id}';'''
    cur.execute(sql)
    con.commit()
    cur.close
    return True  # for successes


# QUERY 38 update alert
def modifyAlert(alert_id, alert_text, link):
    cur = con.cursor()
    sql = f'''UPDATE alerts SET alert_text='{alert_text}', alert_wrong_posture_image_link='{link}' WHERE alert_id = '{alert_id}'; '''
    cur.execute(sql)
    con.commit()
    cur.close()
    return True


# QUERY 39: insert specific exercise  instruction
def addNewExerciseInstruction(exercise_instruction):
    cur = con.cursor()
    sql = f'''INSERT INTO exercises_instructions (exercise_id, instruction_id, alert_id, deviation_positive, deviation_negative,instruction_stage,exercise_instruction_type,alert_deviation_trigger,alert_extended_id) 
           VALUES ('{exercise_instruction.exerciseId}',
           '{exercise_instruction.instructionId}','{exercise_instruction.alertId}','{exercise_instruction.deviationPositive}',
           '{exercise_instruction.deviationNegative}','{exercise_instruction.instructionStage}','{exercise_instruction.exerciseInstructionType}',
           '{exercise_instruction.alertDeviationTrigger}','{exercise_instruction.alertExtendedId}');'''
    cur.execute(sql)
    con.commit()
    cur.close
    return True  # for successes


# QUERY 40: select alerts that contain 3 vertices
def getAllAlertsFor3Vertices(vertex1, vertex2, vertex3):
    cur = con.cursor()
    sql = f'''select * from alerts where instruction_id in (
            select instruction_id from instructions where (vertex1 = '{vertex1}' and vertex3 ='{vertex3}') or 
            (vertex3 = '{vertex1}' and vertex1 = '{vertex3}') and vertex2 ='{vertex2}')'''
    cur.execute(sql)
    res = cur.fetchall()
    cur.close()
    return res


# QUERY 41: Search if there are any existing alerts for instruction
def getAlertsForInstruction(instruction_id):
    cur = con.cursor()
    sql = f'''select * from alerts where instruction_id = '{instruction_id}'; '''
    cur.execute(sql)
    res = cur.fetchall()
    cur.close()
    return res != []


# QUERY 42: Search if there are any existing Exercise instructions for instruction
def getExerciseInstructionsForInstruction(instruction_id):
    cur = con.cursor()
    sql = f'''select * from exercises_instructions where instruction_id = '{instruction_id}'; '''
    cur.execute(sql)
    res = cur.fetchall()
    cur.close()
    return res != []


# QUERY 43 drops row from instructions
def deleteInstruction(instruction_id):
    cur = con.cursor()
    sql = f'''DELETE FROM instructions WHERE instruction_id = '{instruction_id}';'''
    cur.execute(sql)
    con.commit()
    cur.close
    return True  # for successes


# QUERY 44 drop row from exercise instructions
def deleteExerciseInstruction(exercise_instruction_id):
    cur = con.cursor()
    sql = f'''DELETE FROM exercises_instructions WHERE exercise_instruction_id = '{exercise_instruction_id}';'''
    cur.execute(sql)
    con.commit()
    cur.close
    return True  # for successes


# QUERY 46
def deleteExercise(exercise_id):
    cur = con.cursor()
    sql = f'''DELETE FROM exercises WHERE exercise_id = '{exercise_id}';'''
    cur.execute(sql)
    con.commit()
    cur.close
    return True


# Query 47 Exercise
def getMaxStageForExercise(exercise_id):
    cur = con.cursor()
    sql = f"select num_of_stages from exercises where exercise_id = '{exercise_id}'"
    cur.execute(sql)
    res = cur.fetchall()
    return res


# Query 48
def insertNewStageImage(e_id, stage_num, link):
    cur = con.cursor()
    sql = f'''INSERT INTO stage_images (exercise_id, stage_number, image) 
           VALUES ('{e_id}','{stage_num}','{link}');'''
    cur.execute(sql)
    con.commit()
    cur.close
    return True


# Query 49
def stageImageExist(e_id, stage_num):
    cur = con.cursor()
    sql = f'''select * from stage_images where exercise_id = '{e_id}' and stage_number = '{stage_num}';'''
    cur.execute(sql)
    res = cur.fetchall()
    cur.close()
    return res != []


# Query 50
def exerciseExist(exercise):
    cur = con.cursor()
    sql = f'''select * from exercises where exercise_name = '{exercise.exercise_name}' and 
       video = '{exercise.video}' and description ='{exercise.description}' and num_of_stages = '{exercise.num_of_stages}' and main_target = '{exercise.main_target}'; '''
    cur.execute(sql)
    res = cur.fetchall()
    cur.close()
    return res != []


# Query 51
def instructionExist(instruction):
    cur = con.cursor()
    sql = f'''select * from instructions where vertex1 = '{instruction.vertex1}' and 
    vertex2 = '{instruction.vertex2}' and vertex3 = '{instruction.vertex3}' and 
    angle = '{instruction.angle}' and description= '{instruction.description}' and
     instruction_axis = '{instruction.instructionAxis}';'''
    cur.execute(sql)
    res = cur.fetchall()
    cur.close()
    return res != []


# Query 52
def exerciseInstructionExist(exercise_instruction):
    cur = con.cursor()
    sql = f'''select * from exercises_instructions where exercise_id = '{exercise_instruction.exerciseId}' and instruction_id ='{exercise_instruction.instructionId}'
     and alert_id = '{exercise_instruction.alertId}' and deviation_positive ='{exercise_instruction.deviationPositive}' and
      deviation_negative = '{exercise_instruction.deviationNegative}' and instruction_stage = '{exercise_instruction.instructionStage}' and
      exercise_instruction_type = '{exercise_instruction.exerciseInstructionType}' and alert_deviation_trigger = '{exercise_instruction.alertDeviationTrigger}' 
      and alert_extended_id = '{exercise_instruction.alertExtendedId}';'''
    cur.execute(sql)
    res = cur.fetchall()
    cur.close()
    return res != []


# Query 53
def deleteStageImage(e_id, stage_num):
    cur = con.cursor()
    sql = f'''DELETE FROM stage_images WHERE exercise_id = '{e_id}' and stage_number = '{stage_num}';'''
    cur.execute(sql)
    con.commit()
    cur.close
    return True
