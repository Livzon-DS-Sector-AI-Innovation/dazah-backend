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
  if (params.rule_id) searchParams.set('rule_id', params.rule_id)
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

// ============ AI 识别 API ============

export interface AIRecognizedInstrumentInfo {
  instrument_name: string
  model: string
  serial_no: string
  manufacturer: string
  last_calibration_date: string
  next_calibration_date: string
  calibration_agency: string
  raw_result?: string
}

export async function recognizeInstrumentLabel(file: File): Promise<AIRecognizedInstrumentInfo> {
  const formData = new FormData()
  formData.append('file', file)

  const response = await fetch(`${API_BASE}/quality/instrument/recognize`, {
    method: 'POST',
    body: formData,
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: '识别失败' }))
    throw new Error(error.detail || '识别失败')
  }

  const result = await response.json()
  // 统一处理响应格式
  if (result && typeof result === 'object' && 'data' in result) {
    return result.data as AIRecognizedInstrumentInfo
  }
  return result as AIRecognizedInstrumentInfo
}

// ============ 到期提醒 API ============

export interface UpcomingCalibrationRecord {
  id: string
  calibration_no: string
  instrument_id: string | null
  instrument_no: string | null
  instrument_name: string | null
  calibration_date: string | null
  valid_until: string | null
  calibration_result: string
  days_until_expiry: number | null
}

export interface UpcomingCalibrationResponse {
  items: UpcomingCalibrationRecord[]
  total: number
  days: number
}

export interface ReminderResponse {
  sent: boolean
  count: number
  chat_id: string
  receive_id_type: string
}

export async function getUpcomingCalibrationRecords(days: number = 30): Promise<UpcomingCalibrationResponse> {
  return fetchApi<UpcomingCalibrationResponse>(`/quality/instrument/record/upcoming?days=${days}`)
}

export interface RecordsForReminderResponse {
  overdue: Array<{
    id: string
    instrument_id: string | null
    instrument_name: string | null
    instrument_no: string | null
    valid_until: string | null
    days_until_expiry: number
  }>
  upcoming: Array<{
    id: string
    instrument_id: string | null
    instrument_name: string | null
    instrument_no: string | null
    valid_until: string | null
    days_until_expiry: number
  }>
  total_overdue: number
  total_upcoming: number
}

export async function getRecordsForReminder(days: number = 30): Promise<RecordsForReminderResponse> {
  return fetchApi<RecordsForReminderResponse>(`/quality/instrument/record/for-reminder?days=${days}`)
}

export async function sendCalibrationReminder(
  chatId: string,
  receiveIdType: 'chat_id' | 'open_id' = 'chat_id',
  days: number = 30,
  feishuAppId?: string,
  feishuAppSecret?: string
): Promise<ReminderResponse> {
  const params = new URLSearchParams({
    chat_id: chatId,
    receive_id_type: receiveIdType,
    days: String(days),
  })
  if (feishuAppId) params.set('feishu_app_id', feishuAppId)
  if (feishuAppSecret) params.set('feishu_app_secret', feishuAppSecret)

  const response = await fetch(`${API_BASE}/quality/instrument/record/remind?${params}`, {
    method: 'POST',
  })
  if (!response.ok) {
    const text = await response.text()
    try {
      const errData = JSON.parse(text)
      throw new Error(errData.detail || errData.message || `发送失败 (${response.status})`)
    } catch {
      throw new Error(text || `发送失败 (${response.status})`)
    }
  }
  const data = await response.json()
  // 统一处理响应格式
  if (data && typeof data === 'object' && 'data' in data) {
    if (data.code >= 400) {
      throw new Error(data.message || '发送失败')
    }
    return data.data as ReminderResponse
  }
  return data as ReminderResponse
}

// ============ 提醒配置管理 API ============

export interface ReminderConfig {
  id: string
  name: string
  feishu_app_id: string | null
  feishu_app_secret: string | null
  chat_id: string | null
  receive_id_type: string
  remind_30_days: boolean
  remind_14_days: boolean
  remind_7_days: boolean
  remind_overdue: boolean
  is_active: boolean
  last_remind_30_days: string | null
  last_remind_14_days: string | null
  last_remind_7_days: string | null
  last_remind_overdue: string | null
  created_at: string
  updated_at: string
}

