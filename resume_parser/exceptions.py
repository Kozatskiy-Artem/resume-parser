class ResumeNotFoundError(Exception):
    """Exception raised when resume candidates are not found for the query or search parameters"""

    def __init__(self, message: str = "Resume candidates were not found for the query or search parameters"):
        super().__init__(message)
