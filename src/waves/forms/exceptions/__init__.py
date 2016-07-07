from waves.exceptions import WavesException


__all__ = ['WrongFieldDescriptionException', 'NoInputException']


class FormException(WavesException):
    def __init__(self, input, *args, **kwargs):
        super(FormException, self).__init__(*args, **kwargs)


class WrongFieldDescriptionException(FormException):
    pass


class NoInputException(FormException):
    pass
