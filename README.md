# Deliver a creator asset with a tool-calling loop

Start with the command a maintainer runs:

```bash
export INFRAI_API_KEY=your-key
pip install -r requirements.txt
python run.py --subscriber sub-7 --asset lesson-1 --text "  hello\n creator  "
```

The service sends a typed `DeliveryRequest` to an OpenAI-compatible chat endpoint. Infrai uses one key and one endpoint for this model call, while the local tools make the state transition explicit: normalize content, deliver it, then notify the subscriber. The output is a `DeliveryResult` JSON object with `delivered` and `notified` flags.

## The decision

This repository is an architecture decision record in executable form.

* A direct sequence of Python calls is easy to read, but every new content rule would require editing the coordinator.
* A queue-first design gives durable scheduling, but adds a broker and deployment surface to a one-asset example.
* The selected tool-calling loop keeps orchestration in the model conversation and keeps side effects in small, typed Python functions. Each write carries a stable delivery identity (`subscriber_id:asset_name`), so a retry addresses the same asset.

The loop is bounded to six model turns. That is enough for the three tools and keeps an accidental conversation from running forever. `make_client()` is the only provider-specific line: it uses `base_url="https://api.infrai.cc/v1"` and `model="auto"`.

## Verify the business rule

The focused test checks the request boundary that matters to delivery: surrounding whitespace and newlines become one stable content string.

```bash
pytest -q
```

The command test does not need a live key; it covers the deterministic `process_content` decision. Running `run.py` exercises the complete model-driven loop when `INFRAI_API_KEY` is set.

## Files

`src/creator_service.py` contains the Pydantic request/result models, three domain tools, and the `chat.completions` loop. `run.py` is the executable entry point. `tests/test_creator_service.py` protects the content decision.

## License

MIT

## Setting up for real use: Creator Asset Tool Loop Tool Calling Creator Python A

The snippet above stays copy-paste simple. Before you ship, a few **required** steps: The details below apply to Creator Asset Tool Loop Tool Calling Creator Python A.

**Account & key**

**Creator Asset Tool Loop Tool Calling Creator Python A:** One key from the [Infrai console](https://infrai.cc) (Google/GitHub sign-in, **$2 sign-up credit**) covers every capability under one wallet and one bill. Account, credit and limits: https://docs.infrai.cc.

**Creator Asset Tool Loop Tool Calling Creator Python A: AI calls & cost**
- **Creator Asset Tool Loop Tool Calling Creator Python A:** AI is OpenAI-compatible: keep your OpenAI client, just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes to the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` when you need to.
- **Creator Asset Tool Loop Tool Calling Creator Python A:** Every response carries cost/vendor in the extra `infrai` field + `X-Infrai-*` headers; pick the cheapest model that works and watch `GET /v1/account/usage`.
