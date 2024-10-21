TAG_METADATA = [
    {
        "name": "users",
        "description": "User authorization and registration , and working with user data",
    },
    {
        "name": "referal_codes",
        "description": "Working with referral codes",
    },
    {
        "name": "healthz",
        "description": "Standard service health check",
    },
]

TITLE = "FastAPI referal system app"

DESCRIPTION = (
    "An application with the following functionality:"
    "• User authorization and registration , and working with user data"
    "• Working with referral codes"
)


VERSION = "0.0.1"

ERROR_MAPS = {
    "postgres": "PostgreSQL connection failed",
    "redis": "Redis connection failed",
}
