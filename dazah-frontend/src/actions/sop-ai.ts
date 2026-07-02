'use server'

/**
 * SOP AI 模块 Server Actions
 * 文件合规校验模块的 API 调用
 */

import { revalidatePath } from 'next/cache'
import {
  SingleCheckRequest,
  BatchCheckRequest,
  ProblemHandleRequest,
  CheckRecordFilter,
  ApiResponse,
  CheckMain,
  CheckMainDetail,
  CheckProblem,
  SopAiConfig,
  ScheduledJob,
  PaginatedResponse,
  CheckTaskResponse,
  BatchCheckResult,
} from '@/types/sop-ai'

// API 基础路径
const API_BASE_URL = process.env.API_BASE_URL || 'http://localhost:8000/api/v1'

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
    throw new Error(data.message || `API Error: ${response.status}`)
  }

  return data
}

// ============ 配置相关接口 ============

/**
 * 获取配置列表
 */
export async function getConfigs(): Promise<SopAiConfig[]> {
  const response = await fetchAPI<ApiResponse<SopAiConfig[]>>('/sop-ai/config')
  return response.data || []
}

/**
 * 获取单个配置
 */
export async function getConfig(configKey: string): Promise<string> {
  const response = await fetchAPI<ApiResponse<{ config_key: string; config_value: string }>>(
    `/sop-ai/config/${configKey}`
  )
  return response.data?.config_value || ''
}

/**
 * 更新配置
 */
export async function updateConfig(
  configKey: string,
  configValue: string,
  description?: string,
  operator?: string
): Promise<SopAiConfig> {
  const response = await fetchAPI<ApiResponse<SopAiConfig>>(`/sop-ai/config/${configKey}`, {
    method: 'PUT',
    body: JSON.stringify({
      config_value: configValue,
      description,
      operator,
    }),
  })
  revalidatePath('/quality/sop-ai')
  return response.data
}

// ============ 单文件预审接口 ============

/**
 * 单文件预审
 */
export async function singleCheck(
  request: SingleCheckRequest
): Promise<CheckTaskResponse> {
  const response = await fetchAPI<ApiResponse<CheckTaskResponse>>('/sop-ai/check/single', {
    method: 'POST',
    body: JSON.stringify(request),
  })
  revalidatePath('/quality/sop-ai')
  return response.data
}

// ============ 批量巡检接口 ============

/**
 * 批量巡检
 */
export async function batchCheck(
  request: BatchCheckRequest
): Promise<BatchCheckResult> {
  const response = await fetchAPI<ApiResponse<BatchCheckResult>>('/sop-ai/check/batch', {
    method: 'POST',
    body: JSON.stringify(request),
  })
  revalidatePath('/quality/sop-ai')
  return response.data
}

// ============ 记录查询接口 ============

/**
 * 获取校验记录列表
 */
export async function getCheckRecords(
  filter?: CheckRecordFilter
): Promise<PaginatedResponse<CheckMain>> {
  const searchParams = new URLSearchParams()
  if (filter?.status) searchParams.set('status', filter.status)
  if (filter?.file_code) searchParams.set('file_code', filter.file_code)
  if (filter?.start_date) searchParams.set('start_date', filter.start_date)
  if (filter?.end_date) searchParams.set('end_date', filter.end_date)
  if (filter?.page) searchParams.set('page', String(filter.page))
  if (filter?.page_size) searchParams.set('page_size', String(filter.page_size))

  const query = searchParams.toString() ? `?${searchParams.toString()}` : ''
  const response = await fetchAPI<ApiResponse<PaginatedResponse<CheckMain>>>(
    `/sop-ai/records${query}`
  )
  return response.data
}

/**
 * 获取校验记录详情
 */
export async function getCheckRecordDetail(id: string): Promise<CheckMainDetail> {
  const response = await fetchAPI<ApiResponse<CheckMainDetail>>(`/sop-ai/records/${id}`)
  return response.data
}

/**
 * 导出校验报告
 */
export async function exportCheckReport(
  id: string,
  format: 'excel' | 'pdf' = 'excel',
  includeProblems: boolean = true
): Promise<{ download_url: string }> {
  const response = await fetchAPI<ApiResponse<{ download_url: string }>>(
    `/sop-ai/export/${id}?format=${format}&include_problems=${includeProblems}`
  )
  return response.data
}

// ============ 问题处理接口 ============

/**
 * 处理问题
 */
export async function handleProblem(
  problemId: string,
  request: ProblemHandleRequest
): Promise<{ id: string; handle_status: string; ignore_reason?: string }> {
  const response = await fetchAPI<ApiResponse<{ id: string; handle_status: string; ignore_reason?: string }>>(
    `/sop-ai/problems/${problemId}`,
    {
      method: 'PUT',
      body: JSON.stringify(request),
    }
  )
  revalidatePath('/quality/sop-ai')
  return response.data
}

// ============ 定时任务接口 ============

/**
 * 获取定时任务列表
 */
export async function getScheduledJobs(): Promise<ScheduledJob[]> {
  const response = await fetchAPI<ApiResponse<ScheduledJob[]>>('/sop-ai/jobs')
  return response.data || []
}

/**
 * 创建定时任务
 */
export async function createScheduledJob(
  job: Omit<ScheduledJob, 'next_run_time' | 'last_run_time' | 'run_count'>
): Promise<ScheduledJob> {
  const response = await fetchAPI<ApiResponse<ScheduledJob>>('/sop-ai/jobs', {
    method: 'POST',
    body: JSON.stringify(job),
  })
  revalidatePath('/quality/sop-ai')
  return response.data
}

/**
 * 删除定时任务
 */
export async function deleteScheduledJob(jobId: string): Promise<boolean> {
  const response = await fetchAPI<ApiResponse<{ job_id: string; deleted: boolean }>>(
    `/sop-ai/jobs/${jobId}`,
    {
      method: 'DELETE',
    }
  )
  revalidatePath('/quality/sop-ai')
  return response.data.deleted
}