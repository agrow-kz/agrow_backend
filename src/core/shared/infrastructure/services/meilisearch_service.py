from meilisearch_python_sdk import AsyncClient
from meilisearch_python_sdk.models.settings import MeilisearchSettings

from src.core.shared.presentation.dto import SearchIndexConfig, SearchResult


class MeilisearchService:
    def __init__(self, client: AsyncClient):
        self.client = client

    async def index_documents(self, index_name: str, documents: list[dict]) -> None:
        index = self.client.index(index_name)
        await index.add_documents(documents, primary_key="id")

    async def delete_documents(self, index_name: str, document_ids: list[str]) -> None:
        index = self.client.index(index_name)
        string_ids = [str(doc_id) for doc_id in document_ids]
        await index.delete_documents(string_ids)

    async def configure_index(
        self,
        index_name: str,
        index_config: SearchIndexConfig,
    ):
        index = self.client.index(index_name)
        await index.update_settings(
            MeilisearchSettings(
                filterable_attributes=index_config.filterable,
                sortable_attributes=index_config.sortable,
                searchable_attributes=index_config.searchable,
            )
        )

    async def search(
        self,
        index_name: str,
        query: str | None = None,
        filter_expression: str | list[str] | None = None,
        page: int = 1,
        limit: int = 20,
    ):
        index = self.client.index(index_name)

        response = await index.search(
            query=query,
            filter=filter_expression,
            page=page,
            hits_per_page=limit,
        )

        return SearchResult(
            hits=response.hits,
            total=response.total_hits,
            page=response.page,
            pages=response.total_pages,
        )
