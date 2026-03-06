import { useState } from 'react'
import {
  Card, Row, Col, Button, Input, Select, Tabs, List, Tag, Space,
  Upload, Progress, Typography, Empty, message, Modal
} from 'antd'
import {
  VideoCameraOutlined, FileTextOutlined, PictureOutlined,
  PlusOutlined, UploadOutlined, PlayCircleOutlined, DeleteOutlined,
  CopyOutlined, EditOutlined, HistoryOutlined
} from '@ant-design/icons'

const { TextArea } = Input
const { Option } = Select
const { Title, Text } = Typography
const { TabPane } = Tabs

// 视频生成类型
const videoTypes = [
  { key: 't2v', name: '文生视频', icon: <FileTextOutlined />, desc: '输入文案生成视频' },
  { key: 'i2v', name: '图生视频', icon: <PictureOutlined />, desc: '上传图片生成视频' },
  { key: 'avatar', name: '数字人视频', icon: <VideoCameraOutlined />, desc: 'AI数字人口播' },
  { key: 'mix', name: '智能混剪', icon: <PlayCircleOutlined />, desc: '多素材智能混剪' },
]

// 历史记录
const historyItems = [
  { id: 1, type: 't2v', title: '宁波别墅市场分析', status: 'completed', time: '10分钟前', duration: '45秒' },
  { id: 2, type: 'avatar', title: '法拍房避坑指南', status: 'generating', progress: 65, time: '进行中' },
  { id: 3, type: 'i2v', title: '商业投资推荐', status: 'completed', time: '1小时前', duration: '30秒' },
]

