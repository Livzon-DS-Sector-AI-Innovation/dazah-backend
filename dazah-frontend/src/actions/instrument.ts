'use server'

import { revalidatePath } from 'next/cache'
import type {
  Instrument,
  InstrumentListItem,
  InstrumentListResponse,
  InstrumentCreate,
  InstrumentUpdate,
  InstrumentFilter,
  CalibrationRule,
  CalibrationRuleCreate,
  CalibrationRuleUpdate,
  CalibrationRecord,
  CalibrationRecordListItem,
  CalibrationRecordListResponse,
  CalibrationRecordCreate,
  CalibrationRecordUpdate,
  CalibrationRecordFilter,
  ApprovalRecord,
  ApprovalCreate,
} from '@/types/instrument'

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'

// ============ Helper Functions ============

async function fetchApi<T>(
  endpoint: string,
  options?: RequestInit
): Promise<T> {
  const response = await fetch(`${API_BASE}${endpoint}`, {
    headers: {
      'Content-Type': 'application/json',
    },
    ...options,
  })
  const data = await response.json()
  // 统一处理响应格式：如果返回的是 {code, message, data} 格式，则提取 data
  if (data && typeof data === 'object' && 'code' in data && 'data' in data) {
    if (data.code >= 400) {
      throw new Error(data.message || '请求失败')
    }
    return data.data as T
  }
  return data as T
}

// ============ Instrument Actions (仪器设备台账) ============

export async function getInstruments(params: InstrumentFilter = {}) {
  const searchParams = new URLSearchParams()
  if (params.page) searchParams.set('page', String(params.page))
  if (params.page_size) searchParams.set('page_size', String(params.page_size))
  if (params.instrument_no) searchParams.set('instrument_no', params.instrument_no)
  if (params.instrument_name) searchParams.set('instrument_name', params.instrument_name)
  if (params.category) searchParams.set('category', params.category)
  if (params.is_active !== undefined) searchParams.set('is_active', String(params.is_active))
  if (params.status) searchParams.set('status', params.status)
  if (params.is_overdue !== undefined) searchParams.set('is_overdue', String(params.is_overdue))

  const queryString = searchParams.toString()
  const endpoint = `/quality/instrument${queryString ? `?${queryString}` : ''}`
  return fetchApi<InstrumentListResponse>(endpoint)
}

export async function getInstrument(id: string) {
  return fetchApi<Instrument>(`/quality/instrument/${id}`)
}

export async function createInstrument(data: InstrumentCreate) {
  const response = await fetchApi<Instrument>('/quality/instrument', {
    method: 'POST',
    body: JSON.stringify(data),
  })
  revalidatePath('/quality/instrument')
  return response
}

export async function updateInstrument(id: string, data: InstrumentUpdate) {
  const response = await fetchApi<Instrument>(`/quality/instrument/${id}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  })
  revalidatePath('/quality/instrument')
  return response
}

export async function deleteInstrument(id: string) {
  const response = await fetchApi<null>(`/quality/instrument/${id}`, {
    method: 'DELETE',
  })
  revalidatePath('/quality/instrument')
  return response
}

export async function submitInstrument(id: string) {
  const response = await fetchApi<Instrument>(`/quality/instrument/${id}/submit`, {
    method: 'POST',
  })
  revalidatePath('/quality/instrument')
  return response
}

export async function approveInstrumentByAdmin(id: string) {
  const response = await fetchApi<Instrument>(`/quality/instrument/${id}/approve?approved=true&approval_type=admin`, {
    method: 'POST',
  })
  revalidatePath('/quality/instrument')
  return response
}

export async function approveInstrumentByQA(id: string) {
  const response = await fetchApi<Instrument>(`/quality/instrument/${id}/approve?approved=true&approval_type=qa`, {
    method: 'POST',
  })
  revalidatePath('/quality/instrument')
  return response
}

export async function rejectInstrument(id: string, comments: string) {
  const response = await fetchApi<Instrument>(
    `/quality/instrument/${id}/approve?approved=false&comments=${encodeURIComponent(comments)}&approval_type=admin`,
    { method: 'POST' }
  )
  revalidatePath('/quality/instrument')
  return response
}

export async function deactivateInstrument(id: string, reason: string) {
  const response = await fetchApi<Instrument>(
    `/quality/instrument/${id}/deactivate?reason=${encodeURIComponent(reason)}`,
    { method: 'POST' }
  )
  revalidatePath('/quality/instrument')
  return response
}

export async function getOverdueInstruments() {
  return fetchApi<InstrumentListItem[]>('/quality/instrument/overdue')
}

export async function getUpcomingCalibrations(days: number = 30) {
  return fetchApi<InstrumentListItem[]>(`/quality/instrument/upcoming?days=${days}`)
}

// ============ CalibrationRule Actions (校准规则配置) ============

export async function getCalibrationRules(instrumentId?: string) {
  const endpoint = instrumentId
    ? `/quality/instrument/rules?instrument_id=${instrumentId}`
    : '/quality/instrument/rules'
  return fetchApi<CalibrationRule[]>(endpoint)
}

export async function getCalibrationRule(id: string) {
  return fetchApi<CalibrationRule>(`/quality/instrument/rules/${id}`)
}

export async function createCalibrationRule(data: CalibrationRuleCreate) {
  const response = await fetchApi<CalibrationRule>('/quality/instrument/rules', {
    method: 'POST',
    body: JSON.stringify(data),
  })
  revalidatePath('/quality/instrument')
  return response
}

export async function updateCalibrationRule(id: string, data: CalibrationRuleUpdate) {
  const response = await fetchApi<CalibrationRule>(`/quality/instrument/rules/${id}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  })
  revalidatePath('/quality/instrument')
  return response
}

