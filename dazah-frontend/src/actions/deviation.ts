/**
 * 偏差管理 Server Actions
 */
'use server'

import { revalidatePath } from 'next/cache'
import { DeviationCreate, DeviationUpdate, InvestigationCreate, CorrectionCreate, ClosingCreate } from '@/types/deviation'

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

// ============ 偏差列表&发起 ============

export async function getDeviations(params?: {
  status?: string
  deviation_type?: string
  start_date?: string
  end_date?: string
  page?: number
  page_size?: number
}) {
  const searchParams = new URLSearchParams()
  if (params?.status) searchParams.set('status', params.status)
  if (params?.deviation_type) searchParams.set('deviation_type', params.deviation_type)
  if (params?.start_date) searchParams.set('start_date', params.start_date)
  if (params?.end_date) searchParams.set('end_date', params.end_date)
  if (params?.page) searchParams.set('page', String(params.page))
  if (params?.page_size) searchParams.set('page_size', String(params.page_size))
  
  return fetchAPI(`/quality/deviation?${searchParams.toString()}`)
}

export async function getDeviationById(id: string) {
  return fetchAPI(`/quality/deviation/${id}`)
}

export async function createDeviation(data: DeviationCreate) {
  // 转换 dayjs 对象为字符串
  const processedData = {
    ...data,
    occurrence_date: data.occurrence_date && typeof data.occurrence_date === 'object' && 'format' in data.occurrence_date
      ? (data.occurrence_date as { format: (fmt: string) => string }).format('YYYY-MM-DD')
      : data.occurrence_date,
  }
  const result = await fetchAPI('/quality/deviation', {
    method: 'POST',
    body: JSON.stringify(processedData),
  })
  revalidatePath('/quality/deviation')
  return result
}

export async function updateDeviation(id: string, data: DeviationUpdate) {
  // 转换 dayjs 对象为字符串
  const processedData = {
    ...data,
    occurrence_date: data.occurrence_date && typeof data.occurrence_date === 'object' && 'format' in data.occurrence_date
      ? (data.occurrence_date as { format: (fmt: string) => string }).format('YYYY-MM-DD')
      : data.occurrence_date,
  }
  const result = await fetchAPI(`/quality/deviation/${id}`, {
    method: 'PUT',
    body: JSON.stringify(processedData),
  })
  revalidatePath('/quality/deviation')
  return result
}

export async function deleteDeviation(id: string) {
  const result = await fetchAPI(`/quality/deviation/${id}`, {
    method: 'DELETE',
  })
  revalidatePath('/quality/deviation')
  return result
}

export async function submitDeviation(id: string) {
  const result = await fetchAPI(`/quality/deviation/${id}/submit`, {
    method: 'POST',
  })
  revalidatePath('/quality/deviation')
  return result
}

export async function approveDeviation(id: string, data: { approved: boolean; comment?: string }) {
  const result = await fetchAPI(`/quality/deviation/${id}/approve`, {
    method: 'POST',
    body: JSON.stringify(data),
  })
  revalidatePath('/quality/deviation')
  return result
}

export async function lockBatch(id: string, data: { reason: string }) {
  const result = await fetchAPI(`/quality/deviation/${id}/lock-batch`, {
    method: 'POST',
    body: JSON.stringify({ deviation_id: id, ...data }),
  })
  revalidatePath('/quality/deviation')
  return result
}

export async function unlockBatch(id: string) {
  const result = await fetchAPI(`/quality/deviation/${id}/unlock-batch`, {
    method: 'POST',
  })
  revalidatePath('/quality/deviation')
  return result
}

// ============ 偏差调查 ============

export async function getInvestigations(params?: { deviation_id?: string; page?: number; page_size?: number }) {
  const searchParams = new URLSearchParams()
  if (params?.deviation_id) searchParams.set('deviation_id', params.deviation_id)
  if (params?.page) searchParams.set('page', String(params.page))
  if (params?.page_size) searchParams.set('page_size', String(params.page_size))
  
  return fetchAPI(`/quality/deviation/investigations/list?${searchParams.toString()}`)
}

