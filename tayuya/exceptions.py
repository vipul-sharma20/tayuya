from tayuya import constants


class TrackError(Exception):
    """
    Custom error for failure in handling of MIDI track
    """
    def __init__(self):
        self.msg = constants.TRACK_ERROR_MESSAGE

    def __str__(self):
        return repr(self.msg)

