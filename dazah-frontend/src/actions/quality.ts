'use server'

import { revalidatePath } from 'next/cache'
import type {
  InspectionStandard,
  InspectionStandardItem,
  InspectionStandardFormData,
  InspectionStandardItemFormData,
  StandardCopyData,
  ObsoleteData,
  ApprovalRecord,
  StandardQueryParams,
  ApiResponse,
} from '@/types/quality'

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'

// ============ Helper Functions ============

async function fetchApi<T>(
  endpoint: string,
  options?: RequestInit
): Promise<ApiResponse<T>> {
  const response = await fetch(`${API_BASE}${endpoint}`, {
    headers: {
      'Content-Type': 'application/json',
    },
    ...options,
  })
  return response.json()
}

// ============ InspectionStandard Actions ============

export async function getStandards(params: StandardQueryParams = {}) {
  const searchParams = new URLSearchParams()
  if (params.page) searchParams.set('page', String(params.page))
  if (params.page_size) searchParams.set('page_size', String(params.page_size))
  if (params.status) searchParams.set('status', params.status)
  if (params.material_code) searchParams.set('material_code', params.material_code)
  if (params.material_name) searchParams.set('material_name', params.material_name)
  if (params.material_category) searchParams.set('material_category', params.material_category)
  if (params.pharmacopeia) searchParams.set('pharmacopeia', params.pharmacopeia)
  if (params.version) searchParams.set('version', params.version)
  if (params.is_effective !== undefined) searchParams.set('is_effective', String(params.is_effective))

  const queryString = searchParams.toString()
  const endpoint = `/quality/standards${queryString ? `?${queryString}` : ''}`
  return fetchApi<InspectionStandard[]>(endpoint)
}

export async function getEffectiveStandards(params: { material_code?: string; material_category?: string } = {}) {
  const searchParams = new URLSearchParams()
  if (params.material_code) searchParams.set('material_code', params.material_code)
  if (params.material_category) searchParams.set('material_category', params.material_category)

  const queryString = searchParams.toString()
  const endpoint = `/quality/standards/effective${queryString ? `?${queryString}` : ''}`
  return fetchApi<InspectionStandard[]>(endpoint)
}

export async function getStandard(id: string) {
  return fetchApi<InspectionStandard>(`/quality/standards/${id}`)
}

export async function createStandard(data: InspectionStandardFormData) {
  const response = await fetchApi<InspectionStandard>('/quality/standards', {
    method: 'POST',
    body: JSON.stringify(data),
  })
  revalidatePath('/quality/inspection')
  return response
}

