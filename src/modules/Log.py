"""
Log Class
"""
class Log:
    def __init__(self, LogID: str, JobID: str, LogDate: str, Status: str, Message: str):
        self.LogID = LogID
        self.JobID = JobID
        self.LogDate = LogDate
        self.Status = Status
        self.Message = Message

    def toJson(self):
        return {
            "LogID": self.LogID,
            "JobID": self.JobID,
            "LogDate": self.LogDate,
            "Status": self.Status,
            "Message": self.Message
        }

    def __dict__(self):
        return self.toJson()