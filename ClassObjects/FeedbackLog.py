class FeedbackLog:
    def __init__(self, log_id, feedback_id, alert_id, stage_number, rep_number) -> None:
        self.log_id, = log_id,
        self.feedback_id = feedback_id
        self.alert_id = alert_id
        self.stage_number = stage_number
        self.rep_number = rep_number
