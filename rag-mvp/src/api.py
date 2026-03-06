"""AG-005: API 最小闭环——/health、/chat、/handoff。"""

from fastapi import FastAPI, Request
from pydantic import BaseModel

from src.agent.orchestrator import run as orchestrator_run


class ChatRequest(BaseModel):
    """POST /chat 请求体。"""
    question: str


def create_app() -> FastAPI:
    """创建 FastAPI 应用。调用方需设置 app.state.pipeline（RAG 管道）。"""
    app = FastAPI(title="RAG Merchant Agent API")

    @app.get("/health")
    def health():
        return {"status": "ok"}

    @app.post("/chat")
    def chat(request: Request, body: ChatRequest):
        pipeline = getattr(request.app.state, "pipeline", None)
        if pipeline is None:
            return {"answer": "", "sources": [], "risk_flag": False, "handoff": False}
        resp = orchestrator_run(body.question, pipeline)
        return resp.to_dict()

    @app.get("/handoff")
    def handoff():
        return {"handoff": True, "message": "已记录转人工请求，请稍候。"}

    return app


app = create_app()


if __name__ == "__main__":
    """本地启动：自动挂载 RAG pipeline。"""
    from pathlib import Path
    from src.pipeline import RagPipeline
    _app = create_app()
    _app.state.pipeline = RagPipeline(base_dir=Path(__file__).resolve().parent.parent, provider=None)
    import uvicorn
    uvicorn.run(_app, host="0.0.0.0", port=8000)