export async function updateStandard(id: string, data: Partial<InspectionStandardFormData>) {
  const response = await fetchApi<InspectionStandard>(`/quality/standards/${id}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  })
  revalidatePath('/quality/inspection')
  return response
}

export async function deleteStandard(id: string) {
  const response = await fetchApi<null>(`/quality/standards/${id}`, {
    method: 'DELETE',
  })
  revalidatePath('/quality/inspection')
  return response
}

export async function submitStandardForApproval(id: string) {
  const response = await fetchApi<InspectionStandard>(`/quality/standards/${id}/submit`, {
    method: 'POST',
  })
  revalidatePath('/quality/inspection')
  return response
}

export async function approveStandard(id: string) {
  const response = await fetchApi<InspectionStandard>(`/quality/standards/${id}/approve`, {
    method: 'POST',
  })
  revalidatePath('/quality/inspection')
  return response
}

export async function rejectStandard(id: string, comments: string) {
  const response = await fetchApi<InspectionStandard>(
    `/quality/standards/${id}/reject?comments=${encodeURIComponent(comments)}`,
    { method: 'POST' }
  )
  revalidatePath('/quality/inspection')
  return response
}

export async function obsoleteStandard(id: string, data: ObsoleteData) {
  const response = await fetchApi<InspectionStandard>(`/quality/standards/${id}/obsolete`, {
    method: 'POST',
    body: JSON.stringify(data),
  })
  revalidatePath('/quality/inspection')
  return response
}

export async function copyStandard(data: StandardCopyData) {
  const response = await fetchApi<InspectionStandard>('/quality/standards/copy', {
    method: 'POST',
    body: JSON.stringify(data),
  })
  revalidatePath('/quality/inspection')
  return response
}

// ============ InspectionStandardItem Actions ============

export async function getStandardItems(standardId: string) {
  return fetchApi<InspectionStandardItem[]>(`/quality/standards/${standardId}/items`)
}

// ============ ApprovalRecord Actions ============

export async function getApprovalRecords(standardId: string) {
  return fetchApi<ApprovalRecord[]>(`/quality/standards/${standardId}/approvals`)
}

// ============ Sampling Order Actions (取样管理) ============

import type {
  SamplingOrder,
  SamplingOrderCreate,
  SamplingOrderUpdate,
  SamplingOrderListItem,
  SamplingOrderListResponse,
  SamplingOrderFilter,
  SamplingOrderItemCreate,
  SamplingApprovalRecord,
  SamplingApprovalCreate,
  SampleRetentionLedger,
  RetentionLedgerListResponse,
  RetentionLedgerFilter,
} from '@/types/sampling'

export async function getSamplingOrders(params: SamplingOrderFilter & { page?: number; page_size?: number } = {}) {
  const searchParams = new URLSearchParams()
  if (params.page) searchParams.set('page', String(params.page))
  if (params.page_size) searchParams.set('page_size', String(params.page_size))
  if (params.order_no) searchParams.set('order_no', params.order_no)
  if (params.material_code) searchParams.set('material_code', params.material_code)
  if (params.material_name) searchParams.set('material_name', params.material_name)
  if (params.sampling_source) searchParams.set('sampling_source', params.sampling_source)
  if (params.status) searchParams.set('status', params.status)
  if (params.sampling_result) searchParams.set('sampling_result', params.sampling_result)
  if (params.start_date) searchParams.set('start_date', params.start_date)
  if (params.end_date) searchParams.set('end_date', params.end_date)

  const queryString = searchParams.toString()
  const endpoint = `/quality/sampling/orders${queryString ? `?${queryString}` : ''}`
  const response = await fetch(`${API_BASE}${endpoint}`)
  const data = await response.json()
  return data as ApiResponse<SamplingOrderListResponse>
}

export async function getSamplingOrder(id: string) {
  return fetchApi<SamplingOrder>(`/quality/sampling/orders/${id}`)
}

export async function createSamplingOrder(data: SamplingOrderCreate) {
  const response = await fetchApi<SamplingOrder>('/quality/sampling/orders', {
    method: 'POST',
    body: JSON.stringify(data),
  })
  revalidatePath('/quality/sampling')
  return response
}

export async function updateSamplingOrder(id: string, data: SamplingOrderUpdate) {
  const response = await fetchApi<SamplingOrder>(`/quality/sampling/orders/${id}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  })
  revalidatePath('/quality/sampling')
  return response
}

export async function deleteSamplingOrder(id: string) {
  const response = await fetchApi<null>(`/quality/sampling/orders/${id}`, {
    method: 'DELETE',
  })
  revalidatePath('/quality/sampling')
  return response
}

export async function submitSamplingOrderForApproval(id: string) {
  const response = await fetchApi<SamplingOrder>(`/quality/sampling/orders/${id}/submit`, {
    method: 'POST',
  })
  revalidatePath('/quality/sampling')
  return response
}

export async function approveSamplingOrder(id: string, data: SamplingApprovalCreate) {
  const response = await fetchApi<SamplingOrder>(`/quality/sampling/orders/${id}/approve`, {
    method: 'POST',
    body: JSON.stringify(data),
  })
  revalidatePath('/quality/sampling')
  return response
}

export async function getSamplingApprovals(orderId: string) {
  return fetchApi<SamplingApprovalRecord[]>(`/quality/sampling/orders/${orderId}/approvals`)
}

// ============ Retention Ledger Actions (留样台账) ============

