import base64
import io
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1]))

from src.moderate_uploads import Submission, review_submission, screen_caption, upload_image


def test_secret_hint_is_rejected_before_upload():
    allowed, reason = screen_caption("Paste your access token here")
    assert allowed is False
    assert reason == "caption_contains_secret_hint"
    assert review_submission(Submission("shot.png", "Paste your access token here", b"x"), send=False).publish is False


def test_normal_devtools_caption_is_publishable():
    decision = review_submission(Submission("shot.png", "Build event timeline", b"x"), send=False)
    assert decision.publish is True
    assert decision.reason == "ready_for_publish"


def test_upload_sends_json_image(monkeypatch):
    monkeypatch.setenv("INFRAI_API_KEY", "test-key")

    def fake_urlopen(req, timeout):
        assert req.get_header("Content-type") == "application/json"
        assert json.loads(req.data) == {
            "file": base64.b64encode(b"\x00\xff").decode("ascii"),
            "filename": "shot.png",
        }
        return io.BytesIO(b'{"ok":true,"data":{"id":"image-1"}}')

    monkeypatch.setattr("src.moderate_uploads.request.urlopen", fake_urlopen)
    assert upload_image(b"\x00\xff", "shot.png") == "image-1"