export interface ReminderConfigListResponse {
  items: ReminderConfig[]
  total: number
}

export interface ReminderConfigCreate {
  name: string
  feishu_app_id?: string
  feishu_app_secret?: string
  chat_id?: string
  receive_id_type?: string
  remind_30_days?: boolean
  remind_14_days?: boolean
  remind_7_days?: boolean
  remind_overdue?: boolean
  is_active?: boolean
}

export interface ReminderConfigUpdate {
  name?: string
  feishu_app_id?: string
  feishu_app_secret?: string
  chat_id?: string
  receive_id_type?: string
  remind_30_days?: boolean
  remind_14_days?: boolean
  remind_7_days?: boolean
  remind_overdue?: boolean
  is_active?: boolean
}

export async function getReminderConfigs(): Promise<ReminderConfigListResponse> {
  return fetchApi<ReminderConfigListResponse>('/quality/instrument/reminder-config')
}

export async function createReminderConfig(data: ReminderConfigCreate): Promise<ReminderConfig> {
  const response = await fetch(`${API_BASE}/quality/instrument/reminder-config`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  })
  const result = await response.json()
  if (result && typeof result === 'object' && 'data' in result) {
    if (result.code >= 400) throw new Error(result.message || '创建失败')
    return result.data as ReminderConfig
  }
  return result as ReminderConfig
}

export async function updateReminderConfig(id: string, data: ReminderConfigUpdate): Promise<ReminderConfig> {
  const response = await fetch(`${API_BASE}/quality/instrument/reminder-config/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  })
  const result = await response.json()
  if (result && typeof result === 'object' && 'data' in result) {
    if (result.code >= 400) throw new Error(result.message || '更新失败')
    return result.data as ReminderConfig
  }
  return result as ReminderConfig
}

export async function deleteReminderConfig(id: string): Promise<void> {
  const response = await fetch(`${API_BASE}/quality/instrument/reminder-config/${id}`, {
    method: 'DELETE',
  })
  const result = await response.json()
  if (result && typeof result === 'object' && 'code' in result && result.code >= 400) {
    throw new Error(result.message || '删除失败')
  }
}

export interface AutoTriggerResponse {
  results: Array<{
    config_name: string
    sent: string[]
    errors: string[]
  }>
}

export async function autoTriggerReminders(): Promise<AutoTriggerResponse> {
  const response = await fetch(`${API_BASE}/quality/instrument/reminder/auto-trigger`, {
    method: 'POST',
  })
  const result = await response.json()
  if (result && typeof result === 'object' && 'data' in result) {
    return result.data as AutoTriggerResponse
  }
  return result as AutoTriggerResponse
}

// ========== 飞书通讯录 API ==========

export interface FeishuUser {
  open_id: string
  name: string
  en_name?: string
  email?: string
  mobile?: string
  avatar?: string
  department_ids?: string[]
}

export interface FeishuDepartment {
  open_department_id: string
  name: string
  parent_department_id: string
}

export async function resolveFeishuUser(mobile?: string, email?: string): Promise<string | null> {
  const response = await fetch(`${API_BASE}/quality/instrument/feishu-contacts/resolve-user`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ mobile, email }),
  })
  const result = await response.json()
  if (result && typeof result === 'object' && 'data' in result) {
    return result.data.open_id as string | null
  }
  return null
}

export async function getFeishuContactUsers(departmentId: string = '0'): Promise<FeishuUser[]> {
  const response = await fetch(`${API_BASE}/quality/instrument/feishu-contacts/users?department_id=${encodeURIComponent(departmentId)}`)
  const result = await response.json()
  if (result && typeof result === 'object' && 'data' in result) {
    return result.data.users as FeishuUser[]
  }
  return []
}

export async function getFeishuContactDepartments(parentDepartmentId: string = '0'): Promise<FeishuDepartment[]> {
  const response = await fetch(`${API_BASE}/quality/instrument/feishu-contacts/departments?parent_department_id=${encodeURIComponent(parentDepartmentId)}`)
  const result = await response.json()
  if (result && typeof result === 'object' && 'data' in result) {
    return result.data.departments as FeishuDepartment[]
  }
  return []
}
