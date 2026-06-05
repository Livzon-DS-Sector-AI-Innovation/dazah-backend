"""AI platform request and response schemas."""

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: str = Field(..., description="消息角色: system, user, assistant")
    content: str = Field(..., description="消息内容")


class HrPageContext(BaseModel):
    page: str = Field(..., description="当前页面标识")
    filters: dict[str, str | None] | None = Field(
        None, description="当前筛选条件"
    )
    selected_ids: list[str] | None = Field(None, description="选中的行ID")
    data_summary: dict[str, str | int | None] | None = Field(
        None, description="数据摘要"
    )


class ChatRequest(BaseModel):
    messages: list[ChatMessage] = Field(..., description="对话历史")
    page_context: HrPageContext | None = Field(
        None, description="页面上下文"
    )