export async function getRetentionLedger(params: RetentionLedgerFilter & { page?: number; page_size?: number } = {}) {
  const searchParams = new URLSearchParams()
  if (params.page) searchParams.set('page', String(params.page))
  if (params.page_size) searchParams.set('page_size', String(params.page_size))
  if (params.order_no) searchParams.set('order_no', params.order_no)
  if (params.sample_no) searchParams.set('sample_no', params.sample_no)
  if (params.material_code) searchParams.set('material_code', params.material_code)
  if (params.material_name) searchParams.set('material_name', params.material_name)
  if (params.retention_status) searchParams.set('retention_status', params.retention_status)

  const queryString = searchParams.toString()
  const endpoint = `/quality/sampling/retention-ledger${queryString ? `?${queryString}` : ''}`
  const response = await fetch(`${API_BASE}${endpoint}`)
  const data = await response.json()
  return data as ApiResponse<RetentionLedgerListResponse>
}

export async function getRetentionByOrder(orderId: string) {
  return fetchApi<SampleRetentionLedger[]>(`/quality/sampling/retention-ledger/order/${orderId}`)
}

// ============ IQC Inspection Actions (IQC检验) ============

import type {
  IQCInspection,
  IQCInspectionCreate,
  IQCInspectionUpdate,
  IQCInspectionListItem,
  IQCInspectionListResponse,
  IQCInspectionFilter,
  IQCInspectionItemCreate,
  IQCApprovalRecord,
  IQCApprovalCreate,
} from '@/types/iqc'

export async function getIQCInspections(params: IQCInspectionFilter & { page?: number; page_size?: number } = {}) {
  const searchParams = new URLSearchParams()
  if (params.page) searchParams.set('page', String(params.page))
  if (params.page_size) searchParams.set('page_size', String(params.page_size))
  if (params.inspection_no) searchParams.set('inspection_no', params.inspection_no)
  if (params.material_code) searchParams.set('material_code', params.material_code)
  if (params.material_name) searchParams.set('material_name', params.material_name)
  if (params.material_category) searchParams.set('material_category', params.material_category)
  if (params.supplier_name) searchParams.set('supplier_name', params.supplier_name)
  if (params.status) searchParams.set('status', params.status)
  if (params.inspection_conclusion) searchParams.set('inspection_conclusion', params.inspection_conclusion)
  if (params.start_date) searchParams.set('start_date', params.start_date)
  if (params.end_date) searchParams.set('end_date', params.end_date)

  const queryString = searchParams.toString()
  const endpoint = `/quality/iqc/inspections${queryString ? `?${queryString}` : ''}`
  const response = await fetch(`${API_BASE}${endpoint}`)
  const data = await response.json()
  return data as ApiResponse<IQCInspectionListResponse>
}

export async function getIQCInspection(id: string) {
  return fetchApi<IQCInspection>(`/quality/iqc/inspections/${id}`)
}

export async function createIQCInspection(data: IQCInspectionCreate) {
  const response = await fetchApi<IQCInspection>('/quality/iqc/inspections', {
    method: 'POST',
    body: JSON.stringify(data),
  })
  revalidatePath('/quality/iqc')
  return response
}

