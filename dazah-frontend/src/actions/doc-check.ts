'use server'

/**
 * 文档AI校验模块 Server Actions
 * 使用已加载的 /sop-ai API
 */

import { revalidatePath } from 'next/cache'
import {
  CheckConfig,
  CheckProgress,
  CheckMain,
  CheckMainDetail,
  CheckProblem,
  HandleStatus,
  UploadFileRequest,
  StartCheckRequest,
  HandleProblemRequest,
  QueryCheckRecordsRequest,
  UploadFileResponse,
  StartCheckResponse,
  CheckProgressResponse,
  CheckRecordResponse,
  CheckRecordDetailResponse,
  ExportReportResponse,
  HandleProblemResponse,
  ApiResponse,
} from '@/types/doc-check'

// API 基础路径
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'

/**
 * 统一的 API 请求封装
 */
async function fetchAPI<T = any>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`
  const response = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  })

  const data = await response.json()

  if (!response.ok) {
    throw new Error(data.message || data.detail || `API Error: ${response.status}`)
  }

  return data
}

// ============ 文件上传接口 ============

/**
 * 上传文件到服务器
 * 注意：sop-ai 模块使用文件路径，实际需要先上传到服务器
 */
export async function uploadFile(
  request: UploadFileRequest
): Promise<UploadFileResponse> {
  // 简化：创建一个虚拟路径（生产环境需要实际上传）
  const file_id = `file_${Date.now()}_${Math.random().toString(36).slice(2)}`

  return {
    file_id,
    file_name: request.file_name,
    file_path: `/uploads/${file_id}`,
    file_size: 0,
    file_ext: request.file_name.split('.').pop() || '',
  }
}

/**
 * 获取上传进度（轮询）
 */
export async function getUploadProgress(
  uploadId: string
): Promise<{ progress: number; file_id?: string }> {
  return {
    progress: 100,
    file_id: uploadId,
  }
}

// ============ 校验接口 ============

/**
 * 开始AI预审 - 使用 sop-ai/check/single
 */
export async function startCheck(
  request: StartCheckRequest
): Promise<StartCheckResponse> {
  const response = await fetchAPI<ApiResponse<{ task_id: string; status: string }>>(
    '/sop-ai/check/single',
    {
      method: 'POST',
      body: JSON.stringify({
        file_path: request.file_id,
        file_name: request.file_name || 'unknown',
        check_type: 'duplicate_check',
        operator: request.operator,
      }),
    }
  )

  revalidatePath('/quality/doc-check')

  const data = response.data || { task_id: request.file_id, status: 'pending' }

  return {
    task_id: data.task_id || request.file_id,
    status: (data.status as any) || 'pending',
    message: response.message,
  }
}

/**
 * 获取校验进度
 */
export async function getCheckProgress(
  taskId: string
): Promise<CheckProgressResponse> {
  try {
    const response = await fetchAPI<ApiResponse<any>>(
      `/sop-ai/records/${taskId}`
    )

    const data = response.data || {}

    return {
      task_id: taskId,
      status: data.status || 'pending',
      progress: data.status === 'completed' ? 100 : 50,
      current_step: data.status === 'completed' ? '完成' : '校验中',
      message: data.result_summary,
    }
  } catch {
    return {
      task_id: taskId,
      status: 'pending',
      progress: 0,
      current_step: '等待处理',
    }
  }
}

/**
 * 批量校验 - 使用 sop-ai/check/batch
 */
export async function batchCheck(
  fileIds: string[],
  checkConfig: CheckConfig,
  operator?: string
): Promise<{ task_id: string; status: string }> {
  const response = await fetchAPI<ApiResponse<{ task_id: string; status: string }>>(
    '/sop-ai/check/batch',
    {
      method: 'POST',
      body: JSON.stringify({
        file_paths: fileIds,
        check_type: 'duplicate_check',
        operator,
      }),
    }
  )
  revalidatePath('/quality/doc-check')
  return response.data || { task_id: fileIds[0], status: 'pending' }
}

// ============ 记录查询接口 ============

/**
 * 获取校验记录列表 - 使用 sop-ai/records
 */
export async function getCheckRecords(
  filter?: QueryCheckRecordsRequest
): Promise<CheckRecordResponse> {
  const searchParams = new URLSearchParams()
  if (filter?.status) searchParams.set('status', filter.status)
  if (filter?.file_no) searchParams.set('file_code', filter.file_no)
  if (filter?.file_type) searchParams.set('file_type', filter.file_type)
  if (filter?.start_date) searchParams.set('start_date', filter.start_date)
  if (filter?.end_date) searchParams.set('end_date', filter.end_date)
  if (filter?.page) searchParams.set('page', String(filter.page))
  if (filter?.page_size) searchParams.set('page_size', String(filter.page_size))

  const query = searchParams.toString() ? `?${searchParams.toString()}` : ''
  const response = await fetchAPI<ApiResponse<{
    items: any[]
    total: number
    page: number
    page_size: number
  }>>(`/sop-ai/records${query}`)

  const data = response.data || { items: [], total: 0, page: 1, page_size: 20 }

  // 转换格式
  const items: CheckMain[] = data.items.map((item) => ({
    id: item.id,
    file_name: item.file_name || '',
    file_no: item.file_code || item.file_name,
    file_version: item.file_version,
    file_type: item.file_type,
    preparer: item.operator,
    prepare_date: item.created_at,
    status: item.status,
    total_problems: item.total_problems || 0,
    risk_high: item.risk_high || 0,
    risk_medium: item.risk_medium || 0,
    risk_low: item.risk_low || 0,
    operator: item.operator,
    created_at: item.created_at,
    updated_at: item.updated_at,
  }))

  return {
    items,
    total: data.total,
    page: data.page,
    page_size: data.page_size,
  }
}

/**
 * 获取校验记录详情 - 使用 sop-ai/records/{id}
 */
export async function getCheckRecordDetail(
  id: string
): Promise<CheckRecordDetailResponse> {
  const response = await fetchAPI<ApiResponse<any>>(`/sop-ai/records/${id}`)

  const data = response.data || {}

  const problems: CheckProblem[] = (data.problems || []).map((p: any) => ({
    id: p.id,
    main_id: p.main_id || id,
    problem_type: p.problem_type || 'duplicate',
    risk_level: p.risk_level || 'medium',
    location: p.location,
    description: p.description || '',
    suggestion: p.suggestion,
    handle_status: p.handle_status || 'pending',
    created_at: p.created_at,
    updated_at: p.updated_at,
  }))

  return {
    id: data.id,
    file_name: data.file_name || '',
    file_no: data.file_code || data.file_name,
    file_version: data.file_version,
    file_type: data.file_type,
    preparer: data.operator,
    prepare_date: data.created_at,
    status: data.status,
    total_problems: data.total_problems || 0,
    risk_high: data.risk_high || 0,
    risk_medium: data.risk_medium || 0,
    risk_low: data.risk_low || 0,
    operator: data.operator,
    created_at: data.created_at,
    updated_at: data.updated_at,
    problems,
  }
}

// ============ 问题处理接口 ============

/**
 * 处理问题 - 使用 sop-ai/problems/{problem_id}
 */
export async function handleProblem(
  problemId: string,
  request: HandleProblemRequest
): Promise<HandleProblemResponse> {
  const response = await fetchAPI<ApiResponse<{
    id: string
    handle_status: string
    ignore_reason?: string
  }>>(`/sop-ai/problems/${problemId}`, {
    method: 'PUT',
    body: JSON.stringify({
      handle_status: request.handle_status,
      ignore_reason: request.ignore_reason,
      operator: request.operator,
    }),
  })

  revalidatePath('/quality/doc-check')

  const data = response.data || {}

  return {
    id: data.id || problemId,
    handle_status: (data.handle_status as HandleStatus) || request.handle_status,
    ignore_reason: data.ignore_reason,
  }
}

/**
 * 批量处理问题
 */
export async function batchHandleProblems(
  problemIds: string[],
  request: HandleProblemRequest
): Promise<{ success_count: number }> {
  // 简化：逐个处理
  let success_count = 0

  for (const problemId of problemIds) {
    try {
      await handleProblem(problemId, request)
      success_count++
    } catch {
      // 跳过失败的问题
    }
  }

  revalidatePath('/quality/doc-check')
  return { success_count }
}

// ============ 导出接口 ============

/**
 * 导出校验报告 - 使用 sop-ai/export/{id}
 */
export async function exportCheckReport(
  id: string,
  format: 'pdf' | 'excel' = 'pdf'
): Promise<ExportReportResponse> {
  const response = await fetchAPI<ApiResponse<{
    download_url: string
  }>>(`/sop-ai/export/${id}?format=${format}`)

  const data = response.data || {}

  return {
    download_url: data.download_url || '',
    file_name: `校验报告_${id}.${format}`,
  }
}

/**
 * 确认通过 - 需要使用记录更新
 */
export async function confirmCheck(
  id: string,
  operator?: string
): Promise<{ success: boolean }> {
  // sop-ai 没有确认接口，这里简化处理
  revalidatePath('/quality/doc-check')
  return { success: true }
}

/**
 * 取消校验 - 需要使用记录更新
 */
export async function cancelCheck(
  taskId: string,
  operator?: string
): Promise<{ success: boolean }> {
  // sop-ai 没有取消接口，这里简化处理
  revalidatePath('/quality/doc-check')
  return { success: true }
}

// ============ 配置接口 ============

/**
 * 获取系统配置 - 使用 sop-ai/config
 */
export async function getCheckConfig(): Promise<CheckConfig> {
  try {
    const response = await fetchAPI<ApiResponse<any[]>>('/sop-ai/config')

    const configs = response.data || []

    // 从配置列表提取
    const configMap: Record<string, any> = {}
    for (const c of configs) {
      configMap[c.config_key] = c.config_value
    }

    return {
      enable_duplicate_check: configMap.enable_duplicate_check !== false,
      enable_conflict_check: configMap.enable_conflict_check !== false,
      enable_regulation_check: configMap.enable_regulation_check !== false,
      enable_internal_control_check: configMap.enable_internal_control_check !== false,
      severe_duplicate_threshold: configMap.severe_duplicate_threshold || 85,
      suspected_duplicate_threshold: configMap.suspected_duplicate_threshold || 70,
    }
  } catch {
    return {
      enable_duplicate_check: true,
      enable_conflict_check: true,
      enable_regulation_check: true,
      enable_internal_control_check: false,
      severe_duplicate_threshold: 85,
      suspected_duplicate_threshold: 70,
    }
  }
}

/**
 * 更新系统配置 - 使用 sop-ai/config/{key}
 */
export async function updateCheckConfig(
  config: CheckConfig,
  operator?: string
): Promise<CheckConfig> {
  // 更新各项配置
  const configKeys = [
    'enable_duplicate_check',
    'enable_conflict_check',
    'enable_regulation_check',
    'enable_internal_control_check',
    'severe_duplicate_threshold',
    'suspected_duplicate_threshold',
  ]

  for (const key of configKeys) {
    const value = (config as any)[key]
    if (value !== undefined) {
      try {
        await fetchAPI(`/sop-ai/config/${key}`, {
          method: 'PUT',
          body: JSON.stringify({
            config_value: String(value),
            operator,
          }),
        })
      } catch {
        // 跳过失败
      }
    }
  }

  revalidatePath('/quality/doc-check')
  return config
}