DELETION_DISABLED_DETAIL = (
    "Deletion is disabled pending a secure administrative deletion policy"
)


class AdministrativeDeletionDisabled(RuntimeError):
    """Raised when an unresolved destructive operation is attempted."""

