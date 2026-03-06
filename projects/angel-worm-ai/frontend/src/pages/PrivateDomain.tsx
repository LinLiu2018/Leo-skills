import { useState } from 'react'
import {
  Card, Row, Col, Button, List, Avatar, Badge, Tag, Space, Tabs,
  Form, Input, Switch, Select, Table, Modal, message, Statistic
} from 'antd'
import {
  WechatOutlined, UserAddOutlined, ClockCircleOutlined, SendOutlined,
  CommentOutlined, HeartOutlined, EditOutlined, DeleteOutlined,
  PlusOutlined, SettingOutlined, TeamOutlined, MessageOutlined
} from '@ant-design/icons'

const { TextArea } = Input
const { TabPane } = Tabs
const { Option } = Select

// 好友申请数据
const friendRequests = [
  { id: 1, nickname: '张先生', avatar: '', source: '抖音私信', message: '想了解宁波别墅', time: '2分钟前', status: 'pending' },
  { id: 2, nickname: '李女士', avatar: '', source: '视频号', message: '法拍房咨询', time: '5分钟前', status: 'pending' },
  { id: 3, nickname: '王先生', avatar: '', source: '小红书', message: '商业投资', time: '10分钟前', status: 'accepted' },
]

// 朋友圈数据
const moments = [
  { id: 1, content: '今日推荐：鄞州区独栋别墅，带花园，价格美丽', images: 3, likes: 28, comments: 5, time: '1小时前' },
  { id: 2, content: '法拍房避坑指南，新手必看！', images: 6, likes: 45, comments: 12, time: '3小时前' },
]

// 自动任务状态
const autoTasks = [
  { id: 1, name: '自动通过好友', status: true, count: 12 },
  { id: 2, name: '自动回复欢迎语', status: true, count: 45 },
  { id: 3, name: '自动点赞朋友圈', status: false, count: 0 },
  { id: 4, name: '定时发布朋友圈', status: true, count: 3 },
]

function PrivateDomain() {
  const [activeTab, setActiveTab] = useState('friends')
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [form] = Form.useForm()

  const columns = [
    { title: '任务名称', dataIndex: 'name', key: 'name' },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status: boolean) => (
        <Switch checked={status} size="small" />
      )
    },
    {
      title: '今日执行',
      dataIndex: 'count',
      key: 'count',
      render: (count: number) => <Badge count={count} style={{ backgroundColor: '#52c41a' }} />
    },
  ]

  const handlePublishMoment = (values: any) => {
    console.log('发布朋友圈:', values)
    message.success('朋友圈任务已创建')
    setIsModalOpen(false)
    form.resetFields()
  }

  return (
    <div className="private-domain-page">
      <Row gutter={24}>
        <Col span={16}>
          <Card>
            <Tabs activeKey={activeTab} onChange={setActiveTab}>
              <TabPane
                tab={<Space><UserAddOutlined />好友管理</Space>}
                key="friends"
              >
                <List
                  dataSource={friendRequests}
                  renderItem={item => (
                    <List.Item
                      actions={[
                        item.status === 'pending' && (
                          <Space>
                            <Button type="primary" size="small">通过</Button>
                            <Button size="small">忽略</Button>
                          </Space>
                        ),
                        item.status === 'accepted' && <Tag color="success">已通过</Tag>
                      ]}
                    >
                      <List.Item.Meta
                        avatar={<Avatar>{item.nickname[0]}</Avatar>}
                        title={
                          <Space>
                            <span>{item.nickname}</span>
                            <Tag size="small">{item.source}</Tag>
                          </Space>
                        }
                        description={
                          <Space direction="vertical" size={0}>
                            <span>验证消息: {item.message}</span>
                            <span style={{ fontSize: 12, color: '#8c8c8c' }}>{item.time}</span>
                          </Space>
                        }
                      />
                    </List.Item>
                  )}
                />
              </TabPane>

              <TabPane
                tab={<Space><WechatOutlined />朋友圈管理</Space>}
                key="moments"
              >
                <Button
                  type="primary"
                  icon={<PlusOutlined />}
                  onClick={() => setIsModalOpen(true)}
                  style={{ marginBottom: 16 }}
                >
                  发布朋友圈
                </Button>

                <List
                  dataSource={moments}
                  renderItem={item => (
                    <Card style={{ marginBottom: 16 }}>
                      <div style={{ marginBottom: 12 }}>{item.content}</div>
                      <div style={{ color: '#8c8c8c', fontSize: 12, marginBottom: 12 }}>
                        {item.images}张图片 · {item.time}
                      </div>
                      <Space>
                        <Button type="text" icon={<HeartOutlined />}>{item.likes}</Button>
                        <Button type="text" icon={<CommentOutlined />}>{item.comments}</Button>
                        <Button type="text" icon={<EditOutlined />}>编辑</Button>
                        <Button type="text" danger icon={<DeleteOutlined />}>删除</Button>
                      </Space>
                    </Card>
                  )}
                />
              </TabPane>

              <TabPane
                tab={<Space><MessageOutlined />消息管理</Space>}
                key="messages"
              >
                <Card title="快捷回复设置">
                  <Form layout="vertical">
                    <Form.Item label="欢迎语">
                      <TextArea
                        rows={3}
                        defaultValue="您好！我是您的房产顾问Leo，有什么可以帮您的吗？"
                      />
                    </Form.Item>
                    <Form.Item label="咨询回复">
                      <TextArea
                        rows={3}
                        defaultValue="感谢您的咨询！我们的项目位置优越，投资回报率高。需要详细资料吗？"
                      />
                    </Form.Item>
                    <Form.Item label="留资引导">
                      <TextArea
                        rows={3}
                        defaultValue="方便的话留个电话或微信，我发详细资料给您参考~"
                      />
                    </Form.Item>
                    <Button type="primary">保存设置</Button>
                  </Form>
                </Card>
              </TabPane>
            </Tabs>
          </Card>
        </Col>

        <Col span={8}>
          <Card title="私域数据统计">
            <Row gutter={[16, 16]}>
              <Col span={12}>
                <Statistic title="今日新增好友" value={12} prefix={<UserAddOutlined />} />
              </Col>
              <Col span={12}>
                <Statistic title="好友总数" value={2580} prefix={<TeamOutlined />} />
              </Col>
              <Col span={12}>
                <Statistic title="今日互动" value={86} prefix={<CommentOutlined />} />
              </Col>
              <Col span={12}>
                <Statistic title="转化率" value={3.2} suffix="%" />
              </Col>
            </Row>
          </Card>

          <Card style={{ marginTop: 16 }} title="自动化任务">
            <Table
              dataSource={autoTasks}
              columns={columns}
              rowKey="id"
              pagination={false}
              size="small"
            />
          </Card>
        </Col>
      </Row>

      <Modal
        title="发布朋友圈"
        open={isModalOpen}
        onOk={() => form.submit()}
        onCancel={() => setIsModalOpen(false)}
        width={600}
      >
        <Form form={form} layout="vertical" onFinish={handlePublishMoment}>
          <Form.Item
            name="content"
            label="内容"
            rules={[{ required: true, message: '请输入朋友圈内容' }]}
          >
            <TextArea rows={4} placeholder="分享点什么..." />
          </Form.Item>
          <Form.Item name="images" label="图片">
            <div style={{ border: '1px dashed #d9d9d9', padding: 20, textAlign: 'center' }}>
              <PlusOutlined /> 上传图片
            </div>
          </Form.Item>
          <Form.Item name="schedule" label="定时发布">
            <Switch /> 启用定时发布
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}

export default PrivateDomain
