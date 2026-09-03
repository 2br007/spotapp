from fastapi import HTTPException, Request
from starlette.responses import JSONResponse


async def http_exception_handler(request: Request, exception: HTTPException):
    return JSONResponse(
        status_code=exception.status_code,
        content={
            "message": exception.detail if isinstance(exception.detail, str)
            else "Request failed",
            "code": exception.status_code,
        },
    )
