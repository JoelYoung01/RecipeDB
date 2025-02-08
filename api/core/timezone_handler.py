from datetime import timezone
from sqlalchemy import TypeDecorator, DateTime


class UTCDateTime(TypeDecorator):
    """
    Custom SQLAlchemy type that automatically handles UTC conversion
    for datetime fields when working with SQLite
    """

    impl = DateTime
    cache_ok = True

    def process_bind_param(self, value, dialect):
        """Convert datetime to UTC before storing in DB"""
        if value is not None:
            # If datetime has no timezone, assume it's UTC
            if value.tzinfo is None:
                value = value.replace(tzinfo=timezone.utc)
            # Convert to UTC if it's not already
            return value.astimezone(timezone.utc).replace(tzinfo=None)
        return value

    def process_result_value(self, value, dialect):
        """Add UTC timezone to datetime when retrieving from DB"""
        if value is not None:
            return value.replace(tzinfo=timezone.utc)
        return value
