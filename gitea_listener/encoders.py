import json
from datetime import datetime
from typing import Any


__all__ = ['DateTimeEncoder']


class DateTimeEncoder(json.JSONEncoder):
    """
    This class allows safe serialization of datetime objects.
    """
    def default(self, o: Any) -> Any:
        if isinstance(o, datetime):
            return o.isoformat()
        return super().default(o)
