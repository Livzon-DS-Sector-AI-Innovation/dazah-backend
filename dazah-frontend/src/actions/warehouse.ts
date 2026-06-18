'use server'

/**
 * 仓储管理模块 Server Actions
 * 包含试剂/标准品领用、报废相关接口调用
 */

import { revalidatePath } from 'next/cache'

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

// ============ AI 相关接口 ============

/**
 * AI 生成合规领用事由
 * @param billNo 领用单据编号
 * @param userInput 用户补充描述内容
 * @param operator 当前操作人账号
 */
export async function generateUsageReason(
  billNo: string,
  userInput: string,
  operator: string
): Promise<{ code: number; message: string; data: { result: string } }> {
  const response = await fetchAPI<{ code: number; message: string; data: { result: string } }>(
    '/reagent/ai/gen/reason',
    {
      method: 'POST',
      body: JSON.stringify({
        bill_no: billNo,
        user_input: userInput,
        operator: operator,
      }),
    }
  )
  return response
}

/**
 * AI 生成标准报废原因
 * @param billNo 报废单据编号
 * @param userInput 用户补充描述内容
 * @param operator 当前操作人账号
 */
export async function generateScrapReason(
  billNo: string,
  userInput: string,
  operator: string
): Promise<{ code: number; message: string; data: { result: string } }> {
  const response = await fetchAPI<{ code: number; message: string; data: { result: string } }>(
    '/reagent/ai/gen/scrap',
    {
      method: 'POST',
      body: JSON.stringify({
        bill_no: billNo,
        user_input: userInput,
        operator: operator,
      }),
    }
  )
  return response
}

/**
 * AI 试剂异常分析
 * @param billNo 试剂单据编号
 * @param reagentName 试剂名称
 * @param problemDescription 问题描述
 * @param storageConditions 储存条件
 * @param operator 当前操作人账号
 */
export async function generateAnalyse(
  billNo: string,
  reagentName: string,
  problemDescription: string,
  storageConditions: string,
  operator: string
): Promise<{ code: number; message: string; data: { result: string } }> {
  const response = await fetchAPI<{ code: number; message: string; data: { result: string } }>(
    '/reagent/ai/gen/analyse',
    {
      method: 'POST',
      body: JSON.stringify({
        bill_no: billNo,
        reagent_name: reagentName,
        problem_description: problemDescription,
        storage_conditions: storageConditions,
        operator: operator,
      }),
    }
  )
  return response
}

// ============ 领用相关接口 ============

/**
 * 获取试剂领用列表
 */
export async function getReagentUsages(params?: {
  status?: string
  start_date?: string
  end_date?: string
  page?: number
  page_size?: number
}) {
  const searchParams = new URLSearchParams()
  if (params?.status) searchParams.set('status', params.status)
  if (params?.start_date) searchParams.set('start_date', params.start_date)
  if (params?.end_date) searchParams.set('end_date', params.end_date)
  if (params?.page) searchParams.set('page', String(params.page))
  if (params?.page_size) searchParams.set('page_size', String(params.page_size))

  return fetchAPI(`/reagent/usage?${searchParams.toString()}`)
}

/**
 * 创建试剂领用记录
 */
export async function createReagentUsage(data: {
  reagent_id: string
  quantity: number
  usage_reason: string
}) {
  const response = await fetchAPI('/reagent/usage', {
    method: 'POST',
    body: JSON.stringify(data),
  })
  revalidatePath('/warehouse')
  return response
}

/**
 * 提交试剂领用记录
 */
export async function submitReagentUsage(id: string) {
  const response = await fetchAPI(`/reagent/usage/${id}/submit`, {
    method: 'POST',
  })
  revalidatePath('/warehouse')
  return response
}

// ============ 报废相关接口 ============

/**
 * 获取试剂报废列表
 */
export async function getReagentScraps(params?: {
  status?: string
  scrap_type?: string
  start_date?: string
  end_date?: string
  page?: number
  page_size?: number
}) {
  const searchParams = new URLSearchParams()
  if (params?.status) searchParams.set('status', params.status)
  if (params?.scrap_type) searchParams.set('scrap_type', params.scrap_type)
  if (params?.start_date) searchParams.set('start_date', params.start_date)
  if (params?.end_date) searchParams.set('end_date', params.end_date)
  if (params?.page) searchParams.set('page', String(params.page))
  if (params?.page_size) searchParams.set('page_size', String(params.page_size))

  return fetchAPI(`/reagent/scrap?${searchParams.toString()}`)
}

/**
 * 创建试剂报废记录
 */
export async function createReagentScrap(data: {
  reagent_id: string
  quantity: number
  scrap_reason: string
  scrap_type: string
}) {
  const response = await fetchAPI('/reagent/scrap', {
    method: 'POST',
    body: JSON.stringify(data),
  })
  revalidatePath('/warehouse')
  return response
}

/**
 * 提交试剂报废记录
 */
export async function submitReagentScrap(id: string) {
  const response = await fetchAPI(`/reagent/scrap/${id}/submit`, {
    method: 'POST',
  })
  revalidatePath('/warehouse')
  return response
}

// ============ 台账相关接口 ============

/**
 * 获取试剂台账列表
 */
export async function getReagentInventory(params?: {
  keyword?: string
  status?: string
  page?: number
  page_size?: number
}) {
  const searchParams = new URLSearchParams()
  if (params?.keyword) searchParams.set('keyword', params.keyword)
  if (params?.status) searchParams.set('status', params.status)
  if (params?.page) searchParams.set('page', String(params.page))
  if (params?.page_size) searchParams.set('page_size', String(params.page_size))

  return fetchAPI(`/reagent/inventory?${searchParams.toString()}`)
}

/**
 * 获取试剂详情
 */
export async function getReagentById(id: string) {
  return fetchAPI(`/reagent/inventory/${id}`)
}