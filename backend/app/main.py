import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app import config
from app.agent.rosabot_agent import build_agent, ask
from app.models.chat import ChatRequest, ChatResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("rosabot")

_state: dict = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    config.assert_configured()
    logger.info("Building RosaBot agent (model=%s)...", config.MODEL_NAME)
    _state["agent"] = build_agent(
        model=config.MODEL_NAME, temperature=config.TEMPERATURE
    )
    logger.info("RosaBot agent ready.")
    yield
    _state.clear()


app = FastAPI(
    title="RosaBot API",
    description="Staff assistant for India Rosa — menu, allergens, cocktails.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.ALLOWED_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict:
    return {
        "status": "ok" if _state.get("agent") else "starting",
        "model": config.MODEL_NAME,
    }


@app.post("/chat")
def chat(request: ChatRequest) -> ChatResponse:
    agent = _state.get("agent")
    if agent is None:
        # Server is still starting up or failed to build the agent.
        raise HTTPException(
            status_code=503,
            detail="RosaBot is still starting up. Try again in a moment.",
        )

    try:
        reply = ask(agent, request.message, thread_id=request.conversation_id)
    except Exception as exc:  # noqa: BLE001 — we want a clean message for any failure
        # Log the real error server-side for debugging, but never leak internals
        # (API keys, stack traces) to the client.
        logger.exception("Error while answering: %s", exc)
        raise HTTPException(
            status_code=502,
            detail=(
                "RosaBot couldn't generate an answer right now. This is usually "
                "a temporary issue with the language model. Please try again."
            ),
        )

    if not reply or not reply.strip():
        return ChatResponse(
            reply="I'm not sure how to answer that — could you rephrase?"
        )

    return ChatResponse(reply=reply)