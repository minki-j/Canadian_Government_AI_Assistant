import os
import sqlite3
from varname import nameof as n
from pydantic import BaseModel, Field
import asyncio

from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import START, END, StateGraph
from langchain_core.runnables import (
    RunnablePassthrough,
    RunnableParallel,
    RunnableLambda,
)
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage


from agents.state_schema import OverallState, InputState, OutputState

from agents.llm_models import chat_model

from agents.subgraphs.goal_finder.graph import goal_finder_graph
from agents.subgraphs.tour_guide.graph import tour_guide_graph

from agents import prompts


def stage_router(state: OverallState) -> bool:
    print("\n>>> CONDITIONAL EDGE: stage_router")

    if state.stage == "tour_guide":
        return n(tour_guide_graph)
    elif state.stage == "goal_finder":
        return n(goal_finder_graph)


g = StateGraph(OverallState, input=InputState, output=OutputState)
g.add_edge(START, n(stage_router))

g.add_node(n(stage_router), RunnablePassthrough())
g.add_conditional_edges(
    n(stage_router),
    stage_router,
    [
        n(goal_finder_graph),
        n(tour_guide_graph),
    ],
)

g.add_node(n(goal_finder_graph), goal_finder_graph)
g.add_edge(n(goal_finder_graph), "end_of_loop")

g.add_node(n(tour_guide_graph), tour_guide_graph)
g.add_edge(n(tour_guide_graph), "end_of_loop")

g.add_node("end_of_loop", RunnablePassthrough())
g.add_edge("end_of_loop", n(stage_router))

os.makedirs("./data/graph_checkpoints", exist_ok=True)
db_path = os.path.join(".", "data", "graph_checkpoints", "checkpoints.sqlite")
conn = sqlite3.connect(db_path, check_same_thread=False)
memory = SqliteSaver(conn)

main_graph = g.compile(checkpointer=memory, interrupt_before=["end_of_loop"])

with open("./agents/graph_diagrams/main_graph.png", "wb") as f:
    f.write(main_graph.get_graph(xray=1).draw_mermaid_png())
