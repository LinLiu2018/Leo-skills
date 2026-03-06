import { useState, useRef, useEffect } from 'react'
import {
  Card, Input, Button, List, Avatar, Space, Typography, Badge,
  Timeline, Row, Col
} from 'antd'
import {
  SendOutlined, AudioOutlined, RobotOutlined, UserOutlined,
  LoadingOutlined, CheckCircleOutlined, CloseCircleOutlined
} from '@ant-design/icons'

const { TextArea } = Input
const { Text } = Typography

// 快捷指令
const quickCommands = [
  { id: 1, name: '生成房产视频', icon: '🎬', prompt: '帮我做一个关于宁波别墅的视频' },
  { id: 2, name: '监控竞品账号', icon: '👀', prompt: '监控抖音账号"XXX"最近10条视频数据' },
  { id: 3, name: '批量发布内容', icon: '🚀', prompt: '将最新视频发布到所有平台' },
  { id: 4, name: '获取客户线索', icon: '👥', prompt: '把评论区要买的人都加到微信' },
  { id: 5, name: '生成爆款文案', icon: '✍️', prompt: '帮我写5个房产视频的爆款标题' },
  { id: 6, name: '数据分析报告', icon: '📊', prompt: '生成本周运营数据分析报告' },
]

// 消息类型
interface Message {
  id: number
  type: 'user' | 'ai'
  content: string
  timestamp: Date
  status?: 'thinking' | 'executing' | 'completed' | 'error'
  steps?: TaskStep[]
}

interface TaskStep {
  id: number
  name: string
  status: 'pending' | 'running' | 'completed' | 'error'
  detail?: string
}

