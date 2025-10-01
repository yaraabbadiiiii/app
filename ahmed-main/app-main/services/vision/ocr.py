from typing import List, Dict, Any


def run_ocr_placeholder(image_rgb: Any) -> List[Dict[str, Any]]:
    """
    Placeholder OCR that returns a fixed set of lines.
    Replace with real OCR implementation.
    """
    return [
        {"id": "l_001", "text": "مرحبا بك في الجهاز", "lang": "ar", "tokens": []},
        {"id": "l_002", "text": "This is a test", "lang": "en", "tokens": []},
    ]


