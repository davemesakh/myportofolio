import re
from urllib.parse import urlencode, urlsplit

from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.templatetags.static import static


DRIVE_FILE_PATH = re.compile(r"/file/d/([A-Za-z0-9_-]+)/view/?\Z")
HTTPS_VALIDATOR = URLValidator(schemes=["https"])
INVALID_LOGO_SOURCE = "Enter a local static path, an HTTPS image URL, or a public Google Drive share link."


def validate_experience_logo_source(value):
    """Validate a stored local static path or external HTTPS logo source."""
    if not value:
        return
    if not isinstance(value, str) or any(character.isspace() for character in value):
        raise ValidationError(INVALID_LOGO_SOURCE)

    try:
        parsed = urlsplit(value)
    except ValueError as error:
        raise ValidationError(INVALID_LOGO_SOURCE) from error

    if parsed.scheme or parsed.netloc:
        if parsed.scheme != "https" or not parsed.netloc or parsed.username or parsed.password:
            raise ValidationError(INVALID_LOGO_SOURCE)
        try:
            HTTPS_VALIDATOR(value)
        except ValidationError as error:
            raise ValidationError(INVALID_LOGO_SOURCE) from error
        if parsed.hostname == "drive.google.com":
            if parsed.netloc != "drive.google.com" or not DRIVE_FILE_PATH.fullmatch(parsed.path):
                raise ValidationError(INVALID_LOGO_SOURCE)
        return

    # Local values must remain relative static paths, without URL syntax or traversal.
    if (value.startswith(("/", "\\")) or "\\" in value or ":" in value
            or "?" in value or "#" in value or "%" in value
            or any(part in ("", ".", "..") for part in value.split("/"))):
        raise ValidationError(INVALID_LOGO_SOURCE)


def resolve_experience_logo_url(value):
    """Resolve a logo for display without changing its stored source."""
    if not value:
        return ""
    try:
        validate_experience_logo_source(value)
    except ValidationError:
        return ""

    parsed = urlsplit(value)
    if parsed.scheme == "https":
        if parsed.hostname == "drive.google.com":
            file_id = DRIVE_FILE_PATH.fullmatch(parsed.path).group(1)
            # Public/shareable Drive images can still fail due to permissions or
            # hotlink restrictions; Drive is not guaranteed to act as an image CDN.
            return "https://drive.google.com/thumbnail?" + urlencode({"id": file_id, "sz": "w512"})
        return value
    return static(value)
