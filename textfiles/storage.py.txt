from datetime import datetime
from fastapi.responses import JSONResponse
from fastapi import status

# Dateioperationen

def now():
    """Gets the current timestamp."""
    return datetime.utcnow().isoformat() + "Z"

def error_notFound(field, value):
    """Returns a customized error message for searches with no result."""
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"error": f"No exercises found for {field}: '{value}'"}
    )
