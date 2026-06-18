'use client'

import { useState, useCallback, useEffect } from 'react'
import {
  Table,
  Button,
  Space,
  Input,
  Select,
  DatePicker,
  Tag,
  Modal,
  Form,
  InputNumber,
  message,
  Popconfirm,
  Card,
  Row,
  Col,
  Divider,
  Typography,
  Descriptions,
  Tabs,
  Radio,
  Badge,
} from 'antd'
import type { ColumnsType } from 'antd/es/table'
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  EyeOutlined,
  CheckOutlined,
  CloseOutlined,
  ExclamationCircleOutlined,
} from '@ant-design/icons'
import dayjs from 'dayjs'
import {
  Instrument,
  InstrumentListItem,
  InstrumentCreate,
  InstrumentUpdate,
  InstrumentFilter,
  InstrumentStatus,
  InstrumentStatusLabels,
  InstrumentStatusColors,
  InstrumentCategory,
  InstrumentCategoryLabels,
  IQStatus,
  IQStatusLabels,
  IQStatusColors,
  OQStatus,
  OQStatusLabels,
  OQStatusColors,
  CalibrationRule,
  CalibrationRuleCreate,
  CalibrationRuleUpdate,
  CalibrationRecord,
  CalibrationRecordListItem,
  CalibrationRecordCreate,
  CalibrationRecordUpdate,
  CalibrationRecordFilter,
  CalibrationMethod,
  CalibrationMethodLabels,
  CalibrationCycleUnit,
  CalibrationCycleUnitLabels,
  CalibrationResult,
  CalibrationResultLabels,
  CalibrationResultColors,
  RecordStatus,
  RecordStatusLabels,
  RecordStatusColors,
  ApprovalStatus,
  ApprovalStatusLabels,
} from '@/types/instrument'
import {
  getInstruments,
  getInstrument,
  createInstrument,
  updateInstrument,
  deleteInstrument,
  submitInstrument,
  approveInstrumentByAdmin,
  approveInstrumentByQA,
  rejectInstrument,
  getCalibrationRules,
  getCalibrationRule,
  createCalibrationRule,
  updateCalibrationRule,
  deleteCalibrationRule,
  getCalibrationRecords,
  getCalibrationRecord,
  createCalibrationRecord,
  updateCalibrationRecord,
  deleteCalibrationRecord,
  submitCalibrationRecord,
  approveCalibrationRecordByAdmin,
  approveCalibrationRecordByQA,
  rejectCalibrationRecord,
  getInstrumentApprovals,
  getCalibrationRecordApprovals,
} from '@/actions/instrument'

const { RangePicker } = DatePicker
const { Text } = Typography
const { TextArea } = Input

// 初始筛选条件
const initialInstrumentFilter: InstrumentFilter = {
  instrument_no: '',
  instrument_name: '',
  category: undefined,
  is_active: undefined,
  status: undefined,
  is_overdue: undefined,
}

const initialRecordFilter: CalibrationRecordFilter = {
  calibration_no: '',
  calibration_result: undefined,
  status: undefined,
  calibration_method: undefined,
}

// 生成仪器编号
function generateInstrumentNo() {
  const date = dayjs().format('YYYYMMDD')
  const random = Math.floor(Math.random() * 10000).toString().padStart(4, '0')
  return `INS-${date}-${random}`
}

