"""
RosaBot agent — connects the OpenAI model to the menu tools, with memory.

Built with LangChain's create_agent (current recommended API) plus a LangGraph
checkpointer for conversation memory. Each conversation is identified by a
thread_id; the checkpointer stores and replays that thread's history, so the
bot remembers earlier turns. Memory here is in-memory (InMemorySaver) and
resets when the server restarts — swap for SqliteSaver to persist.
"""

from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver

from app.agent.prompts import ROSABOT_SYSTEM_PROMPT
from app.tools.menu_tools import ALL_TOOLS


def build_agent(model: str = "gpt-4o-mini", temperature: float = 0.2):
    """Create and return the RosaBot agent with conversation memory.

    The checkpointer is what gives the agent memory. To persist across
    restarts instead, replace InMemorySaver() with a SqliteSaver — the rest
    of the code stays identical.
    """
    llm = ChatOpenAI(model=model, temperature=temperature)
    checkpointer = InMemorySaver()
    agent = create_agent(
        model=llm,
        tools=ALL_TOOLS,
        system_prompt=ROSABOT_SYSTEM_PROMPT,
        checkpointer=checkpointer,
    )
    return agent


def ask(agent, question: str, thread_id: str = "default") -> str:
    """Send one question and return RosaBot's answer.

    thread_id ties messages into a single conversation. Reusing the same
    thread_id means the agent remembers earlier turns; a new id starts fresh.
    Only the NEW message is sent — the checkpointer replays the history.
    """
    config = {"configurable": {"thread_id": thread_id}}
    result = agent.invoke(
        {"messages": [{"role": "user", "content": question}]},
        config=config,
    )
    return result["messages"][-1].content


if __name__ == "__main__":
    bot = build_agent()
    # Same thread_id across turns => memory. Watch the follow-up resolve "it".
    tid = "demo-conversation"
    for q in [
        "Does the Pisco Sour have egg?",
        "What about nuts?",
        "And how is it made?",
    ]:
        print(f"\n>>> {q}")
        print(ask(bot, q, thread_id=tid))