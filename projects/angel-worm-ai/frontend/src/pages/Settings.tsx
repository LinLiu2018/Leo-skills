import { useState } from 'react'
import {
  Card, Tabs, Form, Input, Button, Switch, Select, Slider, Upload,
  List, Avatar, Tag, Space, Divider, Alert, message, Modal
} from 'antd'
import {
  UserOutlined, LockOutlined, NotificationOutlined, DatabaseOutlined,
  ApiOutlined, SafetyOutlined, InfoCircleOutlined, UploadOutlined,
  SaveOutlined, KeyOutlined, GlobalOutlined, MobileOutlined
} from '@ant-design/icons'

const { TabPane } = Tabs
const { TextArea } = Input
const { Option } = Select

// 第三方API配置
const apiConfigs = [
  { id: 1, name: 'Sora 2 API', type: 'video', status: 'connected', key: 'sk-***1234' },
  { id: 2, name: 'DeepSeek API', type: 'llm', status: 'connected', key: 'sk-***5678' },
  { id: 3, name: 'HeyGem 本地', type: 'avatar', status: 'disconnected', key: '-' },
]

// 平台配置
const platformConfigs = [
  { id: 1, platform: 'douyin', name: '抖音', accounts: 12, enabled: true },
  { id: 2, platform: 'kuaishou', name: '快手', accounts: 8, enabled: true },
  { id: 3, platform: 'shipinhao', name: '视频号', accounts: 6, enabled: true },
  { id: 4, platform: 'xiaohongshu', name: '小红书', accounts: 5, enabled: false },
]

