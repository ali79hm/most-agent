
import asyncio

from most_agent.embeddings.service import generate_media_embeddings


async def main() -> None:
    report = await generate_media_embeddings()

    print("\n========== EMBEDDING REPORT ==========\n")
    print(f"Total media: {report.total_media}")
    print(f"Inserted:    {report.inserted}")
    print(f"Updated:     {report.updated}")
    print(f"Skipped:     {report.skipped}")
    print("\nEmbedding process completed!")
    print("======================================")


if __name__ == "__main__":
    asyncio.run(main())
