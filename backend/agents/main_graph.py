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
from agents.global_nodes.nodes import check_if_solution_is_leaked


from agents import prompts


def stage_router(state: OverallState) -> bool:
    print("\n>>> NODE: stage_router")

    # if state.stage == "greeting":
    #     return n(greeting_stage_graph)

    # if state.stage == "thought_process":
    #     class ClassifierResponse(BaseModel):
    #         rationale: str = Field(description="The rationale for the decision.")
    #         should_end_thought_process: bool = Field(
    #             description="Return True if the candidate has finished thinking about the problem or wants to move on to the actual interview stage, otherwise return False."
    #         )

    #     chain = ChatPromptTemplate.from_template(
    #         prompts.IS_THOUGHT_PROCESS_DONE
    #     ) | chat_model.with_structured_output(ClassifierResponse)

    #     stringified_messages = "\n\n".join(
    #         [
    #             f">>{message.type.upper()}: {message.content}"
    #             for message in state.messages[1:]
    #         ]
    #     )

    #     if chain.invoke({"messages": stringified_messages}).should_end_thought_process:
    #         return n(initiate_main_stage)
    #     else:
    #         return n(thought_process_stage_graph)

    # if state.stage == "main":
    #     return n(main_stage_graph)

    # if state.stage == "assessment":
    #     return n(final_assessment_stage_graph)
    




g = StateGraph(OverallState, input=InputState, output=OutputState)
g.add_edge(START, n(stage_router))

g.add_node(n(stage_router), RunnablePassthrough())
g.add_conditional_edges(
    n(stage_router),
    stage_router,
    [
        n(main_stage_graph),
        n(greeting_stage_graph),
        n(thought_process_stage_graph),
        n(final_assessment_stage_graph),
        n(initiate_main_stage),
    ],
)

g.add_node(n(greeting_stage_graph), greeting_stage_graph)
g.add_edge(n(greeting_stage_graph), "end_of_loop")

g.add_node(n(thought_process_stage_graph), thought_process_stage_graph)
g.add_edge(n(thought_process_stage_graph), n(check_if_solution_is_leaked))

g.add_node(initiate_main_stage)
g.add_edge(n(initiate_main_stage), "end_of_loop")

g.add_node(n(main_stage_graph), main_stage_graph)
g.add_edge(n(main_stage_graph), n(check_if_solution_is_leaked))

g.add_node(n(final_assessment_stage_graph), final_assessment_stage_graph)
g.add_edge(n(final_assessment_stage_graph), "end_of_loop")

g.add_node(n(check_if_solution_is_leaked), check_if_solution_is_leaked)
g.add_edge(n(check_if_solution_is_leaked), "end_of_loop")

g.add_node("end_of_loop", RunnablePassthrough())
g.add_edge("end_of_loop", n(stage_router))

os.makedirs("./data/graph_checkpoints", exist_ok=True)
db_path = os.path.join(".", "data", "graph_checkpoints", "checkpoints.sqlite")
conn = sqlite3.connect(db_path, check_same_thread=False)
memory = SqliteSaver(conn)

main_graph = g.compile(checkpointer=memory, interrupt_before=["end_of_loop"])

with open("./agents/graph_diagrams/main_graph.png", "wb") as f:
    f.write(main_graph.get_graph(xray=1).draw_mermaid_png())
