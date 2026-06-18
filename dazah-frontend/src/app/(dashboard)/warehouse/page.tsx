'use client'

/**
 * 试剂/标准品管理页面
 *
 * 功能说明：
 * - 试剂/标准品台账管理
 * - 领用申请（含AI辅助生成事由）
 * - 报废申请（含AI辅助生成报废原因）
 * - GMP合规要求
 */

import React, { useState, useEffect } from 'react'
import {
  Table,
  Button,
  Modal,
  Form,
  Input,
  Select,
  DatePicker,
  Space,
  Tag,
  Card,
  Row,
  Col,
  message,
  Popconfirm,
  Divider,
  Tooltip,
  InputNumber,
  Alert,
  Tabs,
} from 'antd'
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  CheckOutlined,
  CloseOutlined,
  SearchOutlined,
  RobotOutlined,
  ExclamationCircleOutlined,
} from '@ant-design/icons'
import type { ColumnsType } from 'antd/es/table'
import dayjs from 'dayjs'
import {
  Reagent,
  ReagentUsage,
  ReagentScrap,
  statusLabels,
  usageReasonLabels,
  scrapTypeLabels,
} from '@/types/warehouse'
import * as reagentActions from '@/actions/warehouse'

const { TextArea } = Input
const { RangePicker } = DatePicker

// 模拟当前登录用户（后续接入真实认证）
const CURRENT_USER = 'admin'

// ============ 试剂台账列表 ============
interface ReagentInventoryTabProps {
  onUsageClick: (record: Reagent) => void
  onScrapClick: (record: Reagent) => void
  onAnalyseClick: (record: Reagent) => void
}

const ReagentInventoryTab: React.FC<ReagentInventoryTabProps> = ({ onUsageClick, onScrapClick, onAnalyseClick }) => {
  const [loading, setLoading] = useState(false)
  const [data, setData] = useState<Reagent[]>([])
  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 20,
    total: 0,
  })
  const [searchForm] = Form.useForm()

  const fetchData = async (values?: any) => {
    setLoading(true)
    try {
      const result = await reagentActions.getReagentInventory({
        keyword: values?.keyword,
        status: values?.status,
        page: pagination.current,
        page_size: pagination.pageSize,
      })
      const responseData = result.data || result
      setData(responseData.items || [])
      setPagination((prev) => ({
        ...prev,
        total: responseData.total || 0,
      }))
    } catch (error: any) {
      message.error(error.message || '获取数据失败')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchData()
  }, [pagination.current, pagination.pageSize])

  const columns: ColumnsType<Reagent> = [
    {
      title: '试剂编号',
      dataIndex: 'reagent_no',
      width: 120,
    },
    {
      title: '试剂名称',
      dataIndex: 'reagent_name',
      width: 150,
    },
    {
      title: '规格',
      dataIndex: 'specification',
      width: 100,
    },
    {
      title: '批号',
      dataIndex: 'lot_no',
      width: 100,
    },
    {
      title: '库存数量',
      dataIndex: 'quantity',
      width: 100,
      render: (val, record) => `${val} ${record.unit}`,
    },
    {
      title: '有效期',
      dataIndex: 'expiration_date',
      width: 120,
      render: (date) =>
        date ? (
          dayjs(date).isBefore(dayjs()) ? (
            <Tag color="red">已过期</Tag>
          ) : (
            dayjs(date).format('YYYY-MM-DD')
          )
        ) : (
          '-'
        ),
    },
    {
      title: '状态',
      dataIndex: 'status',
      width: 100,
      render: (status) => {
        const colorMap: Record<string, string> = {
          available: 'green',
          low_stock: 'orange',
          expired: 'red',
          quarantine: 'blue',
        }
        return <Tag color={colorMap[status] || 'default'}>{statusLabels[status] || status}</Tag>
      },
    },
    {
      title: '操作',
      key: 'action',
      width: 220,
      fixed: 'right',
      render: (_, record) => (
        <Space size="small">
          <Button
            type="link"
            size="small"
            icon={<CheckOutlined />}
            onClick={() => onUsageClick(record)}
          >
            领用
          </Button>
          <Button
            type="link"
            size="small"
            icon={<CloseOutlined />}
            onClick={() => onScrapClick(record)}
          >
            报废
          </Button>
          <Tooltip title="AI异常分析">
            <Button
              type="link"
              size="small"
              icon={<RobotOutlined />}
              onClick={() => onAnalyseClick(record)}
            />
          </Tooltip>
        </Space>
      ),
    },
  ]

  return (
    <div>
      <Card size="small" style={{ marginBottom: 16 }}>
        <Form form={searchForm} layout="inline" onFinish={fetchData}>
          <Form.Item name="keyword" label="关键词">
            <Input placeholder="试剂名称/编号" style={{ width: 160 }} />
          </Form.Item>
          <Form.Item name="status" label="状态">
            <Select allowClear placeholder="选择状态" style={{ width: 120 }}>
              <Select.Option value="available">库存充足</Select.Option>
              <Select.Option value="low_stock">库存不足</Select.Option>
              <Select.Option value="expired">已过期</Select.Option>
              <Select.Option value="quarantine">待验</Select.Option>
            </Select>
          </Form.Item>
          <Form.Item>
            <Space>
              <Button type="primary" icon={<SearchOutlined />} htmlType="submit">
                查询
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Card>

      <Table
        columns={columns}
        dataSource={data}
        rowKey="id"
        loading={loading}
        pagination={{
          ...pagination,
          showSizeChanger: true,
          showQuickJumper: true,
          showTotal: (total) => `共 ${total} 条`,
          onChange: (page, pageSize) =>
            setPagination({ current: page, pageSize, total: pagination.total }),
        }}
      />
    </div>
  )
}

