
import hashlib
import json


def build_content_hash(
    text: str,
    *,
    model_name: str,
    prompt_name: str = "document",
    normalize: bool = True,
    truncate: bool = False,
    dimensions: int = 768,
) -> str:
    """
    Generate a SHA-256 fingerprint for an embedding input
    and its generation configuration.
    """

    if not text.strip():
        raise ValueError("Cannot hash empty embedding text")

    payload = {
        "version": 1,
        "text": text,
        "model_name": model_name,
        "prompt_name": prompt_name,
        "normalize": normalize,
        "truncate": truncate,
        "dimensions": dimensions,
    }

    canonical_text = json.dumps(
        payload,
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":"),
    )

    return hashlib.sha256(
        canonical_text.encode("utf-8")
    ).hexdigest()
