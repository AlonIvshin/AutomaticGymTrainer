class Alerts:
    def __init__(self, alertId, alertInstructionId, alertText,alert_wrong_posture_image_link = None) -> None:
        self.alertId = alertId
        self.alertInstructionId = alertInstructionId
        self.alertText = alertText
        self.alert_wrong_posture_image_link = alert_wrong_posture_image_link