// ============ 试剂领用弹窗 ============
interface UsageModalProps {
  visible: boolean
  reagent: Reagent | null
  onClose: () => void
  onSuccess: () => void
}

const UsageModal: React.FC<UsageModalProps> = ({
  visible,
  reagent,
  onClose,
  onSuccess,
}) => {
  const [form] = Form.useForm()
  const [loading, setLoading] = useState(false)
  const [aiLoading, setAiLoading] = useState(false)

  useEffect(() => {
    if (visible && reagent) {
      form.setFieldsValue({
        reagent_id: reagent.id,
        reagent_name: reagent.reagent_name,
        quantity: 1,
      })
    }
  }, [visible, reagent, form])

  const handleAiGenerateReason = async () => {
    const userInput = form.getFieldValue('user_input') || ''
    if (!userInput.trim()) {
      message.warning('请先填写试剂用途描述')
      return
    }

    setAiLoading(true)
    try {
      const billNo = `USAGE-${dayjs().format('YYYYMMDDHHmmss')}`
      const result = await reagentActions.generateUsageReason(
        billNo,
        userInput,
        CURRENT_USER
      )

      if (result.code === 200) {
        form.setFieldValue('usage_reason', result.data.result)
        message.success('AI已生成领用事由，已回填至输入框')
      } else {
        message.error(result.message || 'AI服务异常，请手动填写')
      }
    } catch (error: any) {
      console.error('AI生成领用事由失败:', error)
      message.error('AI服务异常，请手动填写')
    } finally {
      setAiLoading(false)
    }
  }

  const handleSubmit = async () => {
    try {
      const values = await form.validateFields()
      setLoading(true)

      await reagentActions.createReagentUsage(values)
      message.success('领用申请已提交')
      form.resetFields()
      onSuccess()
      onClose()
    } catch (error: any) {
      if (error.errorFields) {
        message.warning('请完善必填信息')
      } else {
        message.error(error.message || '提交失败')
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <Modal
      title="试剂领用申请"
      open={visible}
      onCancel={onClose}
      onOk={handleSubmit}
      width={650}
      confirmLoading={loading}
      destroyOnClose
    >
      <Form
        form={form}
        layout="vertical"
        initialValues={{
          usage_date: dayjs(),
          usage_reason: '',
        }}
      >
        <Row gutter={16}>
          <Col span={12}>
            <Form.Item name="reagent_name" label="试剂名称">
              <Input disabled value={reagent?.reagent_name} />
            </Form.Item>
          </Col>
          <Col span={12}>
            <Form.Item name="reagent_no" label="试剂编号">
              <Input disabled value={reagent?.reagent_no} />
            </Form.Item>
          </Col>
        </Row>

        <Row gutter={16}>
          <Col span={12}>
            <Form.Item name="quantity" label="领用数量" rules={[{ required: true }]}>
              <InputNumber
                min={1}
                max={reagent?.quantity || 999}
                style={{ width: '100%' }}
                addonAfter={reagent?.unit || 'g'}
              />
            </Form.Item>
          </Col>
          <Col span={12}>
            <Form.Item name="usage_date" label="领用日期" rules={[{ required: true }]}>
              <DatePicker style={{ width: '100%' }} />
            </Form.Item>
          </Col>
        </Row>

        <Row gutter={16}>
          <Col span={24}>
            <Form.Item name="user_input" label="试剂用途描述（用于AI辅助生成）">
              <TextArea
                rows={2}
                placeholder="请描述试剂的用途，如：用于高效液相色谱法检测某产品的含量"
              />
            </Form.Item>
          </Col>
        </Row>

        <Row gutter={16}>
          <Col span={24}>
            <Form.Item
              name="usage_reason"
              label={
                <Space>
                  领用事由
                  <Button
                    type="link"
                    size="small"
                    icon={<RobotOutlined />}
                    loading={aiLoading}
                    onClick={handleAiGenerateReason}
                    style={{
                      color: '#1890ff',
                      fontWeight: 'normal',
                    }}
                  >
                    AI生成事由
                  </Button>
                </Space>
              }
              rules={[{ required: true }]}
            >
              <TextArea rows={3} placeholder="请输入或使用AI生成领用事由" />
            </Form.Item>
          </Col>
        </Row>

        <Divider style={{ margin: '12px 0' }} />

        {/* GMP合规提示 */}
        <div
          style={{
            color: '#999',
            fontSize: 12,
            textAlign: 'center',
          }}
        >
          <ExclamationCircleOutlined style={{ marginRight: 4 }} />
          AI内容仅作参考，最终以人工审核确认
        </div>
      </Form>
    </Modal>
  )
}

// ============ 试剂报废弹窗 ============
interface ScrapModalProps {
  visible: boolean
  reagent: Reagent | null
  onClose: () => void
  onSuccess: () => void
}

const ScrapModal: React.FC<ScrapModalProps> = ({
  visible,
  reagent,
  onClose,
  onSuccess,
}) => {
  const [form] = Form.useForm()
  const [loading, setLoading] = useState(false)
  const [aiLoading, setAiLoading] = useState(false)

  useEffect(() => {
    if (visible && reagent) {
      form.setFieldsValue({
        reagent_id: reagent.id,
        reagent_name: reagent.reagent_name,
        quantity: reagent.quantity,
        scrap_type: 'expired',
      })
    }
  }, [visible, reagent, form])

  const handleAiGenerateScrap = async () => {
    const userInput = form.getFieldValue('user_input') || ''
    if (!userInput.trim()) {
      message.warning('请先填写报废情况描述')
      return
    }

    setAiLoading(true)
    try {
      const billNo = `SCRAP-${dayjs().format('YYYYMMDDHHmmss')}`
      const result = await reagentActions.generateScrapReason(
        billNo,
        userInput,
        CURRENT_USER
      )

      if (result.code === 200) {
        form.setFieldValue('scrap_reason', result.data.result)
        message.success('AI已生成报废原因，已回填至输入框')
      } else {
        message.error(result.message || 'AI服务异常，请手动填写')
      }
    } catch (error: any) {
      console.error('AI生成报废原因失败:', error)
      message.error('AI服务异常，请手动填写')
    } finally {
      setAiLoading(false)
    }
  }

  const handleSubmit = async () => {
    try {
      const values = await form.validateFields()
      setLoading(true)

      await reagentActions.createReagentScrap(values)
      message.success('报废申请已提交')
      form.resetFields()
      onSuccess()
      onClose()
    } catch (error: any) {
      if (error.errorFields) {
        message.warning('请完善必填信息')
      } else {
        message.error(error.message || '提交失败')
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <Modal
      title="试剂报废申请"
      open={visible}
      onCancel={onClose}
      onOk={handleSubmit}
      width={650}
      confirmLoading={loading}
      destroyOnClose
    >
      <Form
        form={form}
        layout="vertical"
        initialValues={{
          scrap_date: dayjs(),
          scrap_reason: '',
        }}
      >
        <Row gutter={16}>
          <Col span={12}>
            <Form.Item name="reagent_name" label="试剂名称">
              <Input disabled value={reagent?.reagent_name} />
            </Form.Item>
          </Col>
          <Col span={12}>
            <Form.Item name="reagent_no" label="试剂编号">
              <Input disabled value={reagent?.reagent_no} />
            </Form.Item>
          </Col>
        </Row>

        <Row gutter={16}>
          <Col span={12}>
            <Form.Item name="quantity" label="报废数量" rules={[{ required: true }]}>
              <InputNumber
                min={1}
                max={reagent?.quantity || 999}
                style={{ width: '100%' }}
                addonAfter={reagent?.unit || 'g'}
              />
            </Form.Item>
          </Col>
          <Col span={12}>
            <Form.Item name="scrap_date" label="报废日期" rules={[{ required: true }]}>
              <DatePicker style={{ width: '100%' }} />
            </Form.Item>
          </Col>
        </Row>

        <Row gutter={16}>
          <Col span={12}>
            <Form.Item name="scrap_type" label="报废类型" rules={[{ required: true }]}>
              <Select>
                <Select.Option value="expired">过期报废</Select.Option>
                <Select.Option value="damaged">破损报废</Select.Option>
                <Select.Option value="contaminated">污染报废</Select.Option>
                <Select.Option value="other">其他</Select.Option>
              </Select>
            </Form.Item>
          </Col>
        </Row>

        <Row gutter={16}>
          <Col span={24}>
            <Form.Item name="user_input" label="报废情况描述（用于AI辅助生成）">
              <TextArea
                rows={2}
                placeholder="请描述试剂的报废情况，如：试剂已过期，剩余量较少无法继续使用"
              />
            </Form.Item>
          </Col>
        </Row>

        <Row gutter={16}>
          <Col span={24}>
            <Form.Item
              name="scrap_reason"
              label={
                <Space>
                  报废原因
                  <Button
                    type="link"
                    size="small"
                    icon={<RobotOutlined />}
                    loading={aiLoading}
                    onClick={handleAiGenerateScrap}
                    style={{
                      color: '#1890ff',
                      fontWeight: 'normal',
                    }}
                  >
                    AI生成报废原因
                  </Button>
                </Space>
              }
              rules={[{ required: true }]}
            >
              <TextArea rows={3} placeholder="请输入或使用AI生成报废原因" />
            </Form.Item>
          </Col>
        </Row>

        <Divider style={{ margin: '12px 0' }} />

        {/* GMP合规提示 */}
        <div
          style={{
            color: '#999',
            fontSize: 12,
            textAlign: 'center',
          }}
        >
          <ExclamationCircleOutlined style={{ marginRight: 4 }} />
          AI内容仅作参考，最终以人工审核确认
        </div>
      </Form>
    </Modal>
  )
}

// ============ 领用记录列表 ============
const UsageTab: React.FC = () => {
  const [loading, setLoading] = useState(false)
  const [data, setData] = useState<ReagentUsage[]>([])
  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 20,
    total: 0,
  })

  const fetchData = async () => {
    setLoading(true)
    try {
      const result = await reagentActions.getReagentUsages({
        page: pagination.current,
        page_size: pagination.pageSize,
      })
      const responseData = result.data || result
      setData(responseData.items || [])
      setPagination((prev) => ({
        ...prev,
        total: responseData.total || 0,
      }))
    } catch (error: any) {
      message.error(error.message || '获取数据失败')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchData()
  }, [])

  const columns: ColumnsType<ReagentUsage> = [
    {
      title: '单据编号',
      dataIndex: 'reagent_no',
      width: 150,
    },
    {
      title: '试剂名称',
      dataIndex: 'reagent_name',
      width: 150,
    },
    {
      title: '领用数量',
      dataIndex: 'quantity',
      width: 100,
      render: (val, record) => `${val} ${record.unit}`,
    },
    {
      title: '领用日期',
      dataIndex: 'usage_date',
      width: 120,
      render: (date) => (date ? dayjs(date).format('YYYY-MM-DD') : '-'),
    },
    {
      title: '领用事由',
      dataIndex: 'usage_reason',
      ellipsis: true,
    },
    {
      title: '状态',
      dataIndex: 'status',
      width: 100,
      render: (status) => {
        const colorMap: Record<string, string> = {
          draft: 'default',
          submitted: 'processing',
          approved: 'success',
        }
        return (
          <Tag color={colorMap[status] || 'default'}>
            {statusLabels[status] || status}
          </Tag>
        )
      },
    },
  ]

  return (
    <div>
      <Alert
        message="试剂领用说明"
        description="试剂领用需遵循GMP物料管理规范，填写规范的事由说明。系统提供AI辅助生成合规领用事由功能。"
        type="info"
        showIcon
        style={{ marginBottom: 16 }}
      />

      <Table
        columns={columns}
        dataSource={data}
        rowKey="id"
        loading={loading}
        pagination={{
          ...pagination,
          showTotal: (total) => `共 ${total} 条`,
          onChange: (page, pageSize) =>
            setPagination({ current: page, pageSize, total: pagination.total }),
        }}
      />
    </div>
  )
}

// ============ 报废记录列表 ============
const ScrapTab: React.FC = () => {
  const [loading, setLoading] = useState(false)
  const [data, setData] = useState<ReagentScrap[]>([])
  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 20,
    total: 0,
  })

  const fetchData = async () => {
    setLoading(true)
    try {
      const result = await reagentActions.getReagentScraps({
        page: pagination.current,
        page_size: pagination.pageSize,
      })
      const responseData = result.data || result
      setData(responseData.items || [])
      setPagination((prev) => ({
        ...prev,
        total: responseData.total || 0,
      }))
    } catch (error: any) {
      message.error(error.message || '获取数据失败')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchData()
  }, [])

  const columns: ColumnsType<ReagentScrap> = [
    {
      title: '单据编号',
      dataIndex: 'reagent_no',
      width: 150,
    },
    {
      title: '试剂名称',
      dataIndex: 'reagent_name',
      width: 150,
    },
    {
      title: '报废数量',
      dataIndex: 'quantity',
      width: 100,
      render: (val, record) => `${val} ${record.unit}`,
    },
    {
      title: '报废日期',
      dataIndex: 'scrap_date',
      width: 120,
      render: (date) => (date ? dayjs(date).format('YYYY-MM-DD') : '-'),
    },
    {
      title: '报废类型',
      dataIndex: 'scrap_type',
      width: 100,
      render: (type) => scrapTypeLabels[type] || type,
    },
    {
      title: '报废原因',
      dataIndex: 'scrap_reason',
      ellipsis: true,
    },
    {
      title: '状态',
      dataIndex: 'status',
      width: 100,
      render: (status) => {
        const colorMap: Record<string, string> = {
          draft: 'default',
          submitted: 'processing',
          approved: 'success',
        }
        return (
          <Tag color={colorMap[status] || 'default'}>
            {statusLabels[status] || status}
          </Tag>
        )
      },
    },
  ]

  return (
    <div>
      <Alert
        message="试剂报废说明"
        description="试剂报废需符合实验室台账管理要求，填写规范的报废原因。系统提供AI辅助生成标准报废原因功能。"
        type="info"
        showIcon
        style={{ marginBottom: 16 }}
      />

      <Table
        columns={columns}
        dataSource={data}
        rowKey="id"
        loading={loading}
        pagination={{
          ...pagination,
          showTotal: (total) => `共 ${total} 条`,
          onChange: (page, pageSize) =>
            setPagination({ current: page, pageSize, total: pagination.total }),
        }}
      />
    </div>
  )
}

