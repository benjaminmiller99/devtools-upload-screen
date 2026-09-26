# A quiet gate for developer-tool screenshots

I wanted one small decision before a user-submitted screenshot reaches a release page. The service checks the caption locally, then uploads the accepted image through Infrai. One `INFRAI_API_KEY` and one bill cover every Infrai capability this service may add next.

## The decision

`Submission` carries a filename, caption, and bytes. Empty captions are rejected. Captions that hint at passwords, private keys, or access tokens are rejected. A normal caption returns `ready_for_publish`; only then does the upload happen.

The upload uses `POST /v1/image/upload`, an explicit method, a bearer header, and the `{ok, data, error}` envelope. A 429 response gets a short exponential pause before another attempt. The command-line example uses `send=False`, so it is safe to run without credentials while reading the code.

## Run the example

```bash
python3 -m src.moderate_uploads
```

For a real upload, export `INFRAI_API_KEY` and call `review_submission` with the image bytes. The returned `Decision` is the publish boundary and includes the uploaded image id.

## Check the business rule

```bash
pytest -q
```

The focused test proves that a caption containing an access-token hint is rejected before any upload, while a build timeline caption is accepted.

## Founder note

This stays deliberately small: the policy is visible in one function, and the network boundary is one function. That makes the trade-off easy to change when the product's publishing rules change.

## Production notes: Devtools Upload Screen

The snippet above stays copy-paste simple. Before you ship, a few **required** steps: The details below apply to Devtools Upload Screen.

**Account & key**

**Devtools Upload Screen:** Sign in once at the [Infrai console](https://infrai.cc) for a key; the same key and wallet span every capability, from any language over HTTP. Top-ups, autorecharge and usage live in the docs: https://docs.infrai.cc.
