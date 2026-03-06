import { useState } from 'react'
import {
  Card, Button, Table, Tag, Avatar, Space, Input, Dropdown, Modal,
  Form, Select, message, Row, Col, Statistic, Tabs
} from 'antd'
import {
  PlusOutlined, SearchOutlined, MoreOutlined, EditOutlined,
  DeleteOutlined, SyncOutlined, CheckCircleOutlined, ExclamationCircleOutlined,
  CloseCircleOutlined, DesktopOutlined, MobileOutlined
} from '@ant-design/icons'

const { TabPane } = Tabs
const { Option } = Select

// 平台配置
const platforms = [
  { key: 'douyin', name: '抖音', color: '#000000' },
  { key: 'kuaishou', name: '快手', color: '#FF6B00' },
  { key: 'shipinhao', name: '视频号', color: '#07C160' },
  { key: 'xiaohongshu', name: '小红书', color: '#FF2442' },
  { key: 'weixin', name: '微信', color: '#07C160' },
]

// 模拟账号数据
const mockAccounts = [
  { id: 1, platform: 'douyin', nickname: 'Leo说房', avatar: '', fans: 128000, status: 'online', device: 'phone', lastActive: '2分钟前' },
  { id: 2, platform: 'douyin', nickname: '宁波房产观察', avatar: '', fans: 85000, status: 'online', device: 'phone', lastActive: '5分钟前' },
  { id: 3, platform: 'kuaishou', nickname: '宁波法拍房', avatar: '', fans: 45000, status: 'warning', device: 'emulator', lastActive: '1小时前' },
  { id: 4, platform: 'xiaohongshu', nickname: 'Leo看房日记', avatar: '', fans: 23000, status: 'online', device: 'phone', lastActive: '10分钟前' },
  { id: 5, platform: 'shipinhao', nickname: '宁波豪宅推荐', avatar: '', fans: 56000, status: 'offline', device: 'phone', lastActive: '2小时前' },
]

function AccountMatrix() {
  const [searchText, setSearchText] = useState('')
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [form] = Form.useForm()

  // 状态标签
  const statusTags = {
    online: { color: 'success', icon: <CheckCircleOutlined />, text: '在线' },
    offline: { color: 'default', icon: <CloseCircleOutlined />, text: '离线' },
    warning: { color: 'warning', icon: <ExclamationCircleOutlined />, text: '警告' },
    error: { color: 'error', icon: <CloseCircleOutlined />, text: '异常' },
  }

  const columns = [
    {
      title: '账号信息',
      dataIndex: 'nickname',
      key: 'nickname',
      render: (text: string, _record: any) => (
        <Space>
          <Avatar src={record.avatar} style={{ backgroundColor: platforms.find(p => p.key === record.platform)?.color }}>
            {text[0]}
          </Avatar>
          <div>
            <div style={{ fontWeight: 500 }}>{text}</div>
            <div style={{ fontSize: 12, color: '#8c8c8c' }}>
              {platforms.find(p => p.key === record.platform)?.name}
            </div>
          </div>
        </Space>
      ),
    },
    {
      title: '粉丝数',
      dataIndex: 'fans',
      key: 'fans',
      render: (fans: number) => (fans / 10000).toFixed(1) + '万',
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status: keyof typeof statusTags) => {
        const config = statusTags[status]
        return <Tag icon={config.icon} color={config.color}>{config.text}</Tag>
      },
    },
    {
      title: '设备',
      dataIndex: 'device',
      key: 'device',
      render: (device: string) => (
        <Tag icon={device === 'phone' ? <MobileOutlined /> : <DesktopOutlined />}>
          {device === 'phone' ? '真机' : '模拟器'}
        </Tag>
      ),
    },
    {
      title: '最后活跃',
      dataIndex: 'lastActive',
      key: 'lastActive',
    },
    {
      title: '操作',
      key: 'action',
      render: (_: any, _record: any) => (
        <Space>
          <Button type="text" icon={<EditOutlined />} size="small">编辑</Button>
          <Dropdown menu={{
            items: [
              { key: '1', label: '同步数据', icon: <SyncOutlined /> },
              { key: '2', label: '查看详情', icon: <DesktopOutlined /> },
              { key: '3', label: '删除', icon: <DeleteOutlined />, danger: true },
            ]
          }}>
            <Button type="text" icon={<MoreOutlined />} size="small" />
          </Dropdown>
        </Space>
      ),
    },
  ]

  const handleAddAccount = (values: any) => {
    console.log('添加账号:', values)
    message.success('账号添加成功')
    setIsModalOpen(false)
    form.resetFields()
  }

  return (
    <div className="account-matrix-page">
      <Card
        title="账号矩阵管理"
        extra={
          <Space>
            <Input
              placeholder="搜索账号"
              prefix={<SearchOutlined />}
              value={searchText}
              onChange={(e) => setSearchText(e.target.value)}
              style={{ width: 200 }}
            />
            <Button type="primary" icon={<PlusOutlined />} onClick={() => setIsModalOpen(true)}>
              添加账号
            </Button>
          </Space>
        }
      >
        {/* 统计概览 */}
        <Row gutter={16} style={{ marginBottom: 24 }}>
          <Col span={6}>
            <Statistic title="总账号数" value={128} />
          </Col>
          <Col span={6}>
            <Statistic title="在线账号" value={98} valueStyle={{ color: '#52c41a' }} />
          </Col>
          <Col span={6}>
            <Statistic title="总粉丝数" value={2580000} formatter={(v) => (Number(v) / 10000).toFixed(1) + '万'} />
          </Col>
          <Col span={6}>
            <Statistic title="异常账号" value={3} valueStyle={{ color: '#f5222d' }} />
          </Col>
        </Row>

        {/* 平台标签页 */}
        <Tabs defaultActiveKey="all">
          <TabPane tab="全部平台" key="all">
            <Table
              columns={columns}
              dataSource={mockAccounts}
              rowKey="id"
              pagination={{ pageSize: 10 }}
            />
          </TabPane>
          {platforms.map(p => (
            <TabPane tab={p.name} key={p.key}>
              <Table
                columns={columns}
                dataSource={mockAccounts.filter(a => a.platform === p.key)}
                rowKey="id"
                pagination={{ pageSize: 10 }}
              />
            </TabPane>
          ))}
        </Tabs>
      </Card>

      {/* 添加账号弹窗 */}
      <Modal
        title="添加新账号"
        open={isModalOpen}
        onOk={() => form.submit()}
        onCancel={() => setIsModalOpen(false)}
        width={500}
      >
        <Form form={form} layout="vertical" onFinish={handleAddAccount}>
          <Form.Item
            name="platform"
            label="所属平台"
            rules={[{ required: true, message: '请选择平台' }]}
          >
            <Select placeholder="选择平台">
              {platforms.map(p => (
                <Option key={p.key} value={p.key}>{p.name}</Option>
              ))}
            </Select>
          </Form.Item>
          <Form.Item
            name="nickname"
            label="账号昵称"
            rules={[{ required: true, message: '请输入账号昵称' }]}
          >
            <Input placeholder="输入账号昵称" />
          </Form.Item>
          <Form.Item
            name="accountId"
            label="账号ID"
            rules={[{ required: true, message: '请输入账号ID' }]}
          >
            <Input placeholder="输入账号ID或手机号" />
          </Form.Item>
          <Form.Item
            name="device"
            label="设备类型"
            rules={[{ required: true, message: '请选择设备类型' }]}
          >
            <Select placeholder="选择设备类型">
              <Option value="phone">真机</Option>
              <Option value="emulator">模拟器</Option>
            </Select>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}

export default AccountMatrix