function AICommand() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 0,
      type: 'ai',
      content: '您好！我是天使虫AI操盘手，请输入您的指令，我将自动为您完成复杂的运营任务。',
      timestamp: new Date(),
    }
  ])
  const [inputValue, setInputValue] = useState('')
  const [isProcessing, setIsProcessing] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  // 自动滚动到底部
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSend = async () => {
    if (!inputValue.trim()) return

    const userMessage: Message = {
      id: messages.length,
      type: 'user',
      content: inputValue,
      timestamp: new Date(),
    }

    setMessages(prev => [...prev, userMessage])
    setInputValue('')
    setIsProcessing(true)

    // 模拟AI处理过程
    await simulateAIResponse(userMessage.content)
  }

  const simulateAIResponse = async (userInput: string) => {
    // 步骤1: 思考中
    const thinkingMessage: Message = {
      id: messages.length + 1,
      type: 'ai',
      content: '正在理解您的指令...',
      timestamp: new Date(),
      status: 'thinking',
      steps: [
        { id: 1, name: '解析指令意图', status: 'running' },
        { id: 2, name: '拆解任务步骤', status: 'pending' },
        { id: 3, name: '执行任务', status: 'pending' },
      ]
    }
    setMessages(prev => [...prev, thinkingMessage])

    await delay(1500)

    // 步骤2: 任务拆解完成
    const executingMessage: Message = {
      ...thinkingMessage,
      content: `收到指令："${userInput}"，已拆解为以下任务：`,
      status: 'executing',
      steps: [
        { id: 1, name: '解析指令意图', status: 'completed', detail: '识别为：内容生成+多平台发布任务' },
        { id: 2, name: '生成视频内容', status: 'running', detail: '调用Sora 2 API生成视频...' },
        { id: 3, name: '配置发布计划', status: 'pending' },
        { id: 4, name: '执行矩阵发布', status: 'pending' },
      ]
    }
    setMessages(prev => prev.map(m => m.id === thinkingMessage.id ? executingMessage : m))

    await delay(3000)

    // 步骤3: 任务完成
    const completedMessage: Message = {
      ...executingMessage,
      content: '任务执行完成！已成功生成视频并配置发布计划。',
      status: 'completed',
      steps: [
        { id: 1, name: '解析指令意图', status: 'completed', detail: '识别为：内容生成+多平台发布任务' },
        { id: 2, name: '生成视频内容', status: 'completed', detail: '视频生成成功，时长45秒' },
        { id: 3, name: '配置发布计划', status: 'completed', detail: '已配置4个平台定时发布' },
        { id: 4, name: '执行矩阵发布', status: 'completed', detail: '发布任务已提交' },
      ]
    }
    setMessages(prev => prev.map(m => m.id === thinkingMessage.id ? completedMessage : m))
    setIsProcessing(false)
  }

  const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms))

  const handleQuickCommand = (command: typeof quickCommands[0]) => {
    setInputValue(command.prompt)
  }

  return (
    <div className="ai-command-page" style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Row gutter={24} style={{ flex: 1, overflow: 'hidden' }}>
        {/* 左侧：快捷指令 */}
        <Col span={5} style={{ height: '100%' }}>
          <Card title="快捷指令" style={{ height: '100%', overflow: 'auto' }}>
            <List
              dataSource={quickCommands}
              renderItem={item => (
                <List.Item
                  style={{ cursor: 'pointer', padding: '12px 0' }}
                  onClick={() => handleQuickCommand(item)}
                >
                  <Space>
                    <span style={{ fontSize: 20 }}>{item.icon}</span>
                    <span>{item.name}</span>
                  </Space>
                </List.Item>
              )}
            />
          </Card>
        </Col>

        {/* 中间：对话区 */}
        <Col span={13} style={{ height: '100%' }}>
          <Card
            title={
              <Space>
                <RobotOutlined />
                <span>AI指令控制台</span>
                <Badge status="processing" text="运行中" />
              </Space>
            }
            style={{ height: '100%', display: 'flex', flexDirection: 'column' }}
            bodyStyle={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden', padding: 0 }}
          >
            {/* 消息列表 */}
            <div style={{ flex: 1, overflow: 'auto', padding: '16px 24px' }}>
              <List
                dataSource={messages}
                renderItem={msg => (
                  <List.Item style={{ justifyContent: msg.type === 'user' ? 'flex-end' : 'flex-start', border: 'none' }}>
                    <Space align="start" style={{ maxWidth: '80%' }}>
                      {msg.type === 'ai' && (
                        <Avatar style={{ backgroundColor: '#1677ff' }}><RobotOutlined /></Avatar>
                      )}
                      <div>
                        <Card
                          size="small"
                          style={{
                            backgroundColor: msg.type === 'user' ? '#1677ff' : '#f5f5f5',
                            color: msg.type === 'user' ? '#fff' : '#262626',
                            border: 'none'
                          }}
                          bodyStyle={{ padding: '12px 16px' }}
                        >
                          <Text style={{ color: 'inherit' }}>{msg.content}</Text>
                        </Card>

                        {/* 任务步骤显示 */}
                        {msg.steps && (
                          <Card size="small" style={{ marginTop: 12, background: '#fafafa' }}>
                            <Timeline mode="left" style={{ margin: 0 }}>
                              {msg.steps.map(step => (
                                <Timeline.Item
                                  key={step.id}
                                  dot={
                                    step.status === 'running' ? <LoadingOutlined /> :
                                    step.status === 'completed' ? <CheckCircleOutlined style={{ color: '#52c41a' }} /> :
                                    step.status === 'error' ? <CloseCircleOutlined style={{ color: '#f5222d' }} /> :
                                    <div style={{ width: 10, height: 10, borderRadius: '50%', background: '#d9d9d9' }} />
                                  }
                                  label={step.status === 'completed' ? '完成' : step.status === 'running' ? '执行中' : '等待'}
                                >
                                  <div style={{ fontWeight: 500 }}>{step.name}</div>
                                  {step.detail && <div style={{ fontSize: 12, color: '#8c8c8c' }}>{step.detail}</div>}
                                </Timeline.Item>
                              ))}
                            </Timeline>
                          </Card>
                        )}

                        <Text type="secondary" style={{ fontSize: 12, marginTop: 4, display: 'block' }}>
                          {msg.timestamp.toLocaleTimeString()}
                        </Text>
                      </div>
                      {msg.type === 'user' && (
                        <Avatar style={{ backgroundColor: '#52c41a' }}><UserOutlined /></Avatar>
                      )}
                    </Space>
                  </List.Item>
                )}
              />
              <div ref={messagesEndRef} />
            </div>

            {/* 输入区 */}
            <div style={{ padding: '16px 24px', borderTop: '1px solid #f0f0f0' }}>
              <Space.Compact style={{ width: '100%' }}>
                <Button icon={<AudioOutlined />} />
                <TextArea
                  placeholder="输入您的指令，例如：帮我做一个关于咖啡的视频，发到抖音..."
                  autoSize={{ minRows: 1, maxRows: 4 }}
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  onPressEnter={(e) => {
                    if (!e.shiftKey) {
                      e.preventDefault()
                      handleSend()
                    }
                  }}
                  disabled={isProcessing}
                />
                <Button
                  type="primary"
                  icon={<SendOutlined />}
                  onClick={handleSend}
                  loading={isProcessing}
                >
                  发送
                </Button>
              </Space.Compact>
            </div>
          </Card>
        </Col>

        {/* 右侧：执行日志 */}
        <Col span={6} style={{ height: '100%' }}>
          <Card title="执行日志" style={{ height: '100%' }}>
            <div style={{ fontSize: 12, color: '#8c8c8c', fontFamily: 'monospace' }}>
              <div>[14:32:01] 系统初始化完成</div>
              <div>[14:32:15] 连接AI服务成功</div>
              <div>[14:35:22] 接收到用户指令</div>
              <div>[14:35:23] 开始解析意图...</div>
              <div>[14:35:25] 意图识别: 内容生成+发布</div>
              <div>[14:35:26] 调用视频生成API...</div>
              <div>[14:38:45] 视频生成完成</div>
              <div>[14:38:46] 配置发布计划...</div>
              <div>[14:38:50] 任务执行完成</div>
            </div>
          </Card>
        </Col>
      </Row>
    </div>
  )
}

export default AICommand
