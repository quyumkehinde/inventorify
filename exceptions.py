class AlreadyExistError(Exception):
    def __init__(self, message='Resource already exist.'):
        self.message = message
