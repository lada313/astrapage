import re

def norm_email(x: str | None) -> str | None:
    if not x: return None
    s = x.strip().lower().replace(" ", "")
    return s if ("@" in s and "." in s) else None

def norm_phone(x: str | None) -> str | None:
    if not x: return None
    digits = re.sub(r"\D+", "", x)
    if len(digits) >= 11 and (digits.startswith("7") or digits.startswith("8")):
        digits = "7" + digits[-10:]
    elif len(digits) >= 10 and len(digits) != 11:
        digits = digits[-10:]
    return digits if len(digits) >= 10 else None

def pick_identity(phone: str | None, client_id: str | None, email: str | None):
    # Priority: phone > client_id > email
    if phone: return ("phone", phone)
    if client_id: return ("client_external_id", client_id)
    if email: return ("email", email)
    return (None, None)
