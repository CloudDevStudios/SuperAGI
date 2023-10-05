import asyncio
from typing import Any, List

import aiohttp

from superagi.config.config import get_config
from superagi.helper.webpage_extractor import WebpageExtractor


class GoogleSerpApiWrap:
    def __init__(self, api_key, num_results=10, num_pages=1, num_extracts=3):
        self.api_key = api_key
        self.num_results = num_results
        self.num_pages = num_pages
        self.num_extracts = num_extracts
        self.extractor = WebpageExtractor()

    def search_run(self, query):
        results = asyncio.run(self.fetch_serper_results(query=query))
        return self.process_response(results)

    async def fetch_serper_results(self,
                                   query: str, search_type: str = "search"
                                   ) -> dict[str, Any]:
        headers = {
            "X-API-KEY": self.api_key or "",
            "Content-Type": "application/json",
        }
        params = {"q": query,}
        async with aiohttp.ClientSession() as session:
            async with session.post(
                            f"https://google.serper.dev/{search_type}", headers=headers, params=params
                    ) as response:
                response.raise_for_status()
                return await response.json()

    def process_response(self, results) -> str:
        snippets: List[str] = []
        links: List[str] = []

        if results.get("answerBox"):
            answer_values = []
            answer_box = results.get("answerBox", {})
            if answer_box.get("answer"):
                answer_values.append(answer_box.get("answer"))
            elif answer_box.get("snippet"):
                answer_values.append(answer_box.get("snippet").replace("\n", " "))
            elif answer_box.get("snippetHighlighted"):
                answer_values.append(", ".join(answer_box.get("snippetHighlighted")))

            if answer_values:
                snippets.append("\n".join(answer_values))

        if results.get("knowledgeGraph"):
            knowledge_graph = results.get("knowledgeGraph", {})
            title = knowledge_graph.get("title")
            if entity_type := knowledge_graph.get("type"):
                snippets.append(f"{title}: {entity_type}.")
            if description := knowledge_graph.get("description"):
                snippets.append(description)
            snippets.extend(
                f"{title} {attribute}: {value}."
                for attribute, value in knowledge_graph.get(
                    "attributes", {}
                ).items()
            )
        for result in results["organic"][:self.num_results]:
            if "snippet" in result:
                snippets.append(result["snippet"])
            if "link" in result and len(links) < self.num_results:
                links.append(result["link"])
            snippets.extend(
                f"{attribute}: {value}."
                for attribute, value in result.get("attributes", {}).items()
            )
        if not snippets:
            return {"snippets": "No good Google Search Result was found", "links": []}

        return {"links": links, "snippets": snippets}
