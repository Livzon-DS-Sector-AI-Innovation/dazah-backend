export interface SubMenuItem {
  key: string
  label: string
  path?: string
  children?: SubMenuItem[]
}

export interface ModuleMenu {
  key: string
  label: string
  icon: string
  path: string
  children: SubMenuItem[]
}

export const moduleMenus: ModuleMenu[] = [
  {
    key: "production",
    label: "生产管理",
    icon: "factory",
    path: "/production",
    children: [
      { key: "batches", label: "批次管理", path: "/production/batches" },
      { key: "plan", label: "生产计划", path: "/production/plan" },
      { key: "process", label: "工艺规程", path: "/production/process" },
      { key: "records", label: "生产记录", path: "/production/records" },
      { key: "balance", label: "物料平衡", path: "/production/balance" },
    ],
  },
  {
    key: "equipment",
    label: "设备管理",
    icon: "cog",
    path: "/equipment",
    children: [
      { key: "assets", label: "设备台账", path: "/equipment/assets" },
      { key: "maintenance", label: "维护保养", path: "/equipment/maintenance" },
      { key: "inspection", label: "设备巡检", path: "/equipment/inspection" },
      { key: "spare-parts", label: "备件管理", path: "/equipment/spare-parts" },
    ],
  },
  {
    key: "energy",
    label: "能源管理",
    icon: "bolt",
    path: "/energy",
    children: [
      { key: "monitor", label: "能耗监控", path: "/energy/monitor" },
      { key: "report", label: "能源报表", path: "/energy/report" },
      { key: "saving", label: "节能措施", path: "/energy/saving" },
    ],
  },
  {
    key: "safety",
    label: "安全管理",
    icon: "shield",
    path: "/safety",
    children: [
      { key: "check", label: "安全检查", path: "/safety/check" },
      { key: "hazard", label: "隐患排查", path: "/safety/hazard" },
      { key: "accident", label: "事故管理", path: "/safety/accident" },
      { key: "training", label: "安全培训", path: "/safety/training" },
    ],
  },
  {
    key: "rd",
    label: "研发管理",
    icon: "beaker",
    path: "/rd",
    children: [
      { key: "projects", label: "研发项目", path: "/rd/projects" },
      { key: "experiments", label: "实验记录", path: "/rd/experiments" },
      { key: "reports", label: "研发报告", path: "/rd/reports" },
    ],
  },
  {
    key: "registration",
    label: "注册管理",
    icon: "document",
    path: "/registration",
    children: [
      { key: "filing", label: "注册申报", path: "/registration/filing" },
      { key: "regulation", label: "法规跟踪", path: "/registration/regulation" },
      { key: "documents", label: "文件管理", path: "/registration/documents" },
    ],
  },
  {
    key: "quality",
    label: "质量管理",
    icon: "check-circle",
    path: "/quality",
    children: [
      { key: "quality-dashboard", label: "仪表盘", path: "/quality" },
      {
        key: "reagent-management",
        label: "试剂管理",
        children: [
          { key: "reagent-list", label: "试剂", path: "/quality/reagent" },
          { key: "reagent-reminder-settings", label: "试剂提醒设置", path: "/quality/reagent/reminder" },
        ],
      },
      {
        key: "static-data",
        label: "业务静态数据",
        children: [
          { key: "storage-condition", label: "贮存条件", path: "/quality/static-data/storage-condition" },
          { key: "hplc-reference", label: "液相对照品", path: "/quality/static-data/hplc-reference" },
          { key: "chrom-column", label: "色谱柱", path: "/quality/static-data/chrom-column" },
          { key: "medium", label: "培养基", path: "/quality/static-data/medium" },
          { key: "standard", label: "标准品", path: "/quality/static-data/standard" },
          { key: "static-data-all", label: "全部数据", path: "/quality/static-data" },
        ],
      },
      {
        key: "instrument",
        label: "仪器校准管理",
        children: [
          { key: "instrument-dashboard", label: "仪表盘", path: "/quality/instrument" },
          { key: "instrument-list", label: "仪器台账", path: "/quality/instrument/list" },
          { key: "instrument-settings", label: "提醒设置", path: "/quality/instrument/settings" },
        ],
      },

      {
        key: "stability",
        label: "稳定性实验管理",
        children: [
          { key: "stability-plan", label: "方案录入", path: "/quality/stability/plan" },
          { key: "stability-result", label: "检测结果", path: "/quality/stability/result" },
          { key: "stability-report", label: "总结报告", path: "/quality/stability/report" },
          { key: "stability-settings", label: "提醒设置", path: "/quality/stability/settings" },
        ],
      },

      {
        key: "deviation-automation",
        label: "偏差报告自动化",
        children: [
          { key: "deviation-automation-create", label: "新建偏差报告", path: "/quality/deviation-automation/create" },
          { key: "deviation-automation-history", label: "历史任务查询", path: "/quality/deviation-automation/history" },
          { key: "deviation-automation-sop", label: "SOP规则管理", path: "/quality/deviation-automation/sop" },
          { key: "deviation-automation-templates", label: "报告模板管理", path: "/quality/deviation-automation/templates" },
        ],
      },

      {
        key: "deviation-flow",
        label: "偏差流程提醒",
        children: [
          { key: "deviation-flow-create", label: "新建偏差任务", path: "/quality/deviation-flow/create" },
          { key: "deviation-flow-query", label: "偏差任务查询", path: "/quality/deviation-flow/query" },
          { key: "deviation-flow-settings", label: "偏差提醒设置", path: "/quality/deviation-flow/settings" },
        ],
      },

      { key: "ai-log", label: "AI交互日志", path: "/quality/ai-log" },
      { key: "ai-config", label: "AI配置设置", path: "/quality/ai-config" },
      {
        key: "sop-ai",
        label: "文件合规校验",
        children: [
          { key: "sop-ai-preview", label: "单文件预审", path: "/quality/sop-ai/preview" },
          { key: "sop-ai-batch", label: "批量巡检", path: "/quality/sop-ai/batch" },
          { key: "sop-ai-records", label: "记录台账", path: "/quality/sop-ai/records" },
        ],
      },
    ],
  },
  {
    key: "admin",
    label: "行政管理",
    icon: "building",
    path: "/admin",
    children: [
      { key: "notice", label: "公告通知", path: "/admin/notice" },
      { key: "meeting", label: "会议管理", path: "/admin/meeting" },
      { key: "approval", label: "文件审批", path: "/admin/approval" },
    ],
  },
  {
    key: "hr",
    label: "人事管理",
    icon: "users",
    path: "/hr",
    children: [
      { key: "profile", label: "员工档案", path: "/hr/profile" },
      { key: "attendance", label: "考勤管理", path: "/hr/attendance" },
      { key: "training", label: "培训管理", path: "/hr/training" },
    ],
  },
  {
    key: "warehouse",
    label: "仓储管理",
    icon: "archive",
    path: "/warehouse",
    children: [
      { key: "reagent", label: "试剂/标准品", path: "/warehouse" },
      { key: "inventory", label: "库存管理", path: "/warehouse/inventory" },
      { key: "inout", label: "出入库记录", path: "/warehouse/inout" },
      { key: "stocktake", label: "库存盘点", path: "/warehouse/stocktake" },
    ],
  },
  {
    key: "purchasing",
    label: "采购管理",
    icon: "cart",
    path: "/purchasing",
    children: [
      { key: "request", label: "采购申请", path: "/purchasing/request" },
      { key: "supplier", label: "供应商管理", path: "/purchasing/supplier" },
      { key: "order", label: "采购订单", path: "/purchasing/order" },
    ],
  },
]

export function getModuleByKey(key: string): ModuleMenu | undefined {
  return moduleMenus.find((m) => m.key === key)
}
