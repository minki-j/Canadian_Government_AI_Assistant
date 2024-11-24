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
from . import prompts

def find_goal(state: OverallState):
    print("\n>>> NODE: find_goal")

    class FindGoalResponse(BaseModel):
        is_goal_found: bool = Field(description="Whether the goal has been found.")
        goal_id: str = Field(description="The id of the goal. Leave empty if goal is not found.")
        follow_up_message: str = Field(
            description="The follow up message to send to the user. If the goal was not found, ask a question to help the user find the goal. If the goal is found, tell the user what the goal is."
        )

    response = (
        prompts.FIND_GOAL
        | chat_model.with_structured_output(FindGoalResponse)
    ).invoke(
        {
            "messages": state.stringify_messages(),
            "goal_list": "\n\n".join(
                f"{goal.id}: {goal.name}\n{goal.description}"
                for goal in state.goal_list
            ),
        }
    )

    if response.is_goal_found:
        return {
            "goal_id": response.goal_id,
            "messages": [AIMessage(content=response.follow_up_message)],
        }
    else:
        return {
            "goal_id": "",
            "messages": [AIMessage(content=response.follow_up_message)],
        }

g = StateGraph(OverallState, input=InputState, output=OutputState)
g.add_edge(START, n(find_goal))

g.add_node(n(find_goal), find_goal)
g.add_edge(n(find_goal), END)


goal_finder_graph = g.compile()

with open("./agents/graph_diagrams/goal_finder_graph.png", "wb") as f:
    f.write(goal_finder_graph.get_graph(xray=1).draw_mermaid_png())