function ContentCreation() {
  const [activeType, setActiveType] = useState('t2v')
  const [prompt, setPrompt] = useState('')
  const [generating, setGenerating] = useState(false)
  const [previewOpen, setPreviewOpen] = useState(false)

  const handleGenerate = () => {
    if (!prompt.trim()) {
      message.warning('请输入生成内容描述')
      return
    }
    setGenerating(true)
    // 模拟生成过程
    setTimeout(() => {
      setGenerating(false)
      message.success('视频生成任务已提交')
    }, 1500)
  }

  return (
    <div className="content-creation-page">
      <Row gutter={24}>
        {/* 左侧：创作区 */}
        <Col span={16}>
          <Card
            title={<Space>
              <VideoCameraOutlined />
              <span>AI内容创作</span>
            </Space>}
          >
            {/* 视频类型选择 */}
            <div style={{ marginBottom: 24 }}>
              <Text type="secondary" style={{ display: 'block', marginBottom: 12 }}>选择生成类型</Text>
              <Space wrap size="large">
                {videoTypes.map(type => (
                  <Card
                    key={type.key}
                    className={`type-card ${activeType === type.key ? 'active' : ''}`}
                    onClick={() => setActiveType(type.key)}
                    style={{
                      width: 140,
                      cursor: 'pointer',
                      textAlign: 'center',
                      borderColor: activeType === type.key ? '#1677ff' : undefined
                    }}
                  >
                    <div style={{ fontSize: 32, color: activeType === type.key ? '#1677ff' : '#8c8c8c', marginBottom: 8 }}>
                      {type.icon}
                    </div>
                    <div style={{ fontWeight: 500 }}>{type.name}</div>
                    <div style={{ fontSize: 12, color: '#8c8c8c', marginTop: 4 }}>{type.desc}</div>
                  </Card>
                ))}
              </Space>
            </div>

            {/* 输入区 */}
            <div style={{ marginBottom: 24 }}>
              <Text type="secondary" style={{ display: 'block', marginBottom: 12 }}>
                {activeType === 't2v' && '输入视频文案或描述'}
                {activeType === 'i2v' && '上传图片并描述'}
                {activeType === 'avatar' && '输入口播文案'}
                {activeType === 'mix' && '上传多个素材'}
              </Text>

              {activeType === 'i2v' && (
                <Upload.Dragger style={{ marginBottom: 16 }}>
                  <p className="ant-upload-drag-icon">
                    <UploadOutlined />
                  </p>
                  <p className="ant-upload-text">点击或拖拽上传图片</p>
                  <p className="ant-upload-hint">支持 JPG、PNG、WEBP 格式</p>
                </Upload.Dragger>
              )}

              {activeType === 'mix' && (
                <Upload.Dragger multiple style={{ marginBottom: 16 }}>
                  <p className="ant-upload-drag-icon">
                    <UploadOutlined />
                  </p>
                  <p className="ant-upload-text">上传多个素材进行混剪</p>
                  <p className="ant-upload-hint">支持视频、图片混合上传</p>
                </Upload.Dragger>
              )}

              <TextArea
                rows={6}
                placeholder={
                  activeType === 't2v' ? '输入视频主题或详细描述，AI将为您生成完整视频...' :
                  activeType === 'avatar' ? '输入数字人需要口播的文案内容...' :
                  '补充描述视频风格、场景等信息...'
                }
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
              />
            </div>

            {/* 参数设置 */}
            <div style={{ marginBottom: 24 }}>
              <Text type="secondary" style={{ display: 'block', marginBottom: 12 }}>生成参数</Text>
              <Space size="large">
                <div>
                  <Text style={{ marginRight: 8 }}>视频时长:</Text>
                  <Select defaultValue="15" style={{ width: 100 }}>
                    <Option value="15">15秒</Option>
                    <Option value="30">30秒</Option>
                    <Option value="60">60秒</Option>
                  </Select>
                </div>
                <div>
                  <Text style={{ marginRight: 8 }}>视频比例:</Text>
                  <Select defaultValue="9:16" style={{ width: 100 }}>
                    <Option value="9:16">9:16 (竖屏)</Option>
                    <Option value="16:9">16:9 (横屏)</Option>
                    <Option value="1:1">1:1 (方形)</Option>
                  </Select>
                </div>
                <div>
                  <Text style={{ marginRight: 8 }}>质量等级:</Text>
                  <Select defaultValue="standard" style={{ width: 100 }}>
                    <Option value="standard">标准</Option>
                    <Option value="high">高清</Option>
                    <Option value="ultra">超清</Option>
                  </Select>
                </div>
              </Space>
            </div>

            {/* 操作按钮 */}
            <Space size="middle">
              <Button type="primary" size="large" loading={generating} onClick={handleGenerate}>
                <PlayCircleOutlined /> 开始生成
              </Button>
              <Button size="large" onClick={() => setPrompt('')}>
                清空内容
              </Button>
            </Space>
          </Card>
        </Col>

        {/* 右侧：历史记录 */}
        <Col span={8}>
          <Card
            title={<Space>
              <HistoryOutlined />
              <span>生成历史</span>
            </Space>}
          >
            <List
              dataSource={historyItems}
              renderItem={(item) => (
                <List.Item
                  actions={[
                    <Button type="text" icon={<PlayCircleOutlined />} onClick={() => setPreviewOpen(true)} />,
                    <Button type="text" icon={<CopyOutlined />} />,
                    <Button type="text" icon={<DeleteOutlined />} danger />,
                  ]}
                >
                  <List.Item.Meta
                    title={<div>
                      <Text strong>{item.title}</Text>
                      {item.status === 'generating' && <Tag color="processing" style={{ marginLeft: 8 }}>生成中</Tag>}
                    </div>}
                    description={<Space direction="vertical" size={0}>
                        <Text type="secondary" style={{ fontSize: 12 }}>
                          {videoTypes.find(t => t.key === item.type)?.name} · {item.time}
                        </Text>
                        {item.status === 'generating' ? (
                          <Progress percent={item.progress} size="small" />
                        ) : (
                          <Text type="secondary" style={{ fontSize: 12 }}>时长: {item.duration}</Text>
                        )}
                      </Space>
                    }
                  />
                </List.Item>
              )}
              locale={{
                emptyText: <Empty description="暂无生成记录" />
              }}
            />
          </Card>

          {/* 素材库入口 */}
          <Card style={{ marginTop: 16 }}>
            <div style={{ textAlign: 'center' }}>
              <Title level={5}>素材库</Title>
              <Text type="secondary" style={{ display: 'block', marginBottom: 16 }}>管理和使用您的素材</Text>
              <Button type="primary" icon={<UploadOutlined />} block>
                上传素材
              </Button>
            </div>
          </Card>
        </Col>
      </Row>

      {/* 预览弹窗 */}
      <Modal
        title="视频预览"
        open={previewOpen}
        onCancel={() => setPreviewOpen(false)}
        footer={[
          <Button key="close" onClick={() => setPreviewOpen(false)}>关闭</Button>,
          <Button key="use" type="primary">使用该视频</Button>,
        ]}
        width={800}
      >
        <div style={{ background: '#000', height: 400, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <Text style={{ color: '#fff' }}>视频预览区域</Text>
        </div>
      </Modal>
    </div>
  )
}

export default ContentCreation
