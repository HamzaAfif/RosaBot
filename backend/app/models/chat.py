from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(
        ...,
        min_length=1,
        description="The staff member's question for RosaBot.",
        examples=["Does the Pisco Sour have egg?"],
    )
    conversation_id: str = Field(
        "default",
        description=(
            "Identifies the conversation. Send the same value across messages "
            "to keep context; use a new value to start fresh."
        ),
        examples=["table-7-bartender"],
    )


class ChatResponse(BaseModel):
    reply: str = Field(..., description="RosaBot's answer.")