export async function updateIQCInspection(id: string, data: IQCInspectionUpdate) {
  const response = await fetchApi<IQCInspection>(`/quality/iqc/inspections/${id}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  })
  revalidatePath('/quality/iqc')
  return response
}

export async function deleteIQCInspection(id: string) {
  const response = await fetchApi<null>(`/quality/iqc/inspections/${id}`, {
    method: 'DELETE',
  })
  revalidatePath('/quality/iqc')
  return response
}

export async function submitIQCInspectionForApproval(id: string) {
  const response = await fetchApi<IQCInspection>(`/quality/iqc/inspections/${id}/submit`, {
    method: 'POST',
  })
  revalidatePath('/quality/iqc')
  return response
}

export async function approveIQCInspection(id: string, data: IQCApprovalCreate) {
  const response = await fetchApi<IQCInspection>(`/quality/iqc/inspections/${id}/approve`, {
    method: 'POST',
    body: JSON.stringify(data),
  })
  revalidatePath('/quality/iqc')
  return response
}

export async function getIQCApprovals(inspectionId: string) {
  return fetchApi<IQCApprovalRecord[]>(`/quality/iqc/inspections/${inspectionId}/approvals`)
}

// ============ IPQC Inspection Actions (IPQC过程检验) ============

import type {
  IPQCInspection,
  IPQCInspectionCreate,
  IPQCInspectionUpdate,
  IPQCInspectionListItem,
  IPQCInspectionListResponse,
  IPQCInspectionFilter,
  IPQCInspectionItemCreate,
  IPQCApprovalRecord,
  IPQCApprovalCreate,
} from '@/types/ipqc'

export async function getIPQCInspections(params: IPQCInspectionFilter & { page?: number; page_size?: number } = {}) {
  const searchParams = new URLSearchParams()
  if (params.page) searchParams.set('page', String(params.page))
  if (params.page_size) searchParams.set('page_size', String(params.page_size))
  if (params.inspection_no) searchParams.set('inspection_no', params.inspection_no)
  if (params.batch_no) searchParams.set('batch_no', params.batch_no)
  if (params.product_code) searchParams.set('product_code', params.product_code)
  if (params.product_name) searchParams.set('product_name', params.product_name)
  if (params.process_stage) searchParams.set('process_stage', params.process_stage)
  if (params.status) searchParams.set('status', params.status)
  if (params.inspection_conclusion) searchParams.set('inspection_conclusion', params.inspection_conclusion)
  if (params.batch_locked !== undefined) searchParams.set('batch_locked', String(params.batch_locked))
  if (params.start_date) searchParams.set('start_date', params.start_date)
  if (params.end_date) searchParams.set('end_date', params.end_date)

  const queryString = searchParams.toString()
  const endpoint = `/quality/ipqc/inspections${queryString ? `?${queryString}` : ''}`
  const response = await fetch(`${API_BASE}${endpoint}`)
  const data = await response.json()
  return data as ApiResponse<IPQCInspectionListResponse>
}

export async function getIPQCInspection(id: string) {
  return fetchApi<IPQCInspection>(`/quality/ipqc/inspections/${id}`)
}

export async function createIPQCInspection(data: IPQCInspectionCreate) {
  const response = await fetchApi<IPQCInspection>('/quality/ipqc/inspections', {
    method: 'POST',
    body: JSON.stringify(data),
  })
  revalidatePath('/quality/ipqc')
  return response
}

export async function updateIPQCInspection(id: string, data: IPQCInspectionUpdate) {
  const response = await fetchApi<IPQCInspection>(`/quality/ipqc/inspections/${id}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  })
  revalidatePath('/quality/ipqc')
  return response
}

export async function deleteIPQCInspection(id: string) {
  const response = await fetchApi<null>(`/quality/ipqc/inspections/${id}`, {
    method: 'DELETE',
  })
  revalidatePath('/quality/ipqc')
  return response
}

export async function submitIPQCInspectionForApproval(id: string) {
  const response = await fetchApi<IPQCInspection>(`/quality/ipqc/inspections/${id}/submit`, {
    method: 'POST',
  })
  revalidatePath('/quality/ipqc')
  return response
}

export async function approveIPQCInspection(id: string, data: IPQCApprovalCreate) {
  const response = await fetchApi<IPQCInspection>(`/quality/ipqc/inspections/${id}/approve`, {
    method: 'POST',
    body: JSON.stringify(data),
  })
  revalidatePath('/quality/ipqc')
  return response
}

export async function getIPQCApprovals(inspectionId: string) {
  return fetchApi<IPQCApprovalRecord[]>(`/quality/ipqc/inspections/${inspectionId}/approvals`)
}

export async function lockIPQCBatch(id: string, reason: string) {
  const response = await fetchApi<IPQCInspection>(`/quality/ipqc/inspections/${id}/lock-batch?reason=${encodeURIComponent(reason)}`, {
    method: 'POST',
  })
  revalidatePath('/quality/ipqc')
  return response
}

