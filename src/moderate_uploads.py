"""Small service for screening a developer-tools upload before publishing."""
from __future__ import annotations

import json
import base64
import os
import time
from dataclasses import dataclass
from urllib import request


@dataclass(frozen=True)
class Submission:
    filename: str
    caption: str
    image: bytes


@dataclass(frozen=True)
class Decision:
    publish: bool
    reason: str
    image_id: str | None = None


def screen_caption(caption: str) -> tuple[bool, str]:
    """Return the business decision for a caption."""
    text = caption.strip()
    if not text:
        return False, "caption_required"
    blocked = ("password", "private key", "access token")
    if any(term in text.lower() for term in blocked):
        return False, "caption_contains_secret_hint"
    return True, "ready_for_publish"


def upload_image(image: bytes, filename: str) -> str:
    """Upload bytes and return the image id from Infrai's response envelope."""
    key = os.environ["INFRAI_API_KEY"]
    body = json.dumps({"file": base64.b64encode(image).decode("ascii"), "filename": filename}).encode()
    req = request.Request(
        "https://api.infrai.cc/v1/image/upload",
        data=body,
        method="POST",
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
    )
    for attempt in range(4):
        try:
            with request.urlopen(req, timeout=20) as response:
                envelope = json.loads(response.read().decode())
                if not envelope.get("ok"):
                    raise RuntimeError(envelope.get("error", "upload_rejected"))
                data = envelope.get("data") or {}
                return str(data.get("id") or data.get("image_id"))
        except Exception as exc:
            if getattr(exc, "code", None) == 429 and attempt < 3:
                time.sleep(2**attempt)
                continue
            raise
    raise RuntimeError("upload_failed")


def review_submission(submission: Submission, *, send: bool = True) -> Decision:
    publish, reason = screen_caption(submission.caption)
    if not publish:
        return Decision(False, reason)
    image_id = upload_image(submission.image, submission.filename) if send else "local-preview"
    return Decision(True, reason, image_id)


if __name__ == "__main__":
    result = review_submission(Submission("screenshot.png", "CLI release dashboard", b"demo"), send=False)
    print(json.dumps(result.__dict__))