export async function createInvestigation(data: InvestigationCreate) {
  const result = await fetchAPI('/quality/deviation/investigations', {
    method: 'POST',
    body: JSON.stringify(data),
  })
  revalidatePath('/quality/deviation')
  return result
}

export async function updateInvestigation(id: string, data: Partial<InvestigationCreate>) {
  const result = await fetchAPI(`/quality/deviation/investigations/${id}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  })
  revalidatePath('/quality/deviation')
  return result
}

// ============ 偏差整改 ============

export async function getCorrections(params?: { deviation_id?: string; status?: string; page?: number; page_size?: number }) {
  const searchParams = new URLSearchParams()
  if (params?.deviation_id) searchParams.set('deviation_id', params.deviation_id)
  if (params?.status) searchParams.set('status', params.status)
  if (params?.page) searchParams.set('page', String(params.page))
  if (params?.page_size) searchParams.set('page_size', String(params.page_size))
  
  return fetchAPI(`/quality/deviation/corrections/list?${searchParams.toString()}`)
}

export async function createCorrection(data: CorrectionCreate) {
  const result = await fetchAPI('/quality/deviation/corrections', {
    method: 'POST',
    body: JSON.stringify(data),
  })
  revalidatePath('/quality/deviation')
  return result
}

export async function updateCorrection(id: string, data: Partial<CorrectionCreate>) {
  const result = await fetchAPI(`/quality/deviation/corrections/${id}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  })
  revalidatePath('/quality/deviation')
  return result
}

// ============ 偏差关闭 ============

export async function getClosings(params?: { deviation_id?: string; page?: number; page_size?: number }) {
  const searchParams = new URLSearchParams()
  if (params?.deviation_id) searchParams.set('deviation_id', params.deviation_id)
  if (params?.page) searchParams.set('page', String(params.page))
  if (params?.page_size) searchParams.set('page_size', String(params.page_size))
  
  return fetchAPI(`/quality/deviation/closings/list?${searchParams.toString()}`)
}

export async function createClosing(data: ClosingCreate) {
  const result = await fetchAPI('/quality/deviation/closings', {
    method: 'POST',
    body: JSON.stringify(data),
  })
  revalidatePath('/quality/deviation')
  return result
}