// ============ 试剂异常分析弹窗 ============
interface AnalyseModalProps {
  visible: boolean
  reagent: Reagent | null
  onClose: () => void
}

const AnalyseModal: React.FC<AnalyseModalProps> = ({
  visible,
  reagent,
  onClose,
}) => {
  const [form] = Form.useForm()
  const [loading, setLoading] = useState(false)
  const [aiLoading, setAiLoading] = useState(false)
  const [aiResult, setAiResult] = useState<string>('')

  useEffect(() => {
    if (visible && reagent) {
      form.setFieldsValue({
        reagent_name: reagent.reagent_name,
        reagent_no: reagent.reagent_no,
        storage_conditions: reagent.storage_conditions || '',
        quantity: reagent.quantity,
        unit: reagent.unit,
      })
      setAiResult('')
    }
  }, [visible, reagent, form])

  const handleAiAnalyse = async () => {
    const problemDescription = form.getFieldValue('problem_description') || ''
    if (!problemDescription.trim()) {
      message.warning('请先填写问题描述')
      return
    }

    setAiLoading(true)
    setAiResult('')
    try {
      const billNo = `ANALYSE-${dayjs().format('YYYYMMDDHHmmss')}`
      const result = await reagentActions.generateAnalyse(
        billNo,
        reagent?.reagent_name || '',
        problemDescription,
        form.getFieldValue('storage_conditions') || '',
        CURRENT_USER
      )

      if (result.code === 200) {
        setAiResult(result.data.result)
        message.success('AI分析完成')
      } else {
        message.error(result.message || 'AI服务异常')
      }
    } catch (error: any) {
      console.error('AI分析失败:', error)
      message.error('AI服务异常，请稍后重试')
    } finally {
      setAiLoading(false)
    }
  }

  return (
    <Modal
      title="试剂异常分析"
      open={visible}
      onCancel={onClose}
      footer={[
        <Button key="close" onClick={onClose}>
          关闭
        </Button>,
      ]}
      width={700}
      destroyOnClose
    >
      <Form
        form={form}
        layout="vertical"
      >
        <Row gutter={16}>
          <Col span={12}>
            <Form.Item name="reagent_name" label="试剂名称">
              <Input disabled />
            </Form.Item>
          </Col>
          <Col span={12}>
            <Form.Item name="reagent_no" label="试剂编号">
              <Input disabled />
            </Form.Item>
          </Col>
        </Row>

        <Row gutter={16}>
          <Col span={12}>
            <Form.Item name="storage_conditions" label="储存条件">
              <Input disabled placeholder="来自试剂台账" />
            </Form.Item>
          </Col>
          <Col span={12}>
            <Form.Item name="quantity" label="当前库存">
              <Input disabled />
            </Form.Item>
          </Col>
        </Row>

        <Row gutter={16}>
          <Col span={24}>
            <Form.Item
              name="problem_description"
              label={
                <Space>
                  问题描述
                  <Tag color="orange">必填</Tag>
                </Space>
              }
              extra="描述观察到的异常情况，如：近效期、变色、结块、储存温度异常等"
            >
              <TextArea
                rows={3}
                placeholder="请描述观察到的问题，如：试剂有效期至2024年6月，还有15天到期，外观正常但需关注"
              />
            </Form.Item>
          </Col>
        </Row>

        <Divider />

        <Row gutter={16}>
          <Col span={24}>
            <Form.Item label={
              <Space>
                AI分析结果
                <Button
                  type="primary"
                  icon={<RobotOutlined />}
                  loading={aiLoading}
                  onClick={handleAiAnalyse}
                  size="small"
                >
                  AI分析
                </Button>
              </Space>
            }>
              <div
                style={{
                  background: aiResult ? '#f6ffed' : '#f5f5f5',
                  padding: 16,
                  borderRadius: 4,
                  minHeight: 150,
                  whiteSpace: 'pre-wrap',
                  border: aiResult ? '1px solid #b7eb8f' : '1px dashed #d9d9d9',
                }}
              >
                {aiLoading ? (
                  <span style={{ color: '#999' }}>AI分析中，请稍候...</span>
                ) : aiResult || (
                  <span style={{ color: '#999' }}>
                    点击"AI分析"按钮，系统将基于GMP实验室物料管控要求，
                    分析潜在原因并给出临时处置措施和长期预防管理建议。
                  </span>
                )}
              </div>
            </Form.Item>
          </Col>
        </Row>

        <Divider style={{ margin: '12px 0' }} />

        {/* GMP合规提示 */}
        <Alert
          message="GMP合规说明"
          description="AI分析结果仅供人工参考，需质量人员综合评估后确定处置方案并执行。AI不参与任何业务决策。"
          type="info"
          showIcon
        />
      </Form>
    </Modal>
  )
}

