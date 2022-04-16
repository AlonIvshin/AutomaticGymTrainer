class Feedback:
    def __init__(self, feedback_id, user_id, exercise_id, date, score, reps):
        self.feedback_id = feedback_id
        self.user_id = user_id
        self.exercise_id = exercise_id
        self.date = date
        self.score = score
        self.reps = reps


class FeedbackHistory:
    def __init__(self, feedback_id, exercise_name, date, score, reps):
        self.feedback_id = feedback_id
        self.exercise_name = exercise_name
        self.date = date
        self.score = score
        self.reps = reps
