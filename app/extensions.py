from datetime import datetime, timezone

from flask import jsonify, request
from flask_jwt_extended import JWTManager, get_jwt_identity, verify_jwt_in_request
from flask_jwt_extended.exceptions import JWTExtendedException
from flask_limiter import Limiter
from flask_marshmallow import Marshmallow

ma = Marshmallow()
jwt = JWTManager()


def rate_limit_key():
    try:
        verify_jwt_in_request(optional=True)
        identity = get_jwt_identity()
        if identity is not None:
            return f"user:{identity}"
    except JWTExtendedException:
        pass

    return f"ip:{request.remote_addr or '127.0.0.1'}"


def rate_limit_exceeded(request_limit):
    response = jsonify(
        {
            "error": "rate_limit_exceeded",
            "message": "Rate limit exceeded. Please retry later.",
            "details": {
                "limit": str(request_limit.limit),
                "remaining": request_limit.remaining,
                "reset_at": datetime.fromtimestamp(
                    request_limit.reset_at,
                    tz=timezone.utc,
                ).isoformat(),
                "path": request.path,
            },
        }
    )
    response.status_code = 429
    return response


limiter = Limiter(
    key_func=rate_limit_key,
    headers_enabled=True,
    strategy="moving-window",
    on_breach=rate_limit_exceeded,
)