// ============ 主页面组件 ============
export default function ReagentPage() {
  const [activeTab, setActiveTab] = useState('inventory')
  const [usageModalVisible, setUsageModalVisible] = useState(false)
  const [scrapModalVisible, setScrapModalVisible] = useState(false)
  const [analyseModalVisible, setAnalyseModalVisible] = useState(false)
  const [selectedReagent, setSelectedReagent] = useState<Reagent | null>(null)

  const handleOpenUsageModal = (record: Reagent) => {
    setSelectedReagent(record)
    setUsageModalVisible(true)
  }

  const handleOpenScrapModal = (record: Reagent) => {
    setSelectedReagent(record)
    setScrapModalVisible(true)
  }

  const handleOpenAnalyseModal = (record: Reagent) => {
    setSelectedReagent(record)
    setAnalyseModalVisible(true)
  }

  const handleSuccess = () => {
    // 刷新数据
    window.location.reload()
  }

  const tabItems = [
    {
      key: 'inventory',
      label: '试剂台账',
      children: <ReagentInventoryTab onUsageClick={handleOpenUsageModal} onScrapClick={handleOpenScrapModal} onAnalyseClick={handleOpenAnalyseModal} />,
    },
    {
      key: 'usage',
      label: '领用记录',
      children: <UsageTab />,
    },
    {
      key: 'scrap',
      label: '报废记录',
      children: <ScrapTab />,
    },
  ]

  return (
    <div style={{ padding: 24 }}>
      <Card
        title="试剂/标准品管理"
        extra={
          <Space>
            <Button
              type="primary"
              icon={<PlusOutlined />}
              onClick={() => message.info('新建功能开发中')}
            >
              新建试剂
            </Button>
          </Space>
        }
      >
        <Tabs activeKey={activeTab} onChange={setActiveTab} items={tabItems} />
      </Card>

      {/* 领用弹窗 */}
      <UsageModal
        visible={usageModalVisible}
        reagent={selectedReagent}
        onClose={() => {
          setUsageModalVisible(false)
          setSelectedReagent(null)
        }}
        onSuccess={handleSuccess}
      />

      {/* 报废弹窗 */}
      <ScrapModal
        visible={scrapModalVisible}
        reagent={selectedReagent}
        onClose={() => {
          setScrapModalVisible(false)
          setSelectedReagent(null)
        }}
        onSuccess={handleSuccess}
      />

      {/* 异常分析弹窗 */}
      <AnalyseModal
        visible={analyseModalVisible}
        reagent={selectedReagent}
        onClose={() => {
          setAnalyseModalVisible(false)
          setSelectedReagent(null)
        }}
      />
    </div>
  )
}