export async function deleteCalibrationRule(id: string) {
  const response = await fetchApi<null>(`/quality/instrument/rules/${id}`, {
    method: 'DELETE',
  })
  revalidatePath('/quality/instrument')
  return response
}

// ============ CalibrationRecord Actions (校准记录) ============

export async function getCalibrationRecords(params: CalibrationRecordFilter = {}) {
  const searchParams = new URLSearchParams()
  if (params.page) searchParams.set('page', String(params.page))
  if (params.page_size) searchParams.set('page_size', String(params.page_size))
  if (params.instrument_id) searchParams.set('instrument_id', params.instrument_id)
  if (params.calibration_no) searchParams.set('calibration_no', params.calibration_no)
  if (params.calibration_result) searchParams.set('calibration_result', params.calibration_result)
  if (params.status) searchParams.set('status', params.status)
  if (params.calibration_method) searchParams.set('calibration_method', params.calibration_method)
  if (params.start_date) searchParams.set('start_date', params.start_date)
  if (params.end_date) searchParams.set('end_date', params.end_date)

  const queryString = searchParams.toString()
  const endpoint = `/quality/instrument/records${queryString ? `?${queryString}` : ''}`
  return fetchApi<CalibrationRecordListResponse>(endpoint)
}

export async function getCalibrationRecord(id: string) {
  return fetchApi<CalibrationRecord>(`/quality/instrument/records/${id}`)
}

export async function createCalibrationRecord(data: CalibrationRecordCreate) {
  const response = await fetchApi<CalibrationRecord>('/quality/instrument/records', {
    method: 'POST',
    body: JSON.stringify(data),
  })
  revalidatePath('/quality/instrument')
  return response
}

export async function updateCalibrationRecord(id: string, data: CalibrationRecordUpdate) {
  const response = await fetchApi<CalibrationRecord>(`/quality/instrument/records/${id}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  })
  revalidatePath('/quality/instrument')
  return response
}

export async function deleteCalibrationRecord(id: string) {
  const response = await fetchApi<null>(`/quality/instrument/records/${id}`, {
    method: 'DELETE',
  })
  revalidatePath('/quality/instrument')
  return response
}

export async function submitCalibrationRecord(id: string) {
  const response = await fetchApi<CalibrationRecord>(`/quality/instrument/records/${id}/submit`, {
    method: 'POST',
  })
  revalidatePath('/quality/instrument')
  return response
}

export async function approveCalibrationRecordByAdmin(id: string) {
  const response = await fetchApi<CalibrationRecord>(`/quality/instrument/records/${id}/approve?approved=true&approval_type=admin`, {
    method: 'POST',
  })
  revalidatePath('/quality/instrument')
  return response
}

export async function approveCalibrationRecordByQA(id: string) {
  const response = await fetchApi<CalibrationRecord>(`/quality/instrument/records/${id}/approve?approved=true&approval_type=qa`, {
    method: 'POST',
  })
  revalidatePath('/quality/instrument')
  return response
}

export async function rejectCalibrationRecord(id: string, comments: string) {
  const response = await fetchApi<CalibrationRecord>(
    `/quality/instrument/records/${id}/approve?approved=false&comments=${encodeURIComponent(comments)}&approval_type=admin`,
    { method: 'POST' }
  )
  revalidatePath('/quality/instrument')
  return response
}

// ============ Approval Actions (审批记录) ============

export async function getInstrumentApprovals(instrumentId: string) {
  return fetchApi<ApprovalRecord[]>(`/quality/instrument/${instrumentId}/approvals`)
}

export async function getCalibrationRecordApprovals(recordId: string) {
  return fetchApi<ApprovalRecord[]>(`/quality/instrument/records/${recordId}/approvals`)
}

export async function approveInstrument(id: string, data: ApprovalCreate) {
  const response = await fetchApi<ApprovalRecord>(`/quality/instrument/${id}/approve`, {
    method: 'POST',
    body: JSON.stringify(data),
  })
  revalidatePath('/quality/instrument')
  return response
}

export async function approveCalibrationRecord(id: string, data: ApprovalCreate) {
  const response = await fetchApi<ApprovalRecord>(`/quality/instrument/records/${id}/approve`, {
    method: 'POST',
    body: JSON.stringify(data),
  })
  revalidatePath('/quality/instrument')
  return response
}
