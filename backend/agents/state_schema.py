import datetime
import uuid
import operator
from typing import Annotated, TypedDict, Dict, List
from typing import Annotated, List, Literal
from pydantic import BaseModel, Field
from langgraph.graph.message import AnyMessage, add_messages


# ===========================================
#                VARIABLE SCHEMA
# ===========================================
class Goal(BaseModel):
    id: str = Field(description="The id of the goal.")
    name: str = Field(description="The name of the goal.")
    description: str = Field(description="The description of the goal.")


# ===========================================
#                REDUCER FUNCTIONS
# ===========================================
def replace_with_new_state(_, new):
    return new


# ===========================================
#                    STATE
# ===========================================
class InputState(BaseModel):
    goal_list: list[Goal] = Field(description="The list of goals.")


class OutputState(BaseModel):
    pass


class OverallState(InputState, OutputState):
    stage: Literal["goal_finder", "tour_guide"] = Field(default="goal_finder")
    greeting_msg_index: int = Field(default=0)

    messages: Annotated[list[AnyMessage], add_messages] = Field(default_factory=[])

    def stringify_messages(self):
        stringified_messages = "\n\n".join(
            [
                f">>{message.type.upper()}: {message.content}"
                for message in self.messages[1:]
            ]
        )
        return stringified_messages
