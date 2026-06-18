# 试剂/标准品管理 AI 功能开发提示词

## 项目背景

**项目名称**：丽珠合成制药原料药QMS平台
**技术栈**：FastAPI + SQLAlchemy 2.0 async + PostgreSQL + Next.js 16 + Ant Design
**模块位置**：`dazah-frontend/src/` 前端 | `dazah-backend/app/modules/warehouse/` 后端

---

## 一、核心需求概述

### 业务场景
原料药QC实验室试剂/标准品领用台账管理，遵循GMP物料管控要求。

### 功能优先级

| 优先级 | 功能 | 说明 |
|--------|------|------|
| 🔴 P0 | AI生成领用事由 | 最高频，必做 |
| 🔴 P0 | AI生成报废原因 | 最高频，必做 |
| 🟡 P1 | 试剂异常分析 | 进阶功能 |
| 🟡 P1 | 领用风险评估 | 进阶功能 |
| 🟢 P2 | 批量文案润色 | 可选 |

---

## 二、后端接口开发

### 2.1 已完成的接口

| 接口 | 地址 | 说明 |
|------|------|------|
| 生成领用事由 | `POST /api/v1/reagent/ai/gen/reason` | ✅ 已完成 |
| 生成报废原因 | `POST /api/v1/reagent/ai/gen/scrap` | ✅ 已完成 |

### 2.2 待开发的进阶接口

#### 接口3：试剂异常分析
```
POST /api/v1/reagent/ai/gen/analyse
```

**入参**：
```json
{
  "bill_no": "string",           // 单据编号
  "reagent_name": "string",      // 试剂名称
  "problem_description": "string", // 问题描述（近效期/变质/储存异常）
  "storage_conditions": "string", // 储存条件
  "operator": "string"           // 操作人账号
}
```

**System提示词**：
> 针对试剂近效期、变质、储存异常等问题，分析潜在原因，并给出临时处置措施、长期预防管理建议，符合GMP实验室物料管控要求。

**日志类型**：`试剂异常分析`

**返回格式**：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "result": "分析结果文本...",
    "bill_no": "单据编号",
    "operate_type": "试剂异常分析"
  }
}
```

### 2.3 开发规范

**文件位置**：
- Service：`dazah-backend/app/modules/warehouse/reagent_service.py`
- API：`dazah-backend/app/modules/warehouse/reagent_api.py`
- Schema：`dazah-backend/app/modules/warehouse/reagent_schemas.py`

**固定System提示词配置**：
```python
# 领用事由
SYSTEM_PROMPT_REASON = (
    "你是制药QC实验室管理员，按照GMP物料管理规范，"
    "结合试剂用途，生成正式、合规的试剂领用事由，文字简洁专业。"
)

# 报废原因
SYSTEM_PROMPT_SCRAP = (
    "根据试剂实际情况，生成符合实验室台账要求的标准报废原因描述，"
    "用语严谨合规。"
)

# 异常分析（待开发）
SYSTEM_PROMPT_ANALYSE = (
    "针对试剂近效期、变质、储存异常等问题，分析潜在原因，"
    "并给出临时处置措施、长期预防管理建议，符合GMP实验室物料管控要求。"
)
```

**日志operate_type配置**：
| 接口 | operate_type |
|------|--------------|
| 领用事由 | 试剂领用辅助 |
| 报废原因 | 试剂报废辅助 |
| 异常分析 | 试剂异常分析 |

**要求**：
1. 入参非空校验，参数为空返回错误提示
2. 调用 `MinimaxAiUtil.chat()` 执行AI请求
3. 调用 `saveAiLog` 方法保存AI交互日志至 `qms_ai_log`
4. 全局异常捕获，AI服务异常统一返回兜底文案
5. 不改动原有业务逻辑（库存计算、效期拦截、审批流程）

---

## 三、前端页面开发

### 3.1 已完成的功能

| 功能 | 位置 | 说明 |
|------|------|------|
| 试剂台账列表 | `warehouse/page.tsx` | ✅ 已完成 |
| 领用弹窗+AI按钮 | `warehouse/page.tsx` | ✅ 已完成 |
| 报废弹窗+AI按钮 | `warehouse/page.tsx` | ✅ 已完成 |

### 3.2 待开发的进阶功能

#### 3.2.1 异常记录行AI分析按钮

**位置**：试剂台账列表中近效期/变质/异常记录行

**交互逻辑**：
1. 异常记录行显示【AI分析】按钮
2. 点击后弹出分析结果弹窗
3. 支持一键复制分析内容
4. 按钮样式与领用/报废弹窗AI按钮一致

**代码示例**：
```tsx
// 异常记录行操作列
{
  title: '操作',
  key: 'action',
  render: (_, record) => {
    // 仅近效期/异常状态显示AI分析按钮
    if (record.status === 'expired' || record.status === 'abnormal') {
      return (
        <Space>
          <Button
            type="link"
            size="small"
            icon={<RobotOutlined />}
            onClick={() => handleOpenAnalyseModal(record)}
          >
            AI分析
          </Button>
        </Space>
      )
    }
    return <span>-</span>
  }
}
```

#### 3.2.2 异常分析弹窗

**弹窗内容**：
- 试剂信息展示（名称、批号、有效期）
- AI分析结果展示区域
- 一键复制按钮
- GMP合规提示

### 3.3 AI按钮样式规范

**样式要求**（与仪器校准模块一致）：
```tsx
<Button
  type="link"
  size="small"
  icon={<RobotOutlined />}
  loading={aiLoading}
  onClick={handleAiGenerate}
  style={{
    color: '#1890ff',
    fontWeight: 'normal',
  }}
