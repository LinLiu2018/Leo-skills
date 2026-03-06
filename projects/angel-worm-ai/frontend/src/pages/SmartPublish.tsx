import { useState } from 'react'
import type { Dayjs } from 'dayjs'
import {
  Card, Calendar, Button, Tag, List, Avatar, Badge, Space, Modal,
  Form, Input, Select, TimePicker, DatePicker, Checkbox, message, Tabs, Row, Col, Statistic
} from 'antd'
import {
  ScheduleOutlined, PlusOutlined, EditOutlined, DeleteOutlined,
  PlayCircleOutlined, PauseCircleOutlined, CheckCircleOutlined,
  ClockCircleOutlined, VideoCameraOutlined, SendOutlined
} from '@ant-design/icons'
import type { Dayjs } from 'dayjs'
import dayjs from 'dayjs'

const { TextArea } = Input
const { Option } = Select
const { TabPane } = Tabs

// 发布计划数据
const publishPlans = [
  { id: 1, title: '宁波别墅推荐', platforms: ['douyin', 'kuaishou'], time: '09:00', status: 'pending', date: '2026-03-03' },
  { id: 2, title: '法拍房避坑指南', platforms: ['xiaohongshu'], time: '12:00', status: 'published', date: '2026-03-02' },
  { id: 3, title: '商业投资分析', platforms: ['shipinhao', 'douyin'], time: '18:00', status: 'pending', date: '2026-03-04' },
]

// 平台选项
const platformOptions = [
  { value: 'douyin', label: '抖音', color: '#000' },
  { value: 'kuaishou', label: '快手', color: '#FF6B00' },
  { value: 'shipinhao', label: '视频号', color: '#07C160' },
  { value: 'xiaohongshu', label: '小红书', color: '#FF2442' },
]

function SmartPublish() {
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [form] = Form.useForm()
  const [selectedDate, setSelectedDate] = useState<Dayjs>(dayjs())

  const handleAddPlan = (values: any) => {
    console.log('添加发布计划:', values)
    message.success('发布计划已创建')
    setIsModalOpen(false)
    form.resetFields()
  }

  // 日历单元格渲染
  const dateCellRender = (value: Dayjs) => {
    const dateStr = value.format('YYYY-MM-DD')
    const dayPlans = publishPlans.filter(p => p.date === dateStr)

    return (
      <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
        {dayPlans.map(plan => (
          <li key={plan.id}>
            <Badge
              status={plan.status === 'published' ? 'success' : 'processing'}
              text={<span style={{ fontSize: 12 }}>{plan.time} {plan.title}</span>}
            />
          </li>
        ))}
      </ul>
    )
  }

  return (
    <div className="smart-publish-page">
      <Row gutter={24}>
        {/* 左侧：日历视图 */}
        <Col span={16}>
          <Card
            title={
              <Space>
                <ScheduleOutlined />
                <span>发布日历</span>
              </Space>
            }
            extra={
              <Space>
                <Button icon={<PlayCircleOutlined />}>批量发布</Button>
                <Button type="primary" icon={<PlusOutlined />} onClick={() => setIsModalOpen(true)}>
                  新建计划
                </Button>
              </Space>
            }
          >
            <Calendar
              value={selectedDate}
              onChange={setSelectedDate}
              dateCellRender={dateCellRender}
            />
          </Card>
        </Col>

        {/* 右侧：计划列表 */}
        <Col span={8}>
          <Card
            title={
              <Space>
                <ClockCircleOutlined />
                <span>今日计划</span>
              </Space>
            }
          >
            <List
              dataSource={publishPlans}
              renderItem={item => (
                <List.Item
                  actions={[
                    <Button type="text" icon={<EditOutlined />} size="small" />,
                    <Button type="text" icon={<DeleteOutlined />} size="small" danger />,
                  ]}
                >
                  <List.Item.Meta
                    avatar={
                      <Avatar shape="square" style={{ backgroundColor: '#1677ff' }}>
                        <VideoCameraOutlined />
                      </Avatar>
                    }
                    title={
                      <div>
                        <span style={{ fontWeight: 500 }}>{item.title}</span>
                        <Tag
                          color={item.status === 'published' ? 'success' : 'processing'}
                          style={{ marginLeft: 8 }}
                        >
                          {item.status === 'published' ? '已发布' : '待发布'}
                        </Tag>
                      </div>
                    }
                    description={
                      <Space direction="vertical" size={0}>
                        <span style={{ fontSize: 12, color: '#8c8c8c' }}>
                          发布时间: {item.time}
                        </span>
                        <Space size={4}>
                          {item.platforms.map(p => {
                            const platform = platformOptions.find(o => o.value === p)
                            return (
                              <Tag key={p} color={platform?.color} style={{ fontSize: 10 }}>
                                {platform?.label}
                              </Tag>
                            )
                          })}
                        </Space>
                      </Space>
                    }
                  />
                </List.Item>
              )}
            />
          </Card>

          {/* 发布统计 */}
          <Card style={{ marginTop: 16 }}>
            <Row gutter={16}>
              <Col span={8}>
                <Statistic title="今日发布" value={3} />
              </Col>
              <Col span={8}>
                <Statistic title="本周发布" value={18} />
              </Col>
              <Col span={8}>
                <Statistic title="成功率" value={98} suffix="%" />
              </Col>
            </Row>
          </Card>
        </Col>
      </Row>

      {/* 新建计划弹窗 */}
      <Modal
        title="新建发布计划"
        open={isModalOpen}
        onOk={() => form.submit()}
        onCancel={() => setIsModalOpen(false)}
        width={600}
      >
        <Form form={form} layout="vertical" onFinish={handleAddPlan}>
          <Form.Item
            name="title"
            label="内容标题"
            rules={[{ required: true, message: '请输入内容标题' }]}
          >
            <Input placeholder="输入视频标题" />
          </Form.Item>

          <Form.Item
            name="platforms"
            label="发布平台"
            rules={[{ required: true, message: '请选择发布平台' }]}
          >
            <Checkbox.Group options={platformOptions} />
          </Form.Item>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="date"
                label="发布日期"
                rules={[{ required: true, message: '请选择日期' }]}
              >
                <DatePicker style={{ width: '100%' }} />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="time"
                label="发布时间"
                rules={[{ required: true, message: '请选择时间' }]}
              >
                <TimePicker style={{ width: '100%' }} format="HH:mm" />
              </Form.Item>
            </Col>
          </Row>

          <Form.Item
            name="description"
            label="内容描述"
          >
            <TextArea rows={3} placeholder="补充描述信息（可选）" />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}

export default SmartPublish
