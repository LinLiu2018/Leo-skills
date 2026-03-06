import { useState } from 'react'
import {
  Card, Row, Col, Button, Switch, Tabs, List, Badge, Tag, Space,
  Slider, Input, Form, Select, Table, Progress, Statistic, Alert
} from 'antd'
import {
  RobotOutlined, PlayCircleOutlined, PauseCircleOutlined, SettingOutlined,
  CommentOutlined, EyeOutlined, LikeOutlined, UserAddOutlined,
  HistoryOutlined, ClockCircleOutlined, DashboardOutlined
} from '@ant-design/icons'

const { TabPane } = Tabs
const { TextArea } = Input
const { Option } = Select

// 自动化任务类型
const taskTypes = [
  {
    key: 'nurturing',
    name: '智能养号',
    icon: <EyeOutlined />,
    desc: '模拟真人浏览行为，提升账号活跃度',
    color: '#1677ff'
  },
  {
    key: 'intercept',
    name: '评论截流',
    icon: <CommentOutlined />,
    desc: '监控评论区关键词，自动回复获客',
    color: '#52c41a'
  },
  {
    key: 'customer',
    name: '自动获客',
    icon: <UserAddOutlined />,
    desc: '自动回复私信，引导用户留资',
    color: '#faad14'
  },
]

// 任务状态
const taskStatus = [
  { id: 1, name: '智能养号-抖音', type: 'nurturing', platform: 'douyin', status: 'running', progress: 65 },
  { id: 2, name: '评论截流-小红书', type: 'intercept', platform: 'xiaohongshu', status: 'running', progress: 42 },
  { id: 3, name: '自动获客-快手', type: 'customer', platform: 'kuaishou', status: 'paused', progress: 0 },
]

// 关键词设置
const defaultKeywords = ['怎么买', '多少钱', '联系方式', '加微信', '电话多少']

function AutoOperation() {
  const [activeTab, setActiveTab] = useState('nurturing')
  const [nurturingEnabled, setNurturingEnabled] = useState(false)
  const [interceptEnabled, setInterceptEnabled] = useState(false)
  const [customerEnabled, setCustomerEnabled] = useState(false)
  const [keywords, setKeywords] = useState(defaultKeywords)

  const columns = [
    {
      title: '任务名称',
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: '类型',
      dataIndex: 'type',
      key: 'type',
      render: (type: string) => {
        const config = taskTypes.find(t => t.key === type)
        return <Tag color={config?.color} icon={config?.icon}>{config?.name}</Tag>
      }
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => (
        <Badge status={status === 'running' ? 'processing' : 'default'} text={status === 'running' ? '运行中' : '已暂停'} />
      )
    },
    {
      title: '进度',
      dataIndex: 'progress',
      key: 'progress',
      render: (progress: number) => <Progress percent={progress} size="small" />
    },
    {
      title: '操作',
      key: 'action',
      render: (_: any, record: any) => (
        <Space>
          <Button
            type="text"
            icon={record.status === 'running' ? <PauseCircleOutlined /> : <PlayCircleOutlined />}
          >
            {record.status === 'running' ? '暂停' : '启动'}
          </Button>
          <Button type="text" icon={<SettingOutlined />}>设置</Button>
        </Space>
      )
    },
  ]

  return (
    <div className="auto-operation-page">
      <Row gutter={24}>
        {/* 左侧：功能模块 */}
        <Col span={16}>
          <Card>
            <Tabs activeKey={activeTab} onChange={setActiveTab}>
              {taskTypes.map(type => (
                <TabPane
                  tab={
                    <Space>
                      {type.icon}
                      {type.name}
                    </Space>
                  }
                  key={type.key}
                >
                  <div style={{ padding: '24px 0' }}>
                    {/* 功能开关 */}
                    <Card
                      style={{ marginBottom: 24, background: '#fafafa' }}
                      bodyStyle={{ padding: 24 }}
                    >
                      <Row align="middle" justify="space-between">
                        <Col>
                          <Space direction="vertical" size={4}>
                            <Space>
                              <span style={{ fontSize: 24, color: type.color }}>{type.icon}</span>
                              <span style={{ fontSize: 18, fontWeight: 500 }}>{type.name}</span>
                            </Space>
                            <span style={{ color: '#8c8c8c' }}>{type.desc}</span>
                          </Space>
                        </Col>
                        <Col>
                          <Switch
                            checked={
                              type.key === 'nurturing' ? nurturingEnabled :
                              type.key === 'intercept' ? interceptEnabled :
                              customerEnabled
                            }
                            onChange={(checked) => {
                              if (type.key === 'nurturing') setNurturingEnabled(checked)
                              if (type.key === 'intercept') setInterceptEnabled(checked)
                              if (type.key === 'customer') setCustomerEnabled(checked)
                            }}
                            checkedChildren="开启"
                            unCheckedChildren="关闭"
                            size="default"
                            style={{ width: 60 }}
                          />
                        </Col>
                      </Row>
                    </Card>

                    {/* 功能配置 */}
                    {type.key === 'nurturing' && nurturingEnabled && (
                      <Card title="养号设置" size="small">
                        <Form layout="vertical">
                          <Form.Item label="浏览时长范围（秒）">
                            <Slider range defaultValue={[3, 8]} min={1} max={30} marks={{ 1: '1s', 15: '15s', 30: '30s' }} />
                          </Form.Item>
                          <Form.Item label="点赞概率">
                            <Slider defaultValue={30} min={0} max={100} tipFormatter={(v) => `${v}%`} />
                          </Form.Item>
                          <Form.Item label="关注概率">
                            <Slider defaultValue={10} min={0} max={100} tipFormatter={(v) => `${v}%`} />
                          </Form.Item>
                          <Form.Item label="评论概率">
                            <Slider defaultValue={5} min={0} max={100} tipFormatter={(v) => `${v}%`} />
                          </Form.Item>
                        </Form>
                      </Card>
                    )}

                    {type.key === 'intercept' && interceptEnabled && (
                      <Card title="截流设置" size="small">
                        <Form layout="vertical">
                          <Form.Item label="监控关键词">
                            <Select mode="tags" style={{ width: '100%' }} placeholder="输入关键词按回车" defaultValue={keywords}>
                              {keywords.map(k => <Option key={k}>{k}</Option>)}
                            </Select>
                          </Form.Item>
                          <Form.Item label="自动回复话术">
                            <TextArea rows={4} placeholder="输入自动回复内容，支持变量如{username}"
                              defaultValue="Hi {username}，感谢关注！对房产感兴趣可以私信我了解更多详情~"
                            />
                          </Form.Item>
                          <Form.Item label="回复间隔（秒）">
                            <Slider defaultValue={30} min={5} max={300} marks={{ 5: '5s', 150: '150s', 300: '300s' }} />
                          </Form.Item>
                        </Form>
                      </Card>
                    )}

                    {type.key === 'customer' && customerEnabled && (
                      <Card title="客服设置" size="small">
                        <Form layout="vertical">
                          <Form.Item label="知识库选择">
                            <Select placeholder="选择知识库" defaultValue="default">
                              <Option value="default">默认房产知识库</Option>
                              <Option value="fapai">法拍房专用库</Option>
                              <Option value="shangye">商业投资库</Option>
                            </Select>
                          </Form.Item>
                          <Form.Item label="欢迎语">
                            <TextArea rows={3} defaultValue="您好！我是您的房产顾问，有什么可以帮助您的吗？" />
                          </Form.Item>
                          <Form.Item label="留资引导语">
                            <TextArea rows={3} defaultValue="方便的话留个联系方式，我发详细资料给您参考~" />
                          </Form.Item>
                        </Form>
                      </Card>
                    )}
                  </div>
                </TabPane>
              ))}
            </Tabs>
          </Card>
        </Col>

        {/* 右侧：任务列表和统计 */}
        <Col span={8}>
          <Card title="运行中任务">
            <Table
              dataSource={taskStatus}
              columns={columns}
              rowKey="id"
              pagination={false}
              size="small"
            />
          </Card>

          <Card style={{ marginTop: 16 }} title="今日统计">
            <Row gutter={[16, 16]}>
              <Col span={12}>
                <Statistic title="浏览视频" value={1258} prefix={<EyeOutlined />} />
              </Col>
              <Col span={12}>
                <Statistic title="点赞数" value={126} prefix={<LikeOutlined />} />
              </Col>
              <Col span={12}>
                <Statistic title="评论截流" value={38} prefix={<CommentOutlined />} />
              </Col>
              <Col span={12}>
                <Statistic title="新增客户" value={12} prefix={<UserAddOutlined />} />
              </Col>
            </Row>
          </Card>

          <Alert
            message="安全提示"
            description="自动化操作会模拟真人行为，建议合理设置操作频率，避免触发平台风控。"
            type="info"
            showIcon
            style={{ marginTop: 16 }}
          />
        </Col>
      </Row>
    </div>
  )
}

export default AutoOperation