>
  AI生成事由
</Button>
```

**图标**：`RobotOutlined` from `@ant-design/icons`

**样式特点**：
- `type="link"` 链接样式
- `size="small"` 小尺寸
- 颜色：`#1890ff`
- 字重：正常（非加粗）

### 3.4 GMP合规提示

弹窗底部统一显示：
```tsx
<div style={{ color: '#999', fontSize: 12, textAlign: 'center' }}>
  <ExclamationCircleOutlined style={{ marginRight: 4 }} />
  AI内容仅作参考，最终以人工审核确认
</div>
```

### 3.5 错误处理

```tsx
const handleAiGenerate = async () => {
  setAiLoading(true)
  try {
    const result = await reagentActions.generateXxx(...)
    if (result.code === 200) {
      form.setFieldValue('xxx_reason', result.data.result)
      message.success('AI已生成，已回填至输入框')
    } else {
      message.error(result.message || 'AI服务异常，请手动填写')
    }
  } catch (error) {
    message.error('AI服务异常，请手动填写')
  } finally {
    setAiLoading(false)
  }
}
```

**关键约束**：
- AI功能异常不得阻塞单据保存、提交、审批等核心业务
- 接口异常弹出友好提示，不阻断用户操作

---

## 四、AI日志规范

### 4.1 qms_ai_log表结构

**Schema**：`qms`
**表名**：`qms_ai_log`

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID | 主键 |
| bill_no | VARCHAR(100) | 关联单据编号 |
| operate_type | VARCHAR(50) | 操作类型 |
| operator | VARCHAR(100) | 操作人账号 |
| system_prompt | TEXT | 系统提示词 |
| user_input | TEXT | 用户输入内容 |
| ai_response | TEXT | AI返回内容 |
| error_message | TEXT | 错误信息 |
| tokens_used | INTEGER | token使用量 |
| latency_ms | INTEGER | 响应耗时 |
| created_at | TIMESTAMP | 创建时间 |

### 4.2 日志保存方法

```python
from app.platform.ai.service import AiLogService

service = AiLogService(session)
log_id = await service.save_ai_log(
    operate_type="试剂领用辅助",
    operator="admin",
    system_prompt=SYSTEM_PROMPT_REASON,
    user_input=user_input,
    ai_response=ai_response,
    bill_no=bill_no,
    latency_ms=latency_ms,
)
```

---

## 五、功能示例

### 5.1 领用事由生成示例

**用户输入**：用于高效液相色谱仪检测有关物质

**AI生成输出**：
> 用于高效液相色谱仪（HPLC）检测有关物质及残留溶剂项目，满足原料药质量控制检验要求。

### 5.2 报废原因生成示例

**用户输入**：试剂过期了，剩余量不多

**AI生成输出**：
> 该试剂已超出有效期，剩余量较少无法继续用于检验实验，根据实验室物料管理要求，申请报废处理。

### 5.3 异常分析示例

**用户输入**：
- 试剂名称：甲醇
- 问题描述：临近效期（剩余15天）
- 储存条件：室温保存

**AI生成输出**：
> **原因分析**：
> 1. 领用计划不合理，单次领用量超出实际使用需求
> 2. 先进先出执行不严格，导致试剂积压
>
> **临时处置**：
> 1. 优先使用近效期试剂开展检验项目
> 2. 检查储存条件是否符合试剂说明书要求
>
> **长期预防**：
> 1. 优化领用计划，按需定量领用
> 2. 建立近效期试剂预警机制（效期前30天提醒）
> 3. 严格执行先进先出原则
> 4. 定期盘点库存，及时处理积压试剂

---

## 六、约束条件（GMP必守）

1. AI仅生成文本，不修改库存、不跳过审批、不自动判定
2. 生成内容支持人工二次编辑，人工最终确认
3. AI服务故障时，核心业务完全不受影响
4. `qms_ai_log` 日志禁止物理删除，长期留存可追溯
5. 原有业务逻辑（库存计算、效期拦截、审批流程）全部保留

---

## 七、相关文件路径

### 后端文件
- `dazah-backend/app/platform/ai/minimax_util.py` - MiniMax工具类
- `dazah-backend/app/platform/ai/models.py` - AI日志模型
- `dazah-backend/app/platform/ai/service.py` - AI日志服务
- `dazah-backend/app/modules/warehouse/reagent_schemas.py` - 请求响应Schema
- `dazah-backend/app/modules/warehouse/reagent_service.py` - 业务逻辑
- `dazah-backend/app/modules/warehouse/reagent_api.py` - API接口

### 前端文件
- `dazah-frontend/src/types/warehouse.ts` - 类型定义
- `dazah-frontend/src/actions/warehouse.ts` - Server Actions
- `dazah-frontend/src/app/(dashboard)/warehouse/page.tsx` - 页面组件

### 数据库迁移
- `dazah-backend/alembic/versions/20260608_0002_qms_ai_log.py` - AI日志表迁移

---

## 八、开发检查清单

- [ ] 后端接口入参非空校验
- [ ] 调用MinimaxAiUtil.chat()获取结果
- [ ] 调用saveAiLog保存日志
- [ ] 全局异常捕获，返回兜底文案
- [ ] 前端AI按钮样式与仪器校准一致
- [ ] AI按钮带loading状态
- [ ] 弹窗底部GMP合规提示
- [ ] 错误友好提示，不阻塞核心业务
- [ ] 原有业务逻辑不变