export async function updateClosing(id: string, data: Partial<ClosingCreate>) {
  const result = await fetchAPI(`/quality/deviation/closings/${id}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  })
  revalidatePath('/quality/deviation')
  return result
}

// ============ 统计 ============

export async function getDeviationStatistics() {
  return fetchAPI('/quality/deviation/statistics')
}

// ============ AI辅助功能 ============

export async function aiGenerateDescription(params: {
  deviation_type?: string
  deviation_level?: string
  occurrence_date?: string
  discovering_department?: string
  product_name?: string
  production_batch?: string
  keywords: string
}) {
  const searchParams = new URLSearchParams()
  if (params.deviation_type) searchParams.set('deviation_type', params.deviation_type)
  if (params.deviation_level) searchParams.set('deviation_level', params.deviation_level)
  if (params.occurrence_date) searchParams.set('occurrence_date', params.occurrence_date)
  if (params.discovering_department) searchParams.set('discovering_department', params.discovering_department)
  if (params.product_name) searchParams.set('product_name', params.product_name)
  if (params.production_batch) searchParams.set('production_batch', params.production_batch)
  searchParams.set('keywords', params.keywords)

  return fetchAPI(`/quality/deviation/ai/generate-description?${searchParams.toString()}`, {
    method: 'POST',
  })
}

export async function aiAnalyzeImpact(params: {
  deviation_type?: string
  deviation_level?: string
  occurrence_date?: string
  discovering_department?: string
  product_name?: string
  production_batch?: string
  description?: string
}) {
  const searchParams = new URLSearchParams()
  if (params.deviation_type) searchParams.set('deviation_type', params.deviation_type)
  if (params.deviation_level) searchParams.set('deviation_level', params.deviation_level)
  if (params.occurrence_date) searchParams.set('occurrence_date', params.occurrence_date)
  if (params.discovering_department) searchParams.set('discovering_department', params.discovering_department)
  if (params.product_name) searchParams.set('product_name', params.product_name)
  if (params.production_batch) searchParams.set('production_batch', params.production_batch)
  if (params.description) searchParams.set('description', params.description)

  return fetchAPI(`/quality/deviation/ai/analyze-impact?${searchParams.toString()}`, {
    method: 'POST',
  })
}

export async function aiAnalyzeDirectCause(params: {
  deviation_type: string
  description?: string
  product_name?: string
  production_batch?: string
}) {
  const searchParams = new URLSearchParams()
  searchParams.set('deviation_type', params.deviation_type)
  if (params.description) searchParams.set('description', params.description)
  if (params.product_name) searchParams.set('product_name', params.product_name)
  if (params.production_batch) searchParams.set('production_batch', params.production_batch)

  return fetchAPI(`/quality/deviation/ai/analyze-direct-cause?${searchParams.toString()}`, {
    method: 'POST',
  })
}

export async function aiGenerateEmergencyMeasures(params: {
  deviation_type?: string
  deviation_level?: string
  occurrence_date?: string
  discovering_department?: string
  product_name?: string
  production_batch?: string
  description?: string
}) {
  const searchParams = new URLSearchParams()
  if (params.deviation_type) searchParams.set('deviation_type', params.deviation_type)
  if (params.deviation_level) searchParams.set('deviation_level', params.deviation_level)
  if (params.occurrence_date) searchParams.set('occurrence_date', params.occurrence_date)
  if (params.discovering_department) searchParams.set('discovering_department', params.discovering_department)
  if (params.product_name) searchParams.set('product_name', params.product_name)
  if (params.production_batch) searchParams.set('production_batch', params.production_batch)
  if (params.description) searchParams.set('description', params.description)

  return fetchAPI(`/quality/deviation/ai/generate-emergency-measures?${searchParams.toString()}`, {
    method: 'POST',
  })
}

export async function aiAnalyzeRootCause(params: {
  deviation_type: string
  description?: string
  direct_cause?: string
  root_cause?: string
  investigation_data?: string
}) {
  const searchParams = new URLSearchParams()
  searchParams.set('deviation_type', params.deviation_type)
  if (params.description) searchParams.set('description', params.description)
  if (params.direct_cause) searchParams.set('direct_cause', params.direct_cause)
  if (params.investigation_data) searchParams.set('investigation_data', params.investigation_data)

  return fetchAPI(`/quality/deviation/ai/analyze-root-cause?${searchParams.toString()}`, {
    method: 'POST',
  })
}

export async function aiGenerateCAPA(params: {
  deviation_type: string
  root_cause?: string
  deviation_level?: string
  department?: string
}) {
  const searchParams = new URLSearchParams()
  searchParams.set('deviation_type', params.deviation_type)
  if (params.root_cause) searchParams.set('root_cause', params.root_cause)
  if (params.deviation_level) searchParams.set('deviation_level', params.deviation_level)
  if (params.department) searchParams.set('department', params.department)

  return fetchAPI(`/quality/deviation/ai/generate-capa?${searchParams.toString()}`, {
    method: 'POST',
  })
}

export async function aiGeneratePrevention(params: {
  deviation_type: string
  root_cause?: string
  deviation_level?: string
  department?: string
}) {
  const searchParams = new URLSearchParams()
  searchParams.set('deviation_type', params.deviation_type)
  if (params.root_cause) searchParams.set('root_cause', params.root_cause)
  if (params.deviation_level) searchParams.set('deviation_level', params.deviation_level)
  if (params.department) searchParams.set('department', params.department)

  return fetchAPI(`/quality/deviation/ai/generate-prevention?${searchParams.toString()}`, {
    method: 'POST',
  })
}