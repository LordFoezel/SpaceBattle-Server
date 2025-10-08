from fastapi import Request


def extract_bearer_token(request: Request) -> str | None:
    auth_header = request.headers.get("authorization")
    if not auth_header:
        return None
    s = auth_header.strip()
    if len(s) >= 7 and s[:7].lower() == "bearer ":
        return s[7:].strip()
    return s