export async function unlockIPQCBatch(id: string) {
  const response = await fetchApi<IPQCInspection>(`/quality/ipqc/inspections/${id}/unlock-batch`, {
    method: 'POST',
  })
  revalidatePath('/quality/ipqc')
  return response
}

// ============ FQC Inspection Actions (FQC成品检验) ============

import type {
  FQCInspection,
  FQCInspectionCreate,
  FQCInspectionUpdate,
  FQCInspectionListItem,
  FQCInspectionListResponse,
  FQCInspectionFilter,
  FQCInspectionItemCreate,
  FQCApprovalRecord,
  FQCApprovalCreate,
} from '@/types/fqc'

export async function getFQCInspections(params: FQCInspectionFilter & { page?: number; page_size?: number } = {}) {
  const searchParams = new URLSearchParams()
  if (params.page) searchParams.set('page', String(params.page))
  if (params.page_size) searchParams.set('page_size', String(params.page_size))
  if (params.inspection_no) searchParams.set('inspection_no', params.inspection_no)
  if (params.batch_no) searchParams.set('batch_no', params.batch_no)
  if (params.product_code) searchParams.set('product_code', params.product_code)
  if (params.product_name) searchParams.set('product_name', params.product_name)
  if (params.production_workshop) searchParams.set('production_workshop', params.production_workshop)
  if (params.status) searchParams.set('status', params.status)
  if (params.inspection_conclusion) searchParams.set('inspection_conclusion', params.inspection_conclusion)
  if (params.release_status) searchParams.set('release_status', params.release_status)
  if (params.batch_locked !== undefined) searchParams.set('batch_locked', String(params.batch_locked))
  if (params.start_date) searchParams.set('start_date', params.start_date)
  if (params.end_date) searchParams.set('end_date', params.end_date)

  const queryString = searchParams.toString()
  const endpoint = `/quality/fqc/inspections${queryString ? `?${queryString}` : ''}`
  const response = await fetch(`${API_BASE}${endpoint}`)
  const data = await response.json()
  return data as ApiResponse<FQCInspectionListResponse>
}

export async function getFQCInspection(id: string) {
  return fetchApi<FQCInspection>(`/quality/fqc/inspections/${id}`)
}

export async function createFQCInspection(data: FQCInspectionCreate) {
  const response = await fetchApi<FQCInspection>('/quality/fqc/inspections', {
    method: 'POST',
    body: JSON.stringify(data),
  })
  revalidatePath('/quality/fqc')
  return response
}

export async function updateFQCInspection(id: string, data: FQCInspectionUpdate) {
  const response = await fetchApi<FQCInspection>(`/quality/fqc/inspections/${id}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  })
  revalidatePath('/quality/fqc')
  return response
}

export async function deleteFQCInspection(id: string) {
  const response = await fetchApi<null>(`/quality/fqc/inspections/${id}`, {
    method: 'DELETE',
  })
  revalidatePath('/quality/fqc')
  return response
}

export async function submitFQCInspectionForApproval(id: string) {
  const response = await fetchApi<FQCInspection>(`/quality/fqc/inspections/${id}/submit`, {
    method: 'POST',
  })
  revalidatePath('/quality/fqc')
  return response
}

export async function approveFQCInspection(id: string, data: FQCApprovalCreate) {
  const response = await fetchApi<FQCInspection>(`/quality/fqc/inspections/${id}/approve`, {
    method: 'POST',
    body: JSON.stringify(data),
  })
  revalidatePath('/quality/fqc')
  return response
}

export async function getFQCApprovals(inspectionId: string) {
  return fetchApi<FQCApprovalRecord[]>(`/quality/fqc/inspections/${inspectionId}/approvals`)
}

export async function applyFQCReinspection(id: string, reason: string) {
  const response = await fetchApi<FQCInspection>(`/quality/fqc/inspections/${id}/reinspection?reason=${encodeURIComponent(reason)}`, {
    method: 'POST',
  })
  revalidatePath('/quality/fqc')
  return response
}

export async function releaseFQCInspection(id: string, releaseReason?: string) {
  const url = releaseReason
    ? `/quality/fqc/inspections/${id}/release?release_reason=${encodeURIComponent(releaseReason)}`
    : `/quality/fqc/inspections/${id}/release`
  const response = await fetchApi<FQCInspection>(url, {
    method: 'POST',
  })
  revalidatePath('/quality/fqc')
  return response
}

export async function lockFQCBatch(id: string, reason: string) {
  const response = await fetchApi<FQCInspection>(`/quality/fqc/inspections/${id}/lock-batch?reason=${encodeURIComponent(reason)}`, {
    method: 'POST',
  })
  revalidatePath('/quality/fqc')
  return response
}

export async function unlockFQCBatch(id: string) {
  const response = await fetchApi<FQCInspection>(`/quality/fqc/inspections/${id}/unlock-batch`, {
    method: 'POST',
  })
  revalidatePath('/quality/fqc')
  return response
}

// ============ Stability Study Actions (稳定性试验管理) ============

import type {
  StabilityStudy,
  StabilityStudyCreate,
  StabilityStudyUpdate,
  StabilityStudyListItem,
  StabilityStudyListResponse,
  StabilityStudyFilter,
  StabilitySampleNode,
  StabilitySampleNodeUpdate,
  StabilityInspection,
  StabilityInspectionCreate,
  StabilityInspectionUpdate,
  StabilityInspectionListItem,
  StabilityInspectionListResponse,
  StabilityInspectionFilter,
  StabilityInspectionItemCreate,
  StabilityApprovalRecord,
  StabilityApprovalCreate,
  TrendData,
} from '@/types/stability'

export async function getStabilityStudies(params: StabilityStudyFilter & { page?: number; page_size?: number } = {}) {
  const searchParams = new URLSearchParams()
  if (params.page) searchParams.set('page', String(params.page))
  if (params.page_size) searchParams.set('page_size', String(params.page_size))
  if (params.study_no) searchParams.set('study_no', params.study_no)
  if (params.product_code) searchParams.set('product_code', params.product_code)
  if (params.product_name) searchParams.set('product_name', params.product_name)
  if (params.study_type) searchParams.set('study_type', params.study_type)
  if (params.status) searchParams.set('status', params.status)
  if (params.batch_no) searchParams.set('batch_no', params.batch_no)
  if (params.start_date) searchParams.set('start_date', params.start_date)
  if (params.end_date) searchParams.set('end_date', params.end_date)

  const queryString = searchParams.toString()
  const endpoint = `/quality/stability/studies${queryString ? `?${queryString}` : ''}`
  const response = await fetch(`${API_BASE}${endpoint}`)
  const data = await response.json()
  return data as ApiResponse<StabilityStudyListResponse>
}

export async function getStabilityStudy(id: string) {
  return fetchApi<StabilityStudy>(`/quality/stability/studies/${id}`)
}

export async function createStabilityStudy(data: StabilityStudyCreate) {
  const response = await fetchApi<StabilityStudy>('/quality/stability/studies', {
    method: 'POST',
    body: JSON.stringify(data),
  })
  revalidatePath('/quality/stability')
  return response
}

export async function updateStabilityStudy(id: string, data: StabilityStudyUpdate) {
  const response = await fetchApi<StabilityStudy>(`/quality/stability/studies/${id}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  })
  revalidatePath('/quality/stability')
  return response
}

export async function deleteStabilityStudy(id: string) {
  const response = await fetchApi<null>(`/quality/stability/studies/${id}`, {
    method: 'DELETE',
  })
  revalidatePath('/quality/stability')
  return response
}

export async function submitStabilityStudy(id: string) {
  const response = await fetchApi<StabilityStudy>(`/quality/stability/studies/${id}/submit`, {
    method: 'POST',
  })
  revalidatePath('/quality/stability')
  return response
}

export async function approveStabilityStudy(id: string, data: StabilityApprovalCreate) {
  const response = await fetchApi<StabilityStudy>(`/quality/stability/studies/${id}/approve`, {
    method: 'POST',
    body: JSON.stringify(data),
  })
  revalidatePath('/quality/stability')
  return response
}

