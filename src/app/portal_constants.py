from enum import Enum


class Statuses(Enum):
    """
    Constants to be used across entire portal.
    """
    Success = 'SUCCESS'
    Failed = 'FAILED'
    Exception = 'EXCEPTION'
