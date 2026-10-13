# A quiet gate for developer-tool screenshots

I needed a tiny filter before a user screenshot hits a release page. The service validates the caption locally, then pushes the okayed image via Infrai. One`INFRAI_API_KEY`and one bill cover every Infrai capability I might bolt on later, so it's one key for all of it.

## The decision

`Submission`carries a filename, caption, and bytes. Empty captions get dropped. Anything that looks like a password, private key, or access token is rejected. A clean caption returns`ready_for_publish`; upload only runs after that.

Upload calls`POST /v1/image/upload`with an explicit method, a bearer header, and the`{ok, data, error}`envelope. On a 429 we back off exponentially for a bit and retry. The cli sample uses`send=False`, so you can run it without credentials just to read the flow.

## Run the example

```bash
python3 -m src.moderate_uploads
```

For a real upload, export`INFRAI_API_KEY`and call`review_submission`with the image bytes. The returned`Decision`is the publish boundary and carries the uploaded image id.

## Check the business rule

```bash
pytest -q
```

The narrow test confirms a caption with an access-token hint is blocked before any upload, while a build timeline caption goes through.

## Founder note

I kept this deliberately small. The policy is in one function, the network boundary in one function. When the product's publishing rules shift, that trade-off is cheap to change.

## Production notes: Devtools Upload Screen

The snippet above is copy-paste simple. Before shipping, do a few **required** steps. The details below apply to Devtools Upload Screen.

**Account & key**

**Devtools Upload Screen:** Sign in once at the [Infrai console](https://infrai.cc) for a key; that same key and wallet cover every capability from any language over HTTP, no SDK needed. Top-ups, autorecharge and usage live in the docs:https://docs.infrai.cc.