export async function getStabilityStudySampleNodes(studyId: string) {
  return fetchApi<StabilitySampleNode[]>(`/quality/stability/studies/${studyId}/sample-nodes`)
}

export async function updateStabilitySampleNode(id: string, data: StabilitySampleNodeUpdate) {
  const response = await fetchApi<StabilitySampleNode>(`/quality/stability/sample-nodes/${id}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  })
  return response
}

export async function getStabilityInspections(params: StabilityInspectionFilter & { page?: number; page_size?: number } = {}) {
  const searchParams = new URLSearchParams()
  if (params.page) searchParams.set('page', String(params.page))
  if (params.page_size) searchParams.set('page_size', String(params.page_size))
  if (params.study_id) searchParams.set('study_id', params.study_id)
  if (params.study_no) searchParams.set('study_no', params.study_no)
  if (params.inspection_no) searchParams.set('inspection_no', params.inspection_no)
  if (params.batch_no) searchParams.set('batch_no', params.batch_no)
  if (params.status) searchParams.set('status', params.status)
  if (params.start_date) searchParams.set('start_date', params.start_date)
  if (params.end_date) searchParams.set('end_date', params.end_date)

  const queryString = searchParams.toString()
  const endpoint = `/quality/stability/inspections${queryString ? `?${queryString}` : ''}`
  const response = await fetch(`${API_BASE}${endpoint}`)
  const data = await response.json()
  return data as ApiResponse<StabilityInspectionListResponse>
}

export async function getStabilityInspection(id: string) {
  return fetchApi<StabilityInspection>(`/quality/stability/inspections/${id}`)
}

export async function createStabilityInspection(data: StabilityInspectionCreate) {
  const response = await fetchApi<StabilityInspection>('/quality/stability/inspections', {
    method: 'POST',
    body: JSON.stringify(data),
  })
  revalidatePath('/quality/stability')
  return response
}

export async function updateStabilityInspection(id: string, data: StabilityInspectionUpdate) {
  const response = await fetchApi<StabilityInspection>(`/quality/stability/inspections/${id}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  })
  revalidatePath('/quality/stability')
  return response
}

export async function submitStabilityInspection(id: string) {
  const response = await fetchApi<StabilityInspection>(`/quality/stability/inspections/${id}/submit`, {
    method: 'POST',
  })
  revalidatePath('/quality/stability')
  return response
}

export async function getStabilityTrendData(studyId: string) {
  return fetchApi<TrendData>(`/quality/stability/studies/${studyId}/trend`)
}

// ============ AI交互日志 Actions ============

export interface AiLogItem {
  id: string
  bill_no: string | null
  operate_type: string
  operator: string
  system_prompt: string | null
  user_input: string | null
  ai_response: string | null
  error_message: string | null
  tokens_used: number | null
  latency_ms: number | null
  created_at: string
}

export interface AiLogListResponse {
  items: AiLogItem[]
  total: number
  page: number
  page_size: number
}

export interface AiLogFilter {
  operate_type?: string
  operator?: string
  start_date?: string
  end_date?: string
  keyword?: string
}

export async function getAiLogs(params: AiLogFilter & { page?: number; page_size?: number } = {}) {
  const searchParams = new URLSearchParams()
  if (params.page) searchParams.set('page', String(params.page))
  if (params.page_size) searchParams.set('page_size', String(params.page_size))
  if (params.operate_type) searchParams.set('operate_type', params.operate_type)
  if (params.operator) searchParams.set('operator', params.operator)
  if (params.start_date) searchParams.set('start_date', params.start_date)
  if (params.end_date) searchParams.set('end_date', params.end_date)
  if (params.keyword) searchParams.set('keyword', params.keyword)

  const queryString = searchParams.toString()
  const endpoint = `/ai/logs${queryString ? `?${queryString}` : ''}`
  const response = await fetch(`${API_BASE}${endpoint}`)
  const data = await response.json()
  return data as ApiResponse<AiLogListResponse>
}

export async function getAiLogById(id: string) {
  return fetchApi<AiLogItem>(`/ai/logs/${id}`)
}