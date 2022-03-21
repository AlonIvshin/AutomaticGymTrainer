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
    cur.execute('''select a.alert_id,a.instruction_id,a.alert_text
    from alerts as a
    inner join exercises_instructions as ei on a.instruction_id=ei.instruction_id
    where ei.exercise_id = %s''', str(exerciseId))
    res = cur.fetchall()
    cur.close()
    return res


def closeConnection():
    con.close()
