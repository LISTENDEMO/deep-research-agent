from dataclasses import asdict
import json
from pathlib import Path

from fastapi import FastAPI
from fastapi import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse, StreamingResponse
from pydantic import BaseModel, Field
from dotenv import load_dotenv

from app.graph.runner import run_research
from app.history_store import get_history_store
from app.llm import LlmSettings
from app.tools.search import TavilySearchTool


PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")
load_dotenv(PROJECT_ROOT / "backend" / ".env")


class ResearchRequest(BaseModel):
    query: str = Field(min_length=2)
    use_mock_search: bool = True


app = FastAPI(title="Deep Research Agent", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/config/status")
def config_status() -> dict[str, bool]:
    return {
        "tavily_configured": TavilySearchTool().is_configured,
        "llm_configured": LlmSettings.from_env().is_configured,
    }


@app.post("/api/research")
def research(request: ResearchRequest) -> dict:
    result = run_research(
        request.query,
        use_mock_search=request.use_mock_search,
    )
    payload = asdict(result)
    payload["report_id"] = get_history_store().save_result(result)
    return payload


@app.post("/api/export/markdown")
def export_markdown(request: ResearchRequest) -> PlainTextResponse:
    result = run_research(
        request.query,
        use_mock_search=request.use_mock_search,
    )
    return PlainTextResponse(result.exports["markdown"], media_type="text/markdown")


@app.post("/api/research/events")
def research_events(request: ResearchRequest) -> StreamingResponse:
    def event_stream():
        planned_steps = [
            ("scope", "Scope Agent 正在生成研究简报"),
            ("plan", "Supervisor 正在拆解研究任务"),
            ("research", "Researcher 正在收集和抽取证据"),
            ("verify", "Verifier 正在构建观点对立矩阵"),
            ("write", "Writer 正在生成最终报告"),
        ]
        for step, message in planned_steps:
            yield json.dumps(
                {"event": "step", "step": step, "message": message},
                ensure_ascii=False,
            ) + "\n"

        try:
            result = run_research(
                request.query,
                use_mock_search=request.use_mock_search,
            )
            report_id = get_history_store().save_result(result)
        except Exception as error:
            yield json.dumps(
                {
                    "event": "error",
                    "message": str(error),
                },
                ensure_ascii=False,
            ) + "\n"
            return

        payload = asdict(result)
        payload["report_id"] = report_id
        yield json.dumps(
            {"event": "final", "payload": payload},
            ensure_ascii=False,
        ) + "\n"

    return StreamingResponse(event_stream(), media_type="application/x-ndjson")


@app.get("/api/reports")
def list_reports() -> dict:
    return {"reports": get_history_store().list_reports()}


@app.get("/api/reports/{report_id}")
def get_report(report_id: str) -> dict:
    report = get_history_store().get_report(report_id)
    if report is None:
        raise HTTPException(status_code=404, detail="Report not found")
    return report


@app.delete("/api/reports/{report_id}")
def delete_report(report_id: str) -> dict[str, bool]:
    deleted = get_history_store().delete_report(report_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Report not found")
    return {"deleted": True}
