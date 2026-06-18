/**
 * 质量检验试剂/标准品管理 Server Actions
 */

import {
  Reagent,
  ReagentListResponse,
  CreateReagentRequest,
  UpdateReagentRequest,
  AiRecognizeResponse,
} from '@/types/reagent-quality'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'

/** 通用API调用 */
async function fetchAPI<T>(
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
    throw new Error(data.message || 'API请求失败')
  }

  return data
}

/** AI识别试剂标签图片 */
export async function recognizeReagentLabel(
  fileList: File[]
): Promise<{ code: number; message: string; data: AiRecognizeResponse | null }> {
  const formData = new FormData()

  fileList.forEach((file) => {
    formData.append('files', file)
  })

  const response = await fetch(`${API_BASE_URL}/quality/reagent/recognize`, {
    method: 'POST',
    body: formData,
  })

  const data = await response.json()
  return data
}

/** 获取下一个入场批号 */
export async function getNextIncomingLotNo(
  dateStr?: string
): Promise<{ code: number; message: string; data: { incoming_lot_no: string } | null }> {
  const url = dateStr
    ? `${API_BASE_URL}/quality/reagent/next-lot-no?date_str=${dateStr}`
    : `${API_BASE_URL}/quality/reagent/next-lot-no`

  const response = await fetch(url)
  return response.json()
}

/** 获取试剂列表 */
export async function getReagentList(params: {
  keyword?: string
  category?: string
  status?: string
  page?: number
  page_size?: number
}): Promise<{ code: number; message: string; data: ReagentListResponse }> {
  const searchParams = new URLSearchParams()
  if (params.keyword) searchParams.set('keyword', params.keyword)
  if (params.category) searchParams.set('category', params.category)
  if (params.status) searchParams.set('status', params.status)
  if (params.page) searchParams.set('page', String(params.page))
  if (params.page_size) searchParams.set('page_size', String(params.page_size))

  return fetchAPI(`/quality/reagent/list?${searchParams.toString()}`)
}

/** 获取试剂详情 */
export async function getReagentDetail(
  reagentId: string
): Promise<{ code: number; message: string; data: Reagent | null }> {
  return fetchAPI(`/quality/reagent/${reagentId}`)
}

/** 创建试剂记录 */
export async function createReagent(
  data: CreateReagentRequest
): Promise<{ code: number; message: string; data: Reagent | null }> {
  return fetchAPI(`/quality/reagent`, {
    method: 'POST',
    body: JSON.stringify(data),
  })
}

/** 更新试剂记录 */
export async function updateReagent(
  reagentId: string,
  data: UpdateReagentRequest
): Promise<{ code: number; message: string; data: Reagent | null }> {
  return fetchAPI(`/quality/reagent/${reagentId}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  })
}

/** 删除试剂记录 */
export async function deleteReagent(
  reagentId: string
): Promise<{ code: number; message: string; data: null }> {
  return fetchAPI(`/quality/reagent/${reagentId}`, {
    method: 'DELETE',
  })
}

/** 导出试剂台账Excel */
export async function exportReagentsExcel(params?: {
  keyword?: string
  category?: string
  status?: string
}): Promise<void> {
  const searchParams = new URLSearchParams()
  if (params?.keyword) searchParams.set('keyword', params.keyword)
  if (params?.category) searchParams.set('category', params.category)
  if (params?.status) searchParams.set('status', params.status)

  const url = `${API_BASE_URL}/quality/reagent/export?${searchParams.toString()}`

  // 使用 fetch 下载文件
  const response = await fetch(url)

  if (!response.ok) {
    throw new Error('导出失败')
  }

  // 获取文件名
  const contentDisposition = response.headers.get('Content-Disposition')
  let filename = `试剂台账_${new Date().toISOString().split('T')[0]}.xlsx`
  if (contentDisposition) {
    const match = contentDisposition.match(/filename\*?=['"]?(?:UTF-8'')?([^;\n"']+)/i)
    if (match) {
      filename = decodeURIComponent(match[1])
    }
  }

  // 创建Blob并下载
  const blob = await response.blob()
  const link = document.createElement('a')
  link.href = URL.createObjectURL(blob)
  link.download = filename
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(link.href)
}