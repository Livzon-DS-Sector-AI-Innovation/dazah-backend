/**
 * 原料检验数据表 Server Actions
 * Version: 3 - Fixed recognizeMultipleImages (renamed to fix cache issue)
 */
'use server'

import { revalidatePath } from 'next/cache'
import type { ColumnConfig, CreateTableRequest, UpdateTableRequest } from '@/types/inspection-table'

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'

async function fetchAPI(endpoint: string, options?: RequestInit) {
  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Request failed' }))
    throw new Error(error.detail || `HTTP ${response.status}`)
  }

  return response.json()
}

// ============ 数据表管理 ============

export async function getInspectionTables(params?: {
  is_active?: boolean
  keyword?: string
  page?: number
  page_size?: number
}) {
  const searchParams = new URLSearchParams()
  if (params?.is_active !== undefined) searchParams.set('is_active', String(params.is_active))
  if (params?.keyword) searchParams.set('keyword', params.keyword)
  if (params?.page) searchParams.set('page', String(params.page))
  if (params?.page_size) searchParams.set('page_size', String(params.page_size))

  return fetchAPI(`/quality/inspection-table?${searchParams.toString()}`)
}

export async function getInspectionTable(id: string) {
  return fetchAPI(`/quality/inspection-table/${id}`)
}

export async function createInspectionTable(data: CreateTableRequest) {
  const response = await fetch(`${API_BASE}/quality/inspection-table`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Create failed' }))
    throw new Error(error.detail || `HTTP ${response.status}`)
  }

  const result = await response.json()
  revalidatePath('/quality/inspection-table')
  return result
}

export async function updateInspectionTable(id: string, data: UpdateTableRequest) {
  const response = await fetch(`${API_BASE}/quality/inspection-table/${id}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Update failed' }))
    throw new Error(error.detail || `HTTP ${response.status}`)
  }

  const result = await response.json()
  revalidatePath('/quality/inspection-table')
  return result
}

export async function deleteInspectionTable(id: string) {
  const result = await fetchAPI(`/quality/inspection-table/${id}`, {
    method: 'DELETE',
  })
  revalidatePath('/quality/inspection-table')
  return result
}

// ============ 数据行管理 ============

export async function addTableRow(tableId: string, rowData: Record<string, any>) {
  const response = await fetch(`${API_BASE}/quality/inspection-table/${tableId}/rows`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ row_data: rowData }),
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Add row failed' }))
    throw new Error(error.detail || `HTTP ${response.status}`)
  }

  return response.json()
}

export async function updateTableRow(tableId: string, rowId: number, rowData: Record<string, any>) {
  const response = await fetch(`${API_BASE}/quality/inspection-table/${tableId}/rows/${rowId}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ row_data: rowData }),
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Update row failed' }))
    throw new Error(error.detail || `HTTP ${response.status}`)
  }

  return response.json()
}

export async function deleteTableRow(tableId: string, rowId: number) {
  const result = await fetchAPI(`/quality/inspection-table/${tableId}/rows/${rowId}`, {
    method: 'DELETE',
  })
  return result
}

export async function batchSaveTableRows(tableId: string, rows: Record<string, any>[]) {
  const response = await fetch(`${API_BASE}/quality/inspection-table/${tableId}/rows/batch`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ rows }),
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Batch save failed' }))
    throw new Error(error.detail || `HTTP ${response.status}`)
  }

  return response.json()
}

// ============ AI 识别 ============

export interface RecognizeResult {
  image_url?: string
  images?: Array<{ original_name: string; saved_path: string }>
  recognized_rows: Record<string, any>[]
  columns_config: Array<{
    key: string
    label: string
    type: string
  }>
}

export async function recognizeImage(tableId: string, file: File): Promise<RecognizeResult> {
  const formData = new FormData()
  formData.append('file', file)

  const response = await fetch(`${API_BASE}/quality/inspection-table/${tableId}/recognize/upload`, {
    method: 'POST',
    body: formData,
  })

  // 先获取响应文本
  const responseText = await response.text()

  if (!response.ok) {
    // 尝试解析错误消息
    try {
      const errorData = JSON.parse(responseText)
      throw new Error(errorData.detail || `HTTP ${response.status}`)
    } catch {
      throw new Error(responseText || `HTTP ${response.status}`)
    }
  }

  const result = JSON.parse(responseText)
  return result.data
}

// 多图片上传识别 v3
export async function recognizeMultipleImagesV3(tableId: string, files: File[]): Promise<RecognizeResult> {
  const formData = new FormData()
  files.forEach((file) => {
    formData.append('files', file)
  })

  const response = await fetch(`${API_BASE}/quality/inspection-table/${tableId}/recognize/multiple`, {
    method: 'POST',
    body: formData,
  })

  // 先获取响应文本
  const responseText = await response.text()

  if (!response.ok) {
    // 尝试解析错误消息
    try {
      const errorData = JSON.parse(responseText)
      throw new Error(errorData.detail || `HTTP ${response.status}`)
    } catch {
      throw new Error(responseText || `HTTP ${response.status}`)
    }
  }

  const result = JSON.parse(responseText)
  return result.data
}