export default function InstrumentPage() {
  // 状态
  const [loading, setLoading] = useState(false)
  const [activeTab, setActiveTab] = useState('instruments')

  // 仪器台账状态
  const [instrumentData, setInstrumentData] = useState<InstrumentListItem[]>([])
  const [instrumentTotal, setInstrumentTotal] = useState(0)
  const [instrumentPage, setInstrumentPage] = useState(1)
  const [instrumentPageSize, setInstrumentPageSize] = useState(20)
  const [instrumentFilters, setInstrumentFilters] = useState<InstrumentFilter>(initialInstrumentFilter)

  // 校准记录状态
  const [recordData, setRecordData] = useState<CalibrationRecordListItem[]>([])
  const [recordTotal, setRecordTotal] = useState(0)
  const [recordPage, setRecordPage] = useState(1)
  const [recordPageSize, setRecordPageSize] = useState(20)
  const [recordFilters, setRecordFilters] = useState<CalibrationRecordFilter>(initialRecordFilter)

  // 表单
  const [createForm] = Form.useForm()
  const [editForm] = Form.useForm()
  const [ruleForm] = Form.useForm()
  const [recordForm] = Form.useForm()
  const [recordEditForm] = Form.useForm()

  // 弹窗状态
  const [instrumentModalVisible, setInstrumentModalVisible] = useState(false)
  const [instrumentEditRecord, setInstrumentEditRecord] = useState<Instrument | null>(null)
  const [instrumentViewRecord, setInstrumentViewRecord] = useState<Instrument | null>(null)
  const [instrumentViewVisible, setInstrumentViewVisible] = useState(false)
  const [instrumentMode, setInstrumentMode] = useState<'create' | 'edit'>('create')

  const [ruleModalVisible, setRuleModalVisible] = useState(false)
  const [ruleEditRecord, setRuleEditRecord] = useState<CalibrationRule | null>(null)
  const [ruleMode, setRuleMode] = useState<'create' | 'edit'>('create')
  const [selectedInstrumentId, setSelectedInstrumentId] = useState<string | null>(null)

  const [recordModalVisible, setRecordModalVisible] = useState(false)
  const [recordEditRecord, setRecordEditRecord] = useState<CalibrationRecord | null>(null)
  const [recordViewRecord, setRecordViewRecord] = useState<CalibrationRecord | null>(null)
  const [recordViewVisible, setRecordViewVisible] = useState(false)
  const [recordMode, setRecordMode] = useState<'create' | 'edit'>('create')

  const [approvalModalVisible, setApprovalModalVisible] = useState(false)
  const [approvalRecord, setApprovalRecord] = useState<any>(null)
  const [approvalType, setApprovalType] = useState<'instrument' | 'record'>('instrument')

  const [submitLoading, setSubmitLoading] = useState(false)

  // 加载仪器数据
  const loadInstruments = useCallback(async () => {
    setLoading(true)
    try {
      const response = await getInstruments({
        ...instrumentFilters,
        page: instrumentPage,
        page_size: instrumentPageSize,
      }) as any
      if (response.items) {
        setInstrumentData(response.items || [])
        setInstrumentTotal(response.total || 0)
      } else {
        message.error(response.message || '加载失败')
      }
    } catch (error) {
      message.error('加载数据失败')
    } finally {
      setLoading(false)
    }
  }, [instrumentFilters, instrumentPage, instrumentPageSize])

  // 加载校准记录
  const loadRecords = useCallback(async () => {
    setLoading(true)
    try {
      const response = await getCalibrationRecords({
        ...recordFilters,
        page: recordPage,
        page_size: recordPageSize,
      }) as any
      if (response.items) {
        setRecordData(response.items || [])
        setRecordTotal(response.total || 0)
      } else {
        message.error(response.message || '加载失败')
      }
    } catch (error) {
      message.error('加载数据失败')
    } finally {
      setLoading(false)
    }
  }, [recordFilters, recordPage, recordPageSize])

  useEffect(() => {
    if (activeTab === 'instruments') {
      loadInstruments()
    } else if (activeTab === 'records') {
      loadRecords()
    }
  }, [activeTab, loadInstruments, loadRecords])

  // 仪器操作
  const handleCreateInstrument = () => {
    setInstrumentMode('create')
    createForm.setFieldsValue({
      instrument_no: generateInstrumentNo(),
      is_active: true,
    })
    setInstrumentModalVisible(true)
  }

  const handleEditInstrument = async (record: InstrumentListItem) => {
    try {
      const response = await getInstrument(record.id) as any
      if (response.id) {
        setInstrumentEditRecord(response)
        setInstrumentMode('edit')
        editForm.setFieldsValue({
          ...response,
          manufacture_date: response.manufacture_date ? dayjs(response.manufacture_date) : null,
          iq_confirm_date: response.iq_confirm_date ? dayjs(response.iq_confirm_date) : null,
          oq_confirm_date: response.oq_confirm_date ? dayjs(response.oq_confirm_date) : null,
        })
        setInstrumentModalVisible(true)
      } else {
        message.error(response.message || '获取数据失败')
      }
    } catch (error) {
      message.error('获取数据失败')
    }
  }

  const handleViewInstrument = async (record: InstrumentListItem) => {
    try {
      const response = await getInstrument(record.id) as any
      if (response.id) {
        setInstrumentViewRecord(response)
        setInstrumentViewVisible(true)
      } else {
        message.error(response.message || '获取数据失败')
      }
    } catch (error) {
      message.error('获取数据失败')
    }
  }

  const handleDeleteInstrument = async (id: string) => {
    try {
      await deleteInstrument(id) as any
      message.success('删除成功')
      loadInstruments()
    } catch (error) {
      message.error('删除失败')
    }
  }

  const handleSubmitInstrument = async (id: string) => {
    setSubmitLoading(true)
    try {
      const response = await submitInstrument(id) as any
      if (response.id) {
        message.success('提交成功')
        loadInstruments()
      } else {
        message.error(response.message || '提交失败')
      }
    } catch (error) {
      message.error('提交失败')
    } finally {
      setSubmitLoading(false)
    }
  }

  const handleApproveInstrument = async (id: string, level: 'admin' | 'qa') => {
    setSubmitLoading(true)
    try {
      const response = level === 'admin'
        ? await approveInstrumentByAdmin(id) as any
        : await approveInstrumentByQA(id) as any
      if (response.id) {
        message.success('审批成功')
        loadInstruments()
      } else {
        message.error(response.message || '审批失败')
      }
    } catch (error) {
      message.error('审批失败')
    } finally {
      setSubmitLoading(false)
    }
  }

  const handleRejectInstrument = async (id: string) => {
    Modal.confirm({
      title: '驳回仪器',
      icon: <ExclamationCircleOutlined />,
      content: (
        <Input.TextArea
          id="reject-comments"
          placeholder="请输入驳回原因"
          rows={3}
        />
      ),
      onOk: async () => {
        const comments = (document.getElementById('reject-comments') as HTMLTextAreaElement)?.value
        if (!comments) {
          message.warning('请输入驳回原因')
          return
        }
        setSubmitLoading(true)
        try {
          const response = await rejectInstrument(id, comments) as any
          if (response.id) {
            message.success('驳回成功')
            loadInstruments()
          } else {
            message.error(response.message || '驳回失败')
          }
        } catch (error) {
          message.error('驳回失败')
        } finally {
          setSubmitLoading(false)
        }
      },
    })
  }

  const handleSaveInstrument = async () => {
    try {
      const values = await (instrumentMode === 'create' ? createForm : editForm).validateFields()
      setSubmitLoading(true)
      let response
      if (instrumentMode === 'create') {
        response = await createInstrument(values as InstrumentCreate) as any
      } else if (instrumentEditRecord) {
        response = await updateInstrument(instrumentEditRecord.id, values as InstrumentUpdate) as any
      } else {
        return
      }
      if (response.id) {
        message.success(instrumentMode === 'create' ? '创建成功' : '更新成功')
        setInstrumentModalVisible(false)
        loadInstruments()
      } else {
        message.error(response.message || '操作失败')
      }
    } catch (error: any) {
      if (!error.errorFields) {
        message.error(error.message || '操作失败')
      }
    } finally {
      setSubmitLoading(false)
    }
  }

  // 校准规则操作
  const handleOpenRuleModal = async (instrumentId: string, record?: CalibrationRule) => {
    setSelectedInstrumentId(instrumentId)
    if (record) {
      setRuleEditRecord(record)
      setRuleMode('edit')
      ruleForm.setFieldsValue({
        ...record,
        last_calibration_date: record.last_calibration_date ? dayjs(record.last_calibration_date) : null,
        next_calibration_date: record.next_calibration_date ? dayjs(record.next_calibration_date) : null,
      })
    } else {
      setRuleEditRecord(null)
      setRuleMode('create')
      ruleForm.resetFields()
      ruleForm.setFieldsValue({
        instrument_id: instrumentId,
        calibration_method: CalibrationMethod.EXTERNAL,
        warning_days: 7,
        is_active: true,
      })
    }
    setRuleModalVisible(true)
  }

  const handleSaveRule = async () => {
    try {
      const values = await ruleForm.validateFields()
      setSubmitLoading(true)
      let response
      if (ruleMode === 'create') {
        response = await createCalibrationRule(values as CalibrationRuleCreate) as any
      } else if (ruleEditRecord) {
        response = await updateCalibrationRule(ruleEditRecord.id, values as CalibrationRuleUpdate) as any
      } else {
        return
      }
      if (response.id) {
        message.success(ruleMode === 'create' ? '创建成功' : '更新成功')
        setRuleModalVisible(false)
        loadInstruments()
      } else {
        message.error(response.message || '操作失败')
      }
    } catch (error: any) {
      if (!error.errorFields) {
        message.error(error.message || '操作失败')
      }
    } finally {
      setSubmitLoading(false)
    }
  }

  const handleDeleteRule = async (id: string) => {
    try {
      await deleteCalibrationRule(id) as any
      message.success('删除成功')
      loadInstruments()
    } catch (error) {
      message.error('删除失败')
    }
  }

  // 校准记录操作
  const handleCreateRecord = () => {
    setRecordMode('create')
    recordForm.resetFields()
    recordForm.setFieldsValue({
      calibration_date: dayjs(),
      is_scheduled: false,
    })
    setRecordModalVisible(true)
  }

  const handleEditRecord = async (record: CalibrationRecordListItem) => {
    try {
      const response = await getCalibrationRecord(record.id) as any
      if (response.id) {
        setRecordEditRecord(response)
        setRecordMode('edit')
        recordEditForm.setFieldsValue({
          ...response,
          calibration_date: response.calibration_date ? dayjs(response.calibration_date) : null,
          calibration_end_date: response.calibration_end_date ? dayjs(response.calibration_end_date) : null,
          valid_from: response.valid_from ? dayjs(response.valid_from) : null,
          valid_until: response.valid_until ? dayjs(response.valid_until) : null,
          scheduled_date: response.scheduled_date ? dayjs(response.scheduled_date) : null,
        })
        setRecordModalVisible(true)
      } else {
        message.error(response.message || '获取数据失败')
      }
    } catch (error) {
      message.error('获取数据失败')
    }
  }

  const handleViewRecord = async (record: CalibrationRecordListItem) => {
    try {
      const response = await getCalibrationRecord(record.id) as any
      if (response.id) {
        setRecordViewRecord(response)
        setRecordViewVisible(true)
      } else {
        message.error(response.message || '获取数据失败')
      }
    } catch (error) {
      message.error('获取数据失败')
    }
  }

  const handleDeleteRecord = async (id: string) => {
    try {
      await deleteCalibrationRecord(id) as any
      message.success('删除成功')
      loadRecords()
    } catch (error) {
      message.error('删除失败')
    }
  }

  const handleSubmitRecord = async (id: string) => {
    setSubmitLoading(true)
    try {
      const response = await submitCalibrationRecord(id) as any
      if (response.id) {
        message.success('提交成功')
        loadRecords()
      } else {
        message.error(response.message || '提交失败')
      }
    } catch (error) {
      message.error('提交失败')
    } finally {
      setSubmitLoading(false)
    }
  }

  const handleApproveRecord = async (id: string, level: 'admin' | 'qa') => {
    setSubmitLoading(true)
    try {
      const response = level === 'admin'
        ? await approveCalibrationRecordByAdmin(id) as any
        : await approveCalibrationRecordByQA(id) as any
      if (response.id) {
        message.success('审批成功')
        loadRecords()
      } else {
        message.error(response.message || '审批失败')
      }
    } catch (error) {
      message.error('审批失败')
    } finally {
      setSubmitLoading(false)
    }
  }

  const handleRejectRecord = async (id: string) => {
    Modal.confirm({
      title: '驳回校准记录',
      icon: <ExclamationCircleOutlined />,
      content: (
        <Input.TextArea
          id="record-reject-comments"
          placeholder="请输入驳回原因"
          rows={3}
        />
      ),
      onOk: async () => {
        const comments = (document.getElementById('record-reject-comments') as HTMLTextAreaElement)?.value
        if (!comments) {
          message.warning('请输入驳回原因')
          return
        }
        setSubmitLoading(true)
        try {
          const response = await rejectCalibrationRecord(id, comments) as any
          if (response.id) {
            message.success('驳回成功')
            loadRecords()
          } else {
            message.error(response.message || '驳回失败')
          }
        } catch (error) {
          message.error('驳回失败')
        } finally {
          setSubmitLoading(false)
        }
      },
    })
  }

  const handleSaveRecord = async () => {
    try {
      const values = await (recordMode === 'create' ? recordForm : recordEditForm).validateFields()
      setSubmitLoading(true)
      let response
      if (recordMode === 'create') {
        response = await createCalibrationRecord(values as CalibrationRecordCreate) as any
      } else if (recordEditRecord) {
        response = await updateCalibrationRecord(recordEditRecord.id, values as CalibrationRecordUpdate) as any
      } else {
        return
      }
      if (response.id) {
        message.success(recordMode === 'create' ? '创建成功' : '更新成功')
        setRecordModalVisible(false)
        loadRecords()
      } else {
        message.error(response.message || '操作失败')
      }
    } catch (error: any) {
      if (!error.errorFields) {
        message.error(error.message || '操作失败')
      }
    } finally {
      setSubmitLoading(false)
    }
  }

  // 仪器列表列定义
  const instrumentColumns: ColumnsType<InstrumentListItem> = [
    {
      title: '仪器编号',
      dataIndex: 'instrument_no',
      key: 'instrument_no',
      width: 150,
    },
    {
      title: '仪器名称',
      dataIndex: 'instrument_name',
      key: 'instrument_name',
      width: 180,
    },
    {
      title: '型号',
      dataIndex: 'model',
      key: 'model',
      width: 120,
    },
    {
      title: '分类',
      dataIndex: 'category',
      key: 'category',
      width: 100,
      render: (category: string) => category ? InstrumentCategoryLabels[category as InstrumentCategory] || category : '-',
    },
    {
      title: '存放地点',
      dataIndex: 'location',
      key: 'location',
      width: 120,
    },
    {
      title: '负责人',
      dataIndex: 'responsible_name',
      key: 'responsible_name',
      width: 100,
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 120,
      render: (status: InstrumentStatus) => (
        <Tag color={InstrumentStatusColors[status]}>
          {InstrumentStatusLabels[status]}
        </Tag>
      ),
    },
    {
      title: 'IQ状态',
      dataIndex: 'iq_status',
      key: 'iq_status',
      width: 100,
      render: (iq_status: IQStatus) => iq_status ? (
        <Tag color={IQStatusColors[iq_status]}>
          {IQStatusLabels[iq_status]}
        </Tag>
      ) : '-',
    },
    {
      title: 'OQ状态',
      dataIndex: 'oq_status',
      key: 'oq_status',
      width: 100,
      render: (oq_status: OQStatus) => oq_status ? (
        <Tag color={OQStatusColors[oq_status]}>
          {OQStatusLabels[oq_status]}
        </Tag>
      ) : '-',
    },
    {
      title: '校准到期',
      dataIndex: 'next_calibration_date',
      key: 'next_calibration_date',
      width: 120,
      render: (date: string, record) => {
        if (!date) return '-'
        const isOverdue = record.is_overdue
        return (
          <Badge status={isOverdue ? 'error' : 'success'} text={dayjs(date).format('YYYY-MM-DD')} />
        )
      },
    },
    {
      title: '启用',
      dataIndex: 'is_active',
      key: 'is_active',
      width: 80,
      render: (is_active: boolean) => (
        <Tag color={is_active ? 'green' : 'default'}>
          {is_active ? '是' : '否'}
        </Tag>
      ),
    },
    {
      title: '操作',
      key: 'action',
      width: 280,
      fixed: 'right',
      render: (_, record) => (
        <Space size="small">
          <Button type="link" size="small" icon={<EyeOutlined />} onClick={() => handleViewInstrument(record)}>
            查看
          </Button>
          {record.status === InstrumentStatus.DRAFT && (
            <>
              <Button type="link" size="small" icon={<EditOutlined />} onClick={() => handleEditInstrument(record)}>
                编辑
              </Button>
              <Button type="link" size="small" onClick={() => handleSubmitInstrument(record.id)}>
                提交
              </Button>
              <Popconfirm title="确定删除?" onConfirm={() => handleDeleteInstrument(record.id)}>
                <Button type="link" size="small" danger icon={<DeleteOutlined />}>
                  删除
                </Button>
              </Popconfirm>
            </>
          )}
          {record.status === InstrumentStatus.SUBMITTED && (
            <Button type="link" size="small" onClick={() => handleApproveInstrument(record.id, 'admin')}>
              设备管理员审核
            </Button>
          )}
          {record.status === InstrumentStatus.ADMIN_APPROVED && (
            <Button type="link" size="small" onClick={() => handleApproveInstrument(record.id, 'qa')}>
              QA审核
            </Button>
          )}
          {(record.status === InstrumentStatus.SUBMITTED || record.status === InstrumentStatus.ADMIN_APPROVED) && (
            <Button type="link" size="small" danger onClick={() => handleRejectInstrument(record.id)}>
              驳回
            </Button>
          )}
          {(record.status === InstrumentStatus.DRAFT || record.status === InstrumentStatus.ACTIVE) && (
            <Button type="link" size="small" onClick={() => handleOpenRuleModal(record.id)}>
              配置校准规则
            </Button>
          )}
        </Space>
      ),
    },
  ]

  // 校准记录列表列定义
  const recordColumns: ColumnsType<CalibrationRecordListItem> = [
    {
      title: '校准单号',
      dataIndex: 'calibration_no',
      key: 'calibration_no',
      width: 150,
    },
    {
      title: '仪器编号',
      dataIndex: 'instrument_no',
      key: 'instrument_no',
      width: 120,
    },
    {
      title: '仪器名称',
      dataIndex: 'instrument_name',
      key: 'instrument_name',
      width: 150,
    },
    {
      title: '校准日期',
      dataIndex: 'calibration_date',
      key: 'calibration_date',
      width: 120,
      render: (date: string) => date ? dayjs(date).format('YYYY-MM-DD') : '-',
    },
    {
      title: '校准方式',
      dataIndex: 'calibration_method',
      key: 'calibration_method',
      width: 100,
      render: (method: string) => CalibrationMethodLabels[method as CalibrationMethod] || method,
    },
    {
      title: '校准人员',
      dataIndex: 'calibrator_name',
      key: 'calibrator_name',
      width: 100,
    },
    {
      title: '证书编号',
      dataIndex: 'certificate_no',
      key: 'certificate_no',
      width: 120,
    },
    {
      title: '校准结论',
      dataIndex: 'calibration_result',
      key: 'calibration_result',
      width: 100,
      render: (result: CalibrationResult) => (
        <Tag color={CalibrationResultColors[result]}>
          {CalibrationResultLabels[result]}
        </Tag>
      ),
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 120,
      render: (status: RecordStatus) => (
        <Tag color={RecordStatusColors[status]}>
          {RecordStatusLabels[status]}
        </Tag>
      ),
    },
    {
      title: '操作',
      key: 'action',
      width: 250,
      fixed: 'right',
      render: (_, record) => (
        <Space size="small">
          <Button type="link" size="small" icon={<EyeOutlined />} onClick={() => handleViewRecord(record)}>
            查看
          </Button>
          {record.status === RecordStatus.DRAFT && (
            <>
              <Button type="link" size="small" icon={<EditOutlined />} onClick={() => handleEditRecord(record)}>
                编辑
              </Button>
              <Button type="link" size="small" onClick={() => handleSubmitRecord(record.id)}>
                提交
              </Button>
              <Popconfirm title="确定删除?" onConfirm={() => handleDeleteRecord(record.id)}>
                <Button type="link" size="small" danger icon={<DeleteOutlined />}>
                  删除
                </Button>
              </Popconfirm>
            </>
          )}
          {record.status === RecordStatus.SUBMITTED && (
            <Button type="link" size="small" onClick={() => handleApproveRecord(record.id, 'admin')}>
              设备管理员审核
            </Button>
          )}
          {record.status === RecordStatus.ADMIN_APPROVED && (
            <Button type="link" size="small" onClick={() => handleApproveRecord(record.id, 'qa')}>
              QA审核
            </Button>
          )}
          {(record.status === RecordStatus.SUBMITTED || record.status === RecordStatus.ADMIN_APPROVED) && (
            <Button type="link" size="small" danger onClick={() => handleRejectRecord(record.id)}>
              驳回
            </Button>
          )}
        </Space>
      ),
    },
  ]

  return (
    <div style={{ padding: 24 }}>
      <Card title="仪器校准管理">
        <Tabs
          activeKey={activeTab}
          onChange={setActiveTab}
          items={[
            {
              key: 'instruments',
              label: '仪器台账',
              children: (
                <>
                  {/* 筛选区域 */}
                  <Card size="small" style={{ marginBottom: 16 }}>
                    <Row gutter={16}>
                      <Col span={5}>
                        <Input
                          placeholder="仪器编号"
                          value={instrumentFilters.instrument_no}
                          onChange={e => setInstrumentFilters({ ...instrumentFilters, instrument_no: e.target.value })}
                          allowClear
                        />
                      </Col>
                      <Col span={5}>
                        <Input
                          placeholder="仪器名称"
                          value={instrumentFilters.instrument_name}
                          onChange={e => setInstrumentFilters({ ...instrumentFilters, instrument_name: e.target.value })}
                          allowClear
                        />
                      </Col>
                      <Col span={4}>
                        <Select
                          placeholder="仪器分类"
                          value={instrumentFilters.category}
                          onChange={value => setInstrumentFilters({ ...instrumentFilters, category: value })}
                          allowClear
                          style={{ width: '100%' }}
                        >
                          {Object.entries(InstrumentCategory).map(([key, value]) => (
                            <Select.Option key={value} value={value}>
                              {InstrumentCategoryLabels[value]}
                            </Select.Option>
                          ))}
                        </Select>
                      </Col>
                      <Col span={4}>
                        <Select
                          placeholder="状态"
                          value={instrumentFilters.status}
                          onChange={value => setInstrumentFilters({ ...instrumentFilters, status: value })}
                          allowClear
                          style={{ width: '100%' }}
                        >
                          {Object.entries(InstrumentStatus).map(([key, value]) => (
                            <Select.Option key={value} value={value}>
                              {InstrumentStatusLabels[value]}
                            </Select.Option>
                          ))}
                        </Select>
                      </Col>
                      <Col span={6}>
                        <Space>
                          <Button type="primary" onClick={loadInstruments}>查询</Button>
                          <Button onClick={() => setInstrumentFilters(initialInstrumentFilter)}>重置</Button>
                          <Button type="primary" icon={<PlusOutlined />} onClick={handleCreateInstrument}>新增仪器</Button>
                        </Space>
                      </Col>
                    </Row>
                  </Card>

                  {/* 表格 */}
                  <Table
                    columns={instrumentColumns}
                    dataSource={instrumentData}
                    loading={loading}
                    rowKey="id"
                    scroll={{ x: 1400 }}
                    pagination={{
                      current: instrumentPage,
                      pageSize: instrumentPageSize,
                      total: instrumentTotal,
                      showSizeChanger: true,
                      showQuickJumper: true,
                      showTotal: total => `共 ${total} 条`,
                      onChange: (page, pageSize) => {
                        setInstrumentPage(page)
                        setInstrumentPageSize(pageSize)
                      },
                    }}
                  />
                </>
              ),
            },
            {
              key: 'records',
              label: '校准记录',
              children: (
                <>
                  {/* 筛选区域 */}
                  <Card size="small" style={{ marginBottom: 16 }}>
                    <Row gutter={16}>
                      <Col span={5}>
                        <Input
                          placeholder="校准单号"
                          value={recordFilters.calibration_no}
                          onChange={e => setRecordFilters({ ...recordFilters, calibration_no: e.target.value })}
                          allowClear
                        />
                      </Col>
                      <Col span={4}>
                        <Select
                          placeholder="校准方式"
                          value={recordFilters.calibration_method}
                          onChange={value => setRecordFilters({ ...recordFilters, calibration_method: value })}
                          allowClear
                          style={{ width: '100%' }}
                        >
                          {Object.entries(CalibrationMethod).map(([key, value]) => (
                            <Select.Option key={value} value={value}>
                              {CalibrationMethodLabels[value]}
                            </Select.Option>
                          ))}
                        </Select>
                      </Col>
                      <Col span={4}>
                        <Select
                          placeholder="校准结论"
                          value={recordFilters.calibration_result}
                          onChange={value => setRecordFilters({ ...recordFilters, calibration_result: value })}
                          allowClear
                          style={{ width: '100%' }}
                        >
                          {Object.entries(CalibrationResult).map(([key, value]) => (
                            <Select.Option key={value} value={value}>
                              {CalibrationResultLabels[value]}
                            </Select.Option>
                          ))}
                        </Select>
                      </Col>
                      <Col span={4}>
                        <Select
                          placeholder="状态"
                          value={recordFilters.status}
                          onChange={value => setRecordFilters({ ...recordFilters, status: value })}
                          allowClear
                          style={{ width: '100%' }}
                        >
                          {Object.entries(RecordStatus).map(([key, value]) => (
                            <Select.Option key={value} value={value}>
                              {RecordStatusLabels[value]}
                            </Select.Option>
                          ))}
                        </Select>
                      </Col>
                      <Col span={7}>
                        <Space>
                          <Button type="primary" onClick={loadRecords}>查询</Button>
                          <Button onClick={() => setRecordFilters(initialRecordFilter)}>重置</Button>
                          <Button type="primary" icon={<PlusOutlined />} onClick={handleCreateRecord}>新增校准记录</Button>
                        </Space>
                      </Col>
                    </Row>
                  </Card>

                  {/* 表格 */}
                  <Table
                    columns={recordColumns}
                    dataSource={recordData}
                    loading={loading}
                    rowKey="id"
                    scroll={{ x: 1300 }}
                    pagination={{
                      current: recordPage,
                      pageSize: recordPageSize,
                      total: recordTotal,
                      showSizeChanger: true,
                      showQuickJumper: true,
                      showTotal: total => `共 ${total} 条`,
                      onChange: (page, pageSize) => {
                        setRecordPage(page)
                        setRecordPageSize(pageSize)
                      },
                    }}
                  />
                </>
              ),
            },
          ]}
        />
      </Card>

      {/* 仪器新增/编辑弹窗 */}
      <Modal
        title={instrumentMode === 'create' ? '新增仪器' : '编辑仪器'}
        open={instrumentModalVisible}
        onOk={handleSaveInstrument}
        onCancel={() => setInstrumentModalVisible(false)}
        width={800}
        confirmLoading={submitLoading}
      >
        <Form
          form={instrumentMode === 'create' ? createForm : editForm}
          layout="vertical"
        >
          <Row gutter={16}>
            <Col span={8}>
              <Form.Item
                name="instrument_no"
                label="仪器编号"
                rules={[{ required: true, message: '请输入仪器编号' }]}
              >
                <Input disabled={instrumentMode === 'edit'} />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item
                name="instrument_name"
                label="仪器名称"
                rules={[{ required: true, message: '请输入仪器名称' }]}
              >
                <Input />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="model" label="型号">
                <Input />
              </Form.Item>
            </Col>
          </Row>
          <Row gutter={16}>
            <Col span={8}>
              <Form.Item name="serial_no" label="出厂编号">
                <Input />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="manufacturer" label="制造商">
                <Input />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="location" label="存放地点">
                <Input />
              </Form.Item>
            </Col>
          </Row>
          <Row gutter={16}>
            <Col span={8}>
              <Form.Item name="category" label="仪器分类">
                <Select allowClear>
                  {Object.entries(InstrumentCategory).map(([key, value]) => (
                    <Select.Option key={value} value={value}>
                      {InstrumentCategoryLabels[value]}
                    </Select.Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="manufacture_date" label="出厂日期">
                <DatePicker style={{ width: '100%' }} />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="responsible_name" label="使用负责人">
                <Input />
              </Form.Item>
            </Col>
          </Row>
          <Row gutter={16}>
            <Col span={8}>
              <Form.Item name="iq_status" label="IQ确认状态">
                <Select allowClear>
                  {Object.entries(IQStatus).map(([key, value]) => (
                    <Select.Option key={value} value={value}>
                      {IQStatusLabels[value]}
                    </Select.Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="iq_confirm_date" label="IQ确认日期">
                <DatePicker style={{ width: '100%' }} />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="oq_status" label="OQ确认状态">
                <Select allowClear>
                  {Object.entries(OQStatus).map(([key, value]) => (
                    <Select.Option key={value} value={value}>
                      {OQStatusLabels[value]}
                    </Select.Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
          </Row>
          <Row gutter={16}>
            <Col span={8}>
              <Form.Item name="oq_confirm_date" label="OQ确认日期">
                <DatePicker style={{ width: '100%' }} />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="is_active" label="是否启用" valuePropName="checked">
                <Radio.Group>
                  <Radio value={true}>是</Radio>
                  <Radio value={false}>否</Radio>
                </Radio.Group>
              </Form.Item>
            </Col>
          </Row>
          <Row gutter={16}>
            <Col span={24}>
              <Form.Item name="remark" label="备注">
                <TextArea rows={3} />
              </Form.Item>
            </Col>
          </Row>
        </Form>
      </Modal>

      {/* 仪器详情弹窗 */}
      <Modal
        title="仪器详情"
        open={instrumentViewVisible}
        onCancel={() => setInstrumentViewVisible(false)}
        footer={null}
        width={900}
      >
        {instrumentViewRecord && (
          <Descriptions column={3} bordered size="small">
            <Descriptions.Item label="仪器编号" span={1}>
              {instrumentViewRecord.instrument_no}
            </Descriptions.Item>
            <Descriptions.Item label="仪器名称" span={2}>
              {instrumentViewRecord.instrument_name}
            </Descriptions.Item>
            <Descriptions.Item label="型号" span={1}>
              {instrumentViewRecord.model || '-'}
            </Descriptions.Item>
            <Descriptions.Item label="出厂编号" span={2}>
              {instrumentViewRecord.serial_no || '-'}
            </Descriptions.Item>
            <Descriptions.Item label="制造商" span={2}>
              {instrumentViewRecord.manufacturer || '-'}
            </Descriptions.Item>
            <Descriptions.Item label="存放地点" span={1}>
              {instrumentViewRecord.location || '-'}
            </Descriptions.Item>
            <Descriptions.Item label="仪器分类" span={1}>
              {instrumentViewRecord.category ? InstrumentCategoryLabels[instrumentViewRecord.category] : '-'}
            </Descriptions.Item>
            <Descriptions.Item label="出厂日期" span={1}>
              {instrumentViewRecord.manufacture_date ? dayjs(instrumentViewRecord.manufacture_date).format('YYYY-MM-DD') : '-'}
            </Descriptions.Item>
            <Descriptions.Item label="使用负责人" span={1}>
              {instrumentViewRecord.responsible_name || '-'}
            </Descriptions.Item>
            <Descriptions.Item label="IQ确认状态" span={1}>
              {instrumentViewRecord.iq_status ? (
                <Tag color={IQStatusColors[instrumentViewRecord.iq_status]}>
                  {IQStatusLabels[instrumentViewRecord.iq_status]}
                </Tag>
              ) : '-'}
            </Descriptions.Item>
            <Descriptions.Item label="IQ确认日期" span={1}>
              {instrumentViewRecord.iq_confirm_date ? dayjs(instrumentViewRecord.iq_confirm_date).format('YYYY-MM-DD') : '-'}
            </Descriptions.Item>
            <Descriptions.Item label="OQ确认状态" span={1}>
              {instrumentViewRecord.oq_status ? (
                <Tag color={OQStatusColors[instrumentViewRecord.oq_status]}>
                  {OQStatusLabels[instrumentViewRecord.oq_status]}
                </Tag>
              ) : '-'}
            </Descriptions.Item>
            <Descriptions.Item label="OQ确认日期" span={1}>
              {instrumentViewRecord.oq_confirm_date ? dayjs(instrumentViewRecord.oq_confirm_date).format('YYYY-MM-DD') : '-'}
            </Descriptions.Item>
            <Descriptions.Item label="状态" span={1}>
              <Tag color={InstrumentStatusColors[instrumentViewRecord.status]}>
                {InstrumentStatusLabels[instrumentViewRecord.status]}
              </Tag>
            </Descriptions.Item>
            <Descriptions.Item label="是否启用" span={1}>
              {instrumentViewRecord.is_active ? '是' : '否'}
            </Descriptions.Item>
            <Descriptions.Item label="校准到期日期" span={1}>
              {instrumentViewRecord.next_calibration_date
                ? dayjs(instrumentViewRecord.next_calibration_date).format('YYYY-MM-DD')
                : '-'}
            </Descriptions.Item>
            <Descriptions.Item label="备注" span={3}>
              {instrumentViewRecord.remark || '-'}
            </Descriptions.Item>
          </Descriptions>
        )}

        {/* 校准规则列表 */}
        {instrumentViewRecord?.calibration_rules && instrumentViewRecord.calibration_rules.length > 0 && (
          <>
            <Divider>校准规则</Divider>
            <Table
              dataSource={instrumentViewRecord.calibration_rules}
              rowKey="id"
              size="small"
              pagination={false}
              columns={[
                { title: '校准方式', dataIndex: 'calibration_method', key: 'calibration_method',
                  render: (v: string) => CalibrationMethodLabels[v as CalibrationMethod] || v },
                { title: '校准周期', dataIndex: 'calibration_cycle', key: 'calibration_cycle',
                  render: (v: number, record) => v ? `${v} ${CalibrationCycleUnitLabels[record.calibration_unit as CalibrationCycleUnit] || ''}` : '-' },
                { title: '最近校准日期', dataIndex: 'last_calibration_date', key: 'last_calibration_date',
                  render: (v: string) => v ? dayjs(v).format('YYYY-MM-DD') : '-' },
                { title: '下次校准日期', dataIndex: 'next_calibration_date', key: 'next_calibration_date',
                  render: (v: string) => v ? dayjs(v).format('YYYY-MM-DD') : '-' },
                { title: '校准机构', dataIndex: 'calibration_agency', key: 'calibration_agency' },
                { title: '预警天数', dataIndex: 'warning_days', key: 'warning_days' },
                { title: '是否启用', dataIndex: 'is_active', key: 'is_active', render: (v: boolean) => v ? '是' : '否' },
                {
                  title: '操作',
                  key: 'action',
                  render: (_, record) => (
                    <Space size="small">
                      <Button type="link" size="small" onClick={() => handleOpenRuleModal(instrumentViewRecord!.id, record)}>
                        编辑
                      </Button>
                      <Popconfirm title="确定删除?" onConfirm={() => handleDeleteRule(record.id)}>
                        <Button type="link" size="small" danger>删除</Button>
                      </Popconfirm>
                    </Space>
                  ),
                },
              ]}
            />
          </>
        )}
      </Modal>

      {/* 校准规则弹窗 */}
      <Modal
        title={ruleMode === 'create' ? '新增校准规则' : '编辑校准规则'}
        open={ruleModalVisible}
        onOk={handleSaveRule}
        onCancel={() => setRuleModalVisible(false)}
        width={600}
        confirmLoading={submitLoading}
      >
        <Form form={ruleForm} layout="vertical">
          <Form.Item name="instrument_id" hidden>
            <Input />
          </Form.Item>
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="calibration_method"
                label="校准方式"
                rules={[{ required: true, message: '请选择校准方式' }]}
              >
                <Select>
                  {Object.entries(CalibrationMethod).map(([key, value]) => (
                    <Select.Option key={value} value={value}>
                      {CalibrationMethodLabels[value]}
                    </Select.Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="calibration_cycle" label="校准周期">
                <InputNumber style={{ width: '100%' }} min={1} />
              </Form.Item>
            </Col>
          </Row>
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item name="calibration_unit" label="周期单位">
                <Select allowClear>
                  {Object.entries(CalibrationCycleUnit).map(([key, value]) => (
                    <Select.Option key={value} value={value}>
                      {CalibrationCycleUnitLabels[value]}
                    </Select.Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="warning_days" label="提前预警天数">
                <InputNumber style={{ width: '100%' }} min={1} />
              </Form.Item>
            </Col>
          </Row>
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item name="last_calibration_date" label="最近校准日期">
                <DatePicker style={{ width: '100%' }} />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="next_calibration_date" label="下次校准日期">
                <DatePicker style={{ width: '100%' }} />
              </Form.Item>
            </Col>
          </Row>
          <Row gutter={16}>
            <Col span={24}>
              <Form.Item name="calibration_agency" label="校准机构">
                <Input />
              </Form.Item>
            </Col>
          </Row>
          <Row gutter={16}>
            <Col span={24}>
              <Form.Item name="agency_contact" label="机构联系方式">
                <Input />
              </Form.Item>
            </Col>
          </Row>
          <Row gutter={16}>
            <Col span={24}>
              <Form.Item name="internal_calibrator_name" label="内校人员">
                <Input />
              </Form.Item>
            </Col>
          </Row>
          <Row gutter={16}>
            <Col span={24}>
              <Form.Item name="is_active" label="是否启用" valuePropName="checked">
                <Radio.Group>
                  <Radio value={true}>是</Radio>
                  <Radio value={false}>否</Radio>
                </Radio.Group>
              </Form.Item>
            </Col>
          </Row>
        </Form>
      </Modal>

      {/* 校准记录新增/编辑弹窗 */}
      <Modal
        title={recordMode === 'create' ? '新增校准记录' : '编辑校准记录'}
        open={recordModalVisible}
        onOk={handleSaveRecord}
        onCancel={() => setRecordModalVisible(false)}
        width={800}
        confirmLoading={submitLoading}
      >
        <Form form={recordMode === 'create' ? recordForm : recordEditForm} layout="vertical">
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="instrument_id"
                label="关联仪器"
                rules={[{ required: true, message: '请选择仪器' }]}
              >
                <Select
                  showSearch
                  placeholder="请选择仪器"
                  optionFilterProp="children"
                  filterOption={(input, option) =>
                    (option?.children as any)?.toLowerCase().includes(input.toLowerCase())
                  }
                >
                  {instrumentData
                    .filter(i => i.is_active)
                    .map(instrument => (
                      <Select.Option key={instrument.id} value={instrument.id}>
                        {instrument.instrument_name} ({instrument.instrument_no})
                      </Select.Option>
                    ))}
                </Select>
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="calibration_date"
                label="校准日期"
                rules={[{ required: true, message: '请选择校准日期' }]}
              >
                <DatePicker style={{ width: '100%' }} />
              </Form.Item>
            </Col>
          </Row>
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="calibration_method"
                label="校准方式"
                rules={[{ required: true, message: '请选择校准方式' }]}
              >
                <Select>
                  {Object.entries(CalibrationMethod).map(([key, value]) => (
                    <Select.Option key={value} value={value}>
                      {CalibrationMethodLabels[value]}
                    </Select.Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="calibrator_name" label="校准人员">
                <Input />
              </Form.Item>
            </Col>
          </Row>
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item name="calibration_agency" label="校准机构">
                <Input />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="certificate_no" label="证书编号">
                <Input />
              </Form.Item>
            </Col>
          </Row>
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="calibration_result"
                label="校准结论"
                rules={[{ required: true, message: '请选择校准结论' }]}
              >
                <Select>
                  {Object.entries(CalibrationResult).map(([key, value]) => (
                    <Select.Option key={value} value={value}>
                      {CalibrationResultLabels[value]}
                    </Select.Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="result_reason" label="结论说明">
                <Input />
              </Form.Item>
            </Col>
          </Row>
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item name="valid_from" label="有效期起">
                <DatePicker style={{ width: '100%' }} />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="valid_until" label="有效期至">
                <DatePicker style={{ width: '100%' }} />
              </Form.Item>
            </Col>
          </Row>
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item name="is_scheduled" label="是否计划校准" valuePropName="checked">
                <Radio.Group>
                  <Radio value={false}>否</Radio>
                  <Radio value={true}>是</Radio>
                </Radio.Group>
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="scheduled_date" label="计划校准日期">
                <DatePicker style={{ width: '100%' }} />
              </Form.Item>
            </Col>
          </Row>
          <Row gutter={16}>
            <Col span={24}>
              <Form.Item name="remark" label="备注">
                <TextArea rows={3} />
              </Form.Item>
            </Col>
          </Row>
        </Form>
      </Modal>

      {/* 校准记录详情弹窗 */}
      <Modal
        title="校准记录详情"
        open={recordViewVisible}
        onCancel={() => setRecordViewVisible(false)}
        footer={null}
        width={800}
      >
        {recordViewRecord && (
          <Descriptions column={3} bordered size="small">
            <Descriptions.Item label="校准单号" span={1}>
              {recordViewRecord.calibration_no}
            </Descriptions.Item>
            <Descriptions.Item label="仪器编号" span={2}>
              {recordViewRecord.instrument_no || '-'}
            </Descriptions.Item>
            <Descriptions.Item label="仪器名称" span={3}>
              {recordViewRecord.instrument_name || '-'}
            </Descriptions.Item>
            <Descriptions.Item label="校准日期" span={1}>
              {recordViewRecord.calibration_date
                ? dayjs(recordViewRecord.calibration_date).format('YYYY-MM-DD')
                : '-'}
            </Descriptions.Item>
            <Descriptions.Item label="校准完成日期" span={1}>
              {recordViewRecord.calibration_end_date
                ? dayjs(recordViewRecord.calibration_end_date).format('YYYY-MM-DD')
                : '-'}
            </Descriptions.Item>
            <Descriptions.Item label="校准方式" span={1}>
              {CalibrationMethodLabels[recordViewRecord.calibration_method] || '-'}
            </Descriptions.Item>
            <Descriptions.Item label="校准机构" span={1}>
              {recordViewRecord.calibration_agency || '-'}
            </Descriptions.Item>
            <Descriptions.Item label="校准人员" span={1}>
              {recordViewRecord.calibrator_name || '-'}
            </Descriptions.Item>
            <Descriptions.Item label="证书编号" span={1}>
              {recordViewRecord.certificate_no || '-'}
            </Descriptions.Item>
            <Descriptions.Item label="校准结论" span={1}>
              <Tag color={CalibrationResultColors[recordViewRecord.calibration_result]}>
                {CalibrationResultLabels[recordViewRecord.calibration_result]}
              </Tag>
            </Descriptions.Item>
            <Descriptions.Item label="结论说明" span={1}>
              {recordViewRecord.result_reason || '-'}
            </Descriptions.Item>
            <Descriptions.Item label="有效期起" span={1}>
              {recordViewRecord.valid_from
                ? dayjs(recordViewRecord.valid_from).format('YYYY-MM-DD')
                : '-'}
            </Descriptions.Item>
            <Descriptions.Item label="有效期至" span={1}>
              {recordViewRecord.valid_until
                ? dayjs(recordViewRecord.valid_until).format('YYYY-MM-DD')
                : '-'}
            </Descriptions.Item>
            <Descriptions.Item label="状态" span={1}>
              <Tag color={RecordStatusColors[recordViewRecord.status]}>
                {RecordStatusLabels[recordViewRecord.status]}
              </Tag>
            </Descriptions.Item>
            <Descriptions.Item label="是否计划校准" span={1}>
              {recordViewRecord.is_scheduled ? '是' : '否'}
            </Descriptions.Item>
            <Descriptions.Item label="计划校准日期" span={1}>
              {recordViewRecord.scheduled_date
                ? dayjs(recordViewRecord.scheduled_date).format('YYYY-MM-DD')
                : '-'}
            </Descriptions.Item>
            <Descriptions.Item label="备注" span={3}>
              {recordViewRecord.remark || '-'}
            </Descriptions.Item>
          </Descriptions>
        )}
      </Modal>
    </div>
  )
}
