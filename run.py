import argparse
import json

from src.creator_service import DeliveryRequest, make_client, run_tool_loop


def main() -> None:
    parser = argparse.ArgumentParser(description="Deliver one creator asset.")
    parser.add_argument("--subscriber", required=True)
    parser.add_argument("--asset", required=True)
    parser.add_argument("--text", required=True)
    args = parser.parse_args()
    result = run_tool_loop(DeliveryRequest(subscriber_id=args.subscriber, asset_name=args.asset, asset_text=args.text), make_client())
    print(json.dumps(result.model_dump(), indent=2))


if __name__ == "__main__":
    main()
