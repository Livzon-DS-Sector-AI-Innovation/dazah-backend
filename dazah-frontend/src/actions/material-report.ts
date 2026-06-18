/**
 * 原料报告单 Server Actions
 */
'use server'

import { revalidatePath } from 'next/cache'
import {
  ReportCreate,
  ReportUpdate,
  ReportItemsBatchSave,
  TemplateCreate,
  TemplateUpdate,
} from '@/types/material-report'

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

// ============ 报告单 Actions ============

export async function getReports(params?: {
  template_id?: string
  status?: string
  start_date?: string
  end_date?: string
  keyword?: string
  page?: number
  page_size?: number
}) {
  const searchParams = new URLSearchParams()
  if (params?.template_id) searchParams.set('template_id', params.template_id)
  if (params?.status) searchParams.set('status', params.status)
  if (params?.start_date) searchParams.set('start_date', params.start_date)
  if (params?.end_date) searchParams.set('end_date', params.end_date)
  if (params?.keyword) searchParams.set('keyword', params.keyword)
  if (params?.page) searchParams.set('page', String(params.page))
  if (params?.page_size) searchParams.set('page_size', String(params.page_size))

  return fetchAPI(`/quality/material-report?${searchParams.toString()}`)
}

export async function getReportById(id: string) {
  return fetchAPI(`/quality/material-report/${id}`)
}

export async function createReport(data: ReportCreate) {
  const processedData = {
    ...data,
    report_date: typeof data.report_date === 'object' && 'format' in data.report_date
      ? (data.report_date as { format: (fmt: string) => string }).format('YYYY-MM-DD')
      : data.report_date,
  }
  const result = await fetchAPI('/quality/material-report', {
    method: 'POST',
    body: JSON.stringify(processedData),
  })
  revalidatePath('/quality/material-report')
  return result
}

export async function updateReport(id: string, data: ReportUpdate) {
  const processedData = {
    ...data,
    report_date: data.report_date && typeof data.report_date === 'object' && 'format' in data.report_date
      ? (data.report_date as { format: (fmt: string) => string }).format('YYYY-MM-DD')
      : data.report_date,
  }
  const result = await fetchAPI(`/quality/material-report/${id}`, {
    method: 'PUT',
    body: JSON.stringify(processedData),
  })
  revalidatePath('/quality/material-report')
  return result
}

export async function deleteReport(id: string) {
  const result = await fetchAPI(`/quality/material-report/${id}`, {
    method: 'DELETE',
  })
  revalidatePath('/quality/material-report')
  return result
}

export async function saveReportItems(id: string, data: ReportItemsBatchSave) {
  const result = await fetchAPI(`/quality/material-report/${id}/items`, {
    method: 'POST',
    body: JSON.stringify(data),
  })
  revalidatePath('/quality/material-report')
  return result
}

export async function generateReport(id: string) {
  const response = await fetch(`${API_BASE}/quality/material-report/${id}/generate`, {
    method: 'POST',
  })

  if (!response.ok) {
    throw new Error(`生成报告失败: ${response.status}`)
  }

  // 返回 blob 数据
  return response.blob()
}

export async function submitReport(id: string) {
  const result = await fetchAPI(`/quality/material-report/${id}/submit`, {
    method: 'POST',
  })
  revalidatePath('/quality/material-report')
  return result
}

export async function getReportStatistics() {
  return fetchAPI('/quality/material-report/statistics')
}

// ============ 模板管理 Actions ============

export async function getTemplates(params?: {
  is_active?: boolean
  page?: number
  page_size?: number
}) {
  const searchParams = new URLSearchParams()
  if (params?.is_active !== undefined) searchParams.set('is_active', String(params.is_active))
  if (params?.page) searchParams.set('page', String(params.page))
  if (params?.page_size) searchParams.set('page_size', String(params.page_size))

  return fetchAPI(`/quality/material-report/template?${searchParams.toString()}`)
}

export async function getTemplateById(id: string) {
  return fetchAPI(`/quality/material-report/template/${id}`)
}

export async function uploadTemplate(
  file: File,
  templateName: string,
  templateDescription?: string,
  fieldMapping?: Record<string, any>,
  tableFields?: Record<string, any>
) {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('template_name', templateName)
  if (templateDescription) {
    formData.append('template_description', templateDescription)
  }
  if (fieldMapping) {
    formData.append('field_mapping', JSON.stringify(fieldMapping))
  }
  if (tableFields) {
    formData.append('table_fields', JSON.stringify(tableFields))
  }

  const response = await fetch(`${API_BASE}/quality/material-report/template`, {
    method: 'POST',
    body: formData,
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Upload failed' }))
    throw new Error(error.detail || `HTTP ${response.status}`)
  }

  const result = await response.json()
  revalidatePath('/quality/material-report')
  return result
}

export async function updateTemplate(id: string, data: TemplateUpdate) {
  const result = await fetchAPI(`/quality/material-report/template/${id}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  })
  revalidatePath('/quality/material-report')
  return result
}

export async function deleteTemplate(id: string) {
  const result = await fetchAPI(`/quality/material-report/template/${id}`, {
    method: 'DELETE',
  })
  revalidatePath('/quality/material-report')
  return result
}

export async function previewTemplate(id: string) {
  return fetchAPI(`/quality/material-report/template/${id}/preview`)
}

// ============ 图片上传与AI识别 Actions ============

export async function uploadReportImage(
  reportId: string,
  file: File,
  fieldKey?: string,
  rowIndex?: number
) {
  const formData = new FormData()
  formData.append('file', file)
  if (fieldKey) {
    formData.append('field_key', fieldKey)
  }
  if (rowIndex !== undefined) {
    formData.append('row_index', String(rowIndex))
  }

  const response = await fetch(`${API_BASE}/quality/material-report/${reportId}/images`, {
    method: 'POST',
    body: formData,
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Upload failed' }))
    throw new Error(error.detail || `HTTP ${response.status}`)
  }

  return response.json()
}

export async function getReportImages(reportId: string) {
  return fetchAPI(`/quality/material-report/${reportId}/images`)
}