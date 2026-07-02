from typing import Any
from uuid import UUID

from pydantic import BaseModel

from app.modules.agent.schemas import AgentWorkflowCreate
from app.modules.agent.tools import ToolContext, agent_tool


class WorkflowIdInput(BaseModel):
    workflow_id: UUID


class WorkflowEnabledInput(BaseModel):
    workflow_id: UUID
    enabled: bool


class WorkflowRunIdInput(BaseModel):
    run_id: UUID


def _service(context: ToolContext) -> Any:
    if context.agent_service is None:
        raise RuntimeError("Agent workflow tools require AgentService")
    return context.agent_service


@agent_tool(
    name="agent.list_workflow_capabilities",
    summary="查询可编排业务能力",
    method="GET",
    path="/agent/workflow-capabilities",
    output_hint="返回当前已注册 Agent 工具及其工作流可用性。",
)
async def list_workflow_capabilities(
    context: ToolContext, _: BaseModel
) -> dict[str, Any]:
    return _service(context)._workflow_capabilities()


@agent_tool(
    name="agent.create_workflow",
    summary="创建助手工作流",
    input_model=AgentWorkflowCreate,
    write=True,
    risk_level="medium",
    workflow_allowed=False,
    method="POST",
    path="/agent/workflows",
)
async def create_workflow(
    context: ToolContext, data: AgentWorkflowCreate
) -> dict[str, Any]:
    workflow = await _service(context)._create_workflow_from_request(
        context.db,
        request=data,
        user_id=context.user_id,
        session_id=context.session_id,
    )
    return {
        "workflow": _service(context)._workflow_out(workflow).model_dump(mode="json")
    }


@agent_tool(
    name="agent.list_workflows",
    summary="查询我的助手工作流",
    workflow_allowed=False,
    method="GET",
    path="/agent/workflows",
)
async def list_workflows(context: ToolContext, _: BaseModel) -> dict[str, Any]:
    workflows = await _service(context).repo.list_workflows(
        context.db,
        user_id=context.user_id,
    )
    return {
        "workflows": [
            _service(context)._workflow_out(workflow).model_dump(mode="json")
            for workflow in workflows
        ]
    }


@agent_tool(
    name="agent.get_workflow",
    summary="查看助手工作流详情",
    input_model=WorkflowIdInput,
    workflow_allowed=False,
    method="GET",
    path="/agent/workflows/{workflow_id}",
)
async def get_workflow(context: ToolContext, data: WorkflowIdInput) -> dict[str, Any]:
    workflow = await _service(context)._get_user_workflow(
        context.db,
        {"workflow_id": data.workflow_id},
        user_id=context.user_id,
    )
    return {
        "workflow": _service(context)._workflow_out(workflow).model_dump(mode="json")
    }


@agent_tool(
    name="agent.set_workflow_enabled",
    summary="启停助手工作流",
    input_model=WorkflowEnabledInput,
    write=True,
    risk_level="medium",
    workflow_allowed=False,
    method="POST",
    path="/agent/workflows/{workflow_id}/enabled",
)
async def set_workflow_enabled(
    context: ToolContext, data: WorkflowEnabledInput
) -> dict[str, Any]:
    workflow = await _service(context)._get_user_workflow(
        context.db,
        {"workflow_id": data.workflow_id},
        user_id=context.user_id,
    )
    workflow.status = "enabled" if data.enabled else "disabled"
    workflow.updated_by = context.user_id
    await context.db.flush()
    workflow = await _service(context)._refetch_workflow(context.db, workflow)
    return {
        "workflow": _service(context)._workflow_out(workflow).model_dump(mode="json")
    }


@agent_tool(
    name="agent.run_workflow",
    summary="运行助手工作流",
    input_model=WorkflowIdInput,
    write=True,
    risk_level="medium",
    workflow_allowed=False,
    method="POST",
    path="/agent/workflows/{workflow_id}/run",
)
async def run_workflow(context: ToolContext, data: WorkflowIdInput) -> dict[str, Any]:
    workflow = await _service(context)._get_user_workflow(
        context.db,
        {"workflow_id": data.workflow_id},
        user_id=context.user_id,
    )
    return await _service(context)._start_workflow_run(
        context.db,
        workflow=workflow,
        user_id=context.user_id,
        session_id=context.session_id,
    )


@agent_tool(
    name="agent.cancel_workflow_run",
    summary="取消助手工作流运行",
    input_model=WorkflowRunIdInput,
    write=True,
    risk_level="medium",
    workflow_allowed=False,
    method="POST",
    path="/agent/workflow-runs/{run_id}/cancel",
)
async def cancel_workflow_run(
    context: ToolContext, data: WorkflowRunIdInput
) -> dict[str, Any]:
    run = await _service(context)._get_user_workflow_run(
        context.db,
        {"run_id": data.run_id},
        user_id=context.user_id,
    )
    if run.status not in {"succeeded", "failed", "cancelled"}:
        from datetime import UTC, datetime

        run.status = "cancelled"
        run.finished_at = datetime.now(UTC)
        run.updated_by = context.user_id
        await context.db.flush()
        run = await _service(context)._refetch_workflow_run(context.db, run)
    return {"run": _service(context)._workflow_run_out(run).model_dump(mode="json")}


@agent_tool(
    name="agent.get_workflow_run",
    summary="查看助手工作流运行状态",
    input_model=WorkflowRunIdInput,
    workflow_allowed=False,
    method="GET",
    path="/agent/workflow-runs/{run_id}",
)
async def get_workflow_run(
    context: ToolContext, data: WorkflowRunIdInput
) -> dict[str, Any]:
    run = await _service(context)._get_user_workflow_run(
        context.db,
        {"run_id": data.run_id},
        user_id=context.user_id,
    )
    return {"run": _service(context)._workflow_run_out(run).model_dump(mode="json")}
