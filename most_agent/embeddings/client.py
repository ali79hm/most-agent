
from math import isfinite

import httpx

from most_agent.config import Settings, get_settings


EMBEDDING_DIMENSIONS = 768


class EmbeddingClient:
    """Client for generating embeddings through TEI."""

    def __init__(self, settings: Settings | None = None):
        self.settings = settings or get_settings()

        self.http = httpx.AsyncClient(
            timeout=self.settings.http_timeout_seconds,
        )

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.aclose()

    async def aclose(self) -> None:
        await self.http.aclose()

    async def embed_document(self, text: str) -> list[float]:
        """Generate an embedding for one document."""
        vectors = await self._embed_many(
            [text],
            prompt_name="document",
        )
        return vectors[0]

    async def embed_documents(
        self,
        texts: list[str],
    ) -> list[list[float]]:
        """Generate embeddings for multiple documents in batches."""
        return await self._embed_many(
            texts,
            prompt_name="document",
        )

    async def embed_query(self, text: str) -> list[float]:
        """Generate an embedding for one search query."""
        vectors = await self._embed_many(
            [text],
            prompt_name="query",
        )
        return vectors[0]

    async def _embed_many(
        self,
        texts: list[str],
        prompt_name: str,
    ) -> list[list[float]]:
        """Send documents to TEI in batches."""

        if not texts:
            return []

        if any(not isinstance(text, str) or not text.strip() for text in texts):
            raise ValueError("Embedding inputs cannot be empty")

        results = []
        batch_size = self.settings.embedding_batch_size

        for start in range(0, len(texts), batch_size):
            batch = texts[start:start + batch_size]

            response = await self.http.post(
                str(self.settings.tei_embed_url),
                json={
                    "inputs": batch,
                    "prompt_name": prompt_name,
                    "normalize": True,
                    "truncate": False,
                },
            )

            response.raise_for_status()

            try:
                data = response.json()
            except ValueError as exc:
                raise RuntimeError(
                    "TEI returned invalid JSON"
                ) from exc

            vectors = self._validate_response(
                data,
                expected_count=len(batch),
            )

            results.extend(vectors)

        return results

    @staticmethod
    def _validate_response(
        data,
        expected_count: int,
    ) -> list[list[float]]:
        """Validate the number and dimensions of returned vectors."""

        if not isinstance(data, list) or len(data) != expected_count:
            raise ValueError(
                f"Expected {expected_count} embeddings, "
                f"received {len(data) if isinstance(data, list) else 'invalid response'}"
            )

        results = []

        for index, vector in enumerate(data):
            if not isinstance(vector, list):
                raise ValueError(
                    f"Embedding {index} is not a valid vector"
                )

            if len(vector) != EMBEDDING_DIMENSIONS:
                raise ValueError(
                    f"Embedding {index}: expected "
                    f"{EMBEDDING_DIMENSIONS} dimensions, "
                    f"received {len(vector)}"
                )

            if any(
                isinstance(value, bool)
                or not isinstance(value, (int, float))
                for value in vector
            ):
                raise ValueError(
                    f"Embedding {index} contains non-numeric values"
                )

            vector = [float(value) for value in vector]

            if not all(isfinite(value) for value in vector):
                raise ValueError(
                    f"Embedding {index} contains non-finite values"
                )

            results.append(vector)

        return results