function Settings() {
  const [form] = Form.useForm()
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [currentApi, setCurrentApi] = useState<typeof apiConfigs[0] | null>(null)

  const handleSaveProfile = (values: any) => {
    console.log('保存个人信息:', values)
    message.success('个人信息已保存')
  }

  const handleSaveNotification = (values: any) => {
    console.log('保存通知设置:', values)
    message.success('通知设置已保存')
  }

  const handleConnectApi = (api: typeof apiConfigs[0]) => {
    setCurrentApi(api)
    setIsModalOpen(true)
  }

  return (
    <div className="settings-page">
      <Tabs type="card">
        <TabPane
          tab={<Space><UserOutlined />个人设置</Space>}
          key="profile"
        >
          <Card title="基本信息">
            <Form form={form} layout="vertical" onFinish={handleSaveProfile}>
              <Form.Item label="头像">
                <Upload name="avatar" listType="picture-circle" showUploadList={false}>
                  <div>
                    <UploadOutlined />
                    <div style={{ marginTop: 8 }}>上传</div>
                  </div>
                </Upload>
              </Form.Item>
              <Form.Item name="nickname" label="昵称" rules={[{ required: true }]}>
                <Input prefix={<UserOutlined />} placeholder="输入昵称" />
              </Form.Item>
              <Form.Item name="email" label="邮箱">
                <Input prefix={<GlobalOutlined />} placeholder="输入邮箱" />
              </Form.Item>
              <Form.Item name="phone" label="手机号">
                <Input prefix={<MobileOutlined />} placeholder="输入手机号" />
              </Form.Item>
              <Form.Item>
                <Button type="primary" icon={<SaveOutlined />} htmlType="submit">
                  保存修改
                </Button>
              </Form.Item>
            </Form>
          </Card>

          <Card title="修改密码" style={{ marginTop: 24 }}>
            <Form layout="vertical">
              <Form.Item name="oldPassword" label="当前密码">
                <Input.Password prefix={<LockOutlined />} placeholder="输入当前密码" />
              </Form.Item>
              <Form.Item name="newPassword" label="新密码">
                <Input.Password prefix={<LockOutlined />} placeholder="输入新密码" />
              </Form.Item>
              <Form.Item name="confirmPassword" label="确认新密码">
                <Input.Password prefix={<LockOutlined />} placeholder="再次输入新密码" />
              </Form.Item>
              <Form.Item>
                <Button type="primary">修改密码</Button>
              </Form.Item>
            </Form>
          </Card>
        </TabPane>

        <TabPane
          tab={<Space><ApiOutlined />API配置</Space>}
          key="api"
        >
          <Card title="AI服务配置">
            <List
              dataSource={apiConfigs}
              renderItem={item => (
                <List.Item
                  actions={[
                    <Button
                      type={item.status === 'connected' ? 'default' : 'primary'}
                      onClick={() => handleConnectApi(item)}
                    >
                      {item.status === 'connected' ? '重新配置' : '连接'}
                    </Button>
                  ]}
                >
                  <List.Item.Meta
                    avatar={
                      <Avatar style={{ backgroundColor: item.status === 'connected' ? '#52c41a' : '#f5222d' }}>
                        <ApiOutlined />
                      </Avatar>
                    }
                    title={item.name}
                    description={
                      <Space>
                        <Tag>{item.type.toUpperCase()}</Tag>
                        <Tag color={item.status === 'connected' ? 'success' : 'error'}>
                          {item.status === 'connected' ? '已连接' : '未连接'}
                        </Tag>
                        <span>API Key: {item.key}</span>
                      </Space>
                    }
                  />
                </List.Item>
              )}
            />
          </Card>

          <Card title="平台配置" style={{ marginTop: 24 }}>
            <List
              dataSource={platformConfigs}
              renderItem={item => (
                <List.Item
                  actions={[
                    <Switch checked={item.enabled} />,
                    <Button type="text">配置</Button>
                  ]}
                >
                  <List.Item.Meta
                    title={
                      <Space>
                        <span>{item.name}</span>
                        <Tag>{item.accounts}个账号</Tag>
                      </Space>
                    }
                    description={`平台状态: ${item.enabled ? '已启用' : '已禁用'}`}
                  />
                </List.Item>
              )}
            />
          </Card>
        </TabPane>

        <TabPane
          tab={<Space><NotificationOutlined />通知设置</Space>}
          key="notification"
        >
          <Card title="消息通知">
            <Form layout="vertical" onFinish={handleSaveNotification}>
              <Form.Item label="系统通知">
                <Switch defaultChecked />
              </Form.Item>
              <Form.Item label="任务完成通知">
                <Switch defaultChecked />
              </Form.Item>
              <Form.Item label="异常告警">
                <Switch defaultChecked />
              </Form.Item>
              <Form.Item label="每日数据报告">
                <Switch />
              </Form.Item>
              <Form.Item>
                <Button type="primary" icon={<SaveOutlined />} htmlType="submit">
                  保存设置
                </Button>
              </Form.Item>
            </Form>
          </Card>
        </TabPane>

        <TabPane
          tab={<Space><SafetyOutlined />安全与风控</Space>}
          key="security"
        >
          <Card title="风控策略">
            <Alert
              message="安全提示"
              description="合理的操作间隔和随机行为可以有效降低触发平台风控的概率。"
              type="info"
              showIcon
              style={{ marginBottom: 24 }}
            />
            <Form layout="vertical">
              <Form.Item label="操作间隔随机范围（秒）">
                <Slider range defaultValue={[5, 15]} min={1} max={60} />
              </Form.Item>
              <Form.Item label="单日最大操作次数">
                <Slider defaultValue={100} min={10} max={500} />
              </Form.Item>
              <Form.Item label="启用设备指纹模拟">
                <Switch defaultChecked />
              </Form.Item>
              <Form.Item label="启用IP代理池">
                <Switch />
              </Form.Item>
              <Form.Item label="行为随机化">
                <Switch defaultChecked />
              </Form.Item>
              <Form.Item>
                <Button type="primary">保存风控策略</Button>
              </Form.Item>
            </Form>
          </Card>
        </TabPane>

        <TabPane
          tab={<Space><DatabaseOutlined />存储与缓存</Space>}
          key="storage"
        >
          <Card title="存储管理">
            <List>
              <List.Item
                actions={[<Button>清理</Button>]}
              >
                <List.Item.Meta
                  title="临时文件"
                  description="占用空间: 1.2GB"
                />
              </List.Item>
              <List.Item
                actions={[<Button>清理</Button>]}
              >
                <List.Item.Meta
                  title="生成视频缓存"
                  description="占用空间: 3.5GB"
                />
              </List.Item>
              <List.Item
                actions={[<Button>清理</Button>]}
              >
                <List.Item.Meta
                  title="日志文件"
                  description="占用空间: 256MB"
                />
              </List.Item>
            </List>
            <Divider />
            <Button type="primary" danger>一键清理所有缓存</Button>
          </Card>
        </TabPane>

        <TabPane
          tab={<Space><InfoCircleOutlined />关于</Space>}
          key="about"
        >
          <Card style={{ textAlign: 'center', padding: '48px 0' }}>
            <div style={{ fontSize: 48, marginBottom: 16 }}>🤖</div>
            <h2>天使虫AI操盘手系统</h2>
            <p style={{ color: '#8c8c8c', marginTop: 16 }}>版本: 1.0.0 (Build 2026.03.02)</p>
            <p style={{ color: '#8c8c8c' }}>全链路AI数字员工操作系统</p>
            <Divider />
            <Space>
              <Button>检查更新</Button>
              <Button>查看文档</Button>
              <Button>反馈问题</Button>
            </Space>
            <Divider />
            <p style={{ fontSize: 12, color: '#bfbfbf' }}>
              Copyright © 2026 天使虫AI. All rights reserved.
            </p>
          </Card>
        </TabPane>
      </Tabs>

      {/* API配置弹窗 */}
      <Modal
        title={`配置 ${currentApi?.name}`}
        open={isModalOpen}
        onOk={() => setIsModalOpen(false)}
        onCancel={() => setIsModalOpen(false)}
      >
        <Form layout="vertical">
          <Form.Item label="API Key" required>
            <Input.Password prefix={<KeyOutlined />} placeholder="输入API Key" />
          </Form.Item>
          <Form.Item label="Base URL">
            <Input placeholder="可选，自定义API地址" />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}

export default Settings
