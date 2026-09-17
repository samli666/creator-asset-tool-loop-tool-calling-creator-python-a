from src.creator_service import DeliveryRequest, process_content


def test_content_processing_keeps_delivery_text_deterministic() -> None:
    request = DeliveryRequest(subscriber_id="sub-7", asset_name="lesson-1", asset_text="  hello\n creator  ")
    assert process_content(request.asset_text) == "hello creator"
