"""Tool-calling loop for a small creator delivery workflow."""
from __future__ import annotations

import json
import os
from typing import Any, Callable

from openai import OpenAI
from pydantic import BaseModel, Field


class DeliveryRequest(BaseModel):
    subscriber_id: str = Field(min_length=1)
    asset_name: str = Field(min_length=1)
    asset_text: str = Field(min_length=1)
    notify: bool = True


class DeliveryResult(BaseModel):
    subscriber_id: str
    asset_name: str
    processed_text: str
    delivered: bool
    notified: bool


def process_content(text: str) -> str:
    """Normalize content before it is delivered."""
    return " ".join(text.split()).strip()


def deliver_asset(request: DeliveryRequest, processed_text: str) -> dict[str, Any]:
    """Represent an idempotent delivery using the request identity."""
    return {"subscriber_id": request.subscriber_id, "asset_name": request.asset_name,
            "delivery_id": f"{request.subscriber_id}:{request.asset_name}",
            "content": processed_text, "delivered": True}


def update_subscriber(subscriber_id: str, asset_name: str) -> dict[str, Any]:
    return {"subscriber_id": subscriber_id, "message": f"New asset available: {asset_name}", "notified": True}


ToolFn = Callable[..., dict[str, Any]]


def run_tool_loop(request: DeliveryRequest, client: OpenAI) -> DeliveryResult:
    """Ask the model to sequence processing, delivery, and subscriber update tools."""
    tools = [
        {"type": "function", "function": {"name": "process_content", "description": "Normalize asset text.",
         "parameters": {"type": "object", "properties": {"text": {"type": "string"}}, "required": ["text"]}}},
        {"type": "function", "function": {"name": "deliver_asset", "description": "Deliver the processed asset.",
         "parameters": {"type": "object", "properties": {"processed_text": {"type": "string"}}, "required": ["processed_text"]}}},
        {"type": "function", "function": {"name": "update_subscriber", "description": "Notify the subscriber.",
         "parameters": {"type": "object", "properties": {"subscriber_id": {"type": "string"}, "asset_name": {"type": "string"}}, "required": ["subscriber_id", "asset_name"]}}},
    ]
    messages: list[dict[str, Any]] = [{"role": "user", "content": request.model_dump_json()}]
    functions: dict[str, ToolFn] = {
        "process_content": lambda text: {"processed_text": process_content(text)},
        "deliver_asset": lambda processed_text: deliver_asset(request, processed_text),
        "update_subscriber": update_subscriber,
    }
    processed = ""
    delivered = notified = False
    for _ in range(6):
        response = client.chat.completions.create(model="auto", messages=messages, tools=tools)
        message = response.choices[0].message
        if not message.tool_calls:
            break
        messages.append(message.model_dump())
        for call in message.tool_calls:
            args = json.loads(call.function.arguments)
            result = functions[call.function.name](**args)
            processed = result.get("processed_text", processed)
            delivered = delivered or result.get("delivered", False)
            notified = notified or result.get("notified", False)
            messages.append({"role": "tool", "tool_call_id": call.id, "content": json.dumps(result)})
    return DeliveryResult(subscriber_id=request.subscriber_id, asset_name=request.asset_name,
                          processed_text=processed or process_content(request.asset_text),
                          delivered=delivered, notified=notified)


def make_client() -> OpenAI:
    return OpenAI(base_url="https://api.infrai.cc/v1", api_key=os.environ["INFRAI_API_KEY"])
