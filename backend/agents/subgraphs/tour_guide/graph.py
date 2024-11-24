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


g = StateGraph(OverallState, input=InputState, output=OutputState)
g.add_edge(START, "start_node")

g.add_node("start_node", RunnablePassthrough())
g.add_edge("start_node", END)


tour_guide_graph = g.compile()

with open("./agents/graph_diagrams/tour_guide_graph.png", "wb") as f:
    f.write(tour_guide_graph.get_graph(xray=1).draw_mermaid_png())
