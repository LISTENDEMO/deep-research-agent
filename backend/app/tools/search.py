from __future__ import annotations

import os
import re
from dataclasses import dataclass
from urllib.parse import urlparse
from typing import Protocol

import requests

from app.models import SearchResult


BLOCKED_DOMAINS = {
    "facebook.com",
    "www.facebook.com",
}


def clean_search_content(content: str) -> str:
    cleaned = re.sub(r"!\[[^\]]*]\([^)]+\)", " ", content)
    cleaned = re.sub(r"\[([^\]]+)]\([^)]+\)", r"\1", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned.strip()


def is_useful_result(title: str, url: str, content: str) -> bool:
    parsed = urlparse(url)
    if parsed.netloc.lower() in BLOCKED_DOMAINS:
        return False
    text = clean_search_content(content)
    noisy_fragments = [
        "Skip to content",
        "Navigation Menu",
        "Search code, repositories",
        "起点课堂会员权益",
        "职业体系课特权",
        "线下行业大会特权",
        "{{ use",
    ]
    if any(fragment.lower() in text.lower() for fragment in noisy_fragments):
        return False
    return len(text) >= 60 and bool(title.strip()) and bool(url.strip())


class SearchTool(Protocol):
    def search(self, query: str, max_results: int = 3) -> list[SearchResult]:
        ...


@dataclass(slots=True)
class TavilySearchTool:
    api_key: str | None = None

    def __post_init__(self) -> None:
        if self.api_key is None:
            self.api_key = os.getenv("TAVILY_API_KEY")

    @property
    def is_configured(self) -> bool:
        return bool(self.api_key)

    def search(self, query: str, max_results: int = 3) -> list[SearchResult]:
        if not self.api_key:
            raise RuntimeError("TAVILY_API_KEY is required for live Tavily search.")
        response = requests.post(
            "https://api.tavily.com/search",
            json={
                "api_key": self.api_key,
                "query": query,
                "max_results": max(max_results * 2, 5),
                "include_answer": True,
                "search_depth": "advanced",
                "include_raw_content": False,
            },
            timeout=30,
        )
        response.raise_for_status()
        payload = response.json()
        results: list[SearchResult] = []
        for item in payload.get("results", []):
            title = item.get("title", "Untitled source")
            url = item.get("url", "")
            content = clean_search_content(item.get("content", ""))
            if not is_useful_result(title, url, content):
                continue
            results.append(
                SearchResult(
                title=item.get("title", "Untitled source"),
                url=item.get("url", ""),
                    content=content,
                )
            )
            if len(results) >= max_results:
                break
        return results


class MockSearchTool:
    def search(self, query: str, max_results: int = 3) -> list[SearchResult]:
        lowered = query.lower()
        if "rag" in lowered and any(word in lowered for word in ["幻觉", "可追溯", "追溯", "溯源", "引用", "可信", "trace", "ground", "faithfulness"]):
            governance_result = SearchResult(
                title="Enterprise RAG governance checklist",
                url="https://example.com/rag-governance",
                content=(
                    "企业知识库 RAG 需要为文档和 chunk 保留 doc_id、version、owner、updated_at、ACL 和 source_url，"
                    "否则答案无法追溯到具体来源和权限边界。"
                ),
            )
            retrieval_result = SearchResult(
                title="Grounded retrieval for enterprise RAG",
                url="https://example.com/grounded-retrieval",
                content=(
                    "通过 metadata filter、hybrid retrieval 和 rerank 控制进入上下文的证据，"
                    "可以减少无关或无权限内容诱导模型产生幻觉。"
                ),
            )
            citation_result = SearchResult(
                title="Citation mapping and faithfulness checks",
                url="https://example.com/rag-citation-map",
                content=(
                    "答案中的关键 claim 应绑定 citation map 和 chunk_id，并在生成后做 faithfulness 或 groundedness 校验，"
                    "未被证据支持的 claim 应拒答或降级。"
                ),
            )
            audit_result = SearchResult(
                title="RAG audit logging",
                url="https://example.com/rag-audit",
                content=(
                    "保存 query、retrieved_chunk_ids、scores、prompt、answer 和 citation_map，"
                    "能支持企业审计、问题复现和回归测试。"
                ),
            )
            if any(word in lowered for word in ["metadata", "acl", "权限", "治理", "version"]):
                samples = [governance_result, retrieval_result, audit_result]
            elif any(word in lowered for word in ["citation", "faithfulness", "grounded", "引用", "校验"]):
                samples = [citation_result, audit_result, retrieval_result]
            elif any(word in lowered for word in ["audit", "coverage", "评估", "日志", "回放"]):
                samples = [audit_result, citation_result, governance_result]
            else:
                samples = [governance_result, retrieval_result, citation_result]
            return samples[:max_results]

        if "rag" in lowered and any(word in lowered for word in ["召回", "recall", "检索"]):
            eval_result = SearchResult(
                title="RAG recall optimization guide",
                url="https://example.com/rag-recall-guide",
                content=(
                    "应优先建立 Recall@k 评估集，用固定问题和相关文档衡量召回是否真正提升，"
                    "否则无法判断 query rewrite、top_k 或 rerank 调参是否有效。"
                ),
            )
            hybrid_result = SearchResult(
                title="Hybrid retrieval and reranking notes",
                url="https://example.com/hybrid-retrieval",
                content=(
                    "可以通过 BM25 与向量检索混合召回扩大候选覆盖面，再用 reranker 控制噪声，"
                    "适合语义召回和关键词召回都重要的企业知识库。"
                ),
            )
            chunk_result = SearchResult(
                title="Chunking and metadata for RAG",
                url="https://example.com/rag-chunking",
                content=(
                    "提高召回的基础是知识覆盖、合理分块和 metadata 过滤；分块割裂上下文或元数据错误会导致相关文档漏召回。"
                ),
            )
            rewrite_result = SearchResult(
                title="Query rewrite and HyDE for RAG",
                url="https://example.com/rag-query-rewrite",
                content=(
                    "Query rewrite、multi-query 和 HyDE 能把用户问题改写成多种检索表达，"
                    "降低用户表述和知识库文档表述不一致导致的漏召回。"
                ),
            )
            risk_result = SearchResult(
                title="Recall tradeoff memo",
                url="https://example.com/rag-recall-tradeoff",
                content="扩大 top_k 和多路召回会提高候选覆盖，但也会带来噪声、延迟和 rerank 成本，需要用阈值和重排控制。",
            )
            if any(word in lowered for word in ["rewrite", "multi", "hyde", "改写"]):
                samples = [rewrite_result, eval_result, risk_result]
            elif any(word in lowered for word in ["chunk", "index", "metadata", "分块", "索引"]):
                samples = [chunk_result, hybrid_result, risk_result]
            elif any(word in lowered for word in ["hybrid", "rerank", "candidate", "混合", "重排"]):
                samples = [hybrid_result, risk_result, eval_result]
            elif any(word in lowered for word in ["evaluation", "recall@k", "ndcg", "评估", "指标"]):
                samples = [eval_result, risk_result, hybrid_result]
            else:
                samples = [eval_result, chunk_result, hybrid_result]
            return samples[:max_results]

        samples = [
            SearchResult(
                title="Research method note",
                url="https://example.com/research-method",
                content=f"{query} 需要先明确评价指标和适用场景，再比较不同方案的收益、成本和副作用。",
            ),
            SearchResult(
                title="Implementation risk memo",
                url="https://example.com/implementation-risk",
                content=f"{query} 的风险包括数据质量不足、评估口径不清、上线成本和长期维护复杂度。",
            ),
            SearchResult(
                title="Production rollout brief",
                url="https://example.com/production-rollout",
                content=f"{query} 落地时需要小规模试点、记录指标变化，并保留人工复核和回滚机制。",
            ),
        ]
        return samples[:max_results]
