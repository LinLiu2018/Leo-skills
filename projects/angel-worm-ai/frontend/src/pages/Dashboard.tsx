import { Row, Col, Card, Statistic, Badge, List, Avatar, Typography, Button, Space, Tag } from 'antd'
import {
  TeamOutlined,
  VideoCameraOutlined,
  UserAddOutlined,
  MessageOutlined,
  ArrowUpOutlined,
  ArrowDownOutlined,
  SyncOutlined,
  PlusOutlined,
} from '@ant-design/icons'
import './Dashboard.css'

const { Title, Text } = Typography

// 模拟数据
const statsData = [
  { title: '总账号数', value: 128, icon: <TeamOutlined />, color: '#1677ff', trend: '+12%', up: true },
  { title: '今日发布', value: 45, icon: <VideoCameraOutlined />, color: '#52c41a', trend: '+8%', up: true },
  { title: '新增线索', value: 238, icon: <UserAddOutlined />, color: '#faad14', trend: '+23%', up: true },
  { title: '私域增长', value: 89, icon: <MessageOutlined />, color: '#722ed1', trend: '-5%', up: false },
]

const recentActivity = [
  { id: 1, action: '发布视频', detail: '抖音账号"Leo说房"发布《宁波别墅市场分析》', time: '2分钟前', status: 'success' },
  { id: 2, action: '获取线索', detail: '小红书账号收到3条购买意向评论', time: '5分钟前', status: 'processing' },
  { id: 3, action: '自动回复', detail: '微信自动通过好友申请: 张先生', time: '10分钟前', status: 'success' },
  { id: 4, action: '内容生成', detail: 'AI生成《法拍房避坑指南》视频脚本', time: '15分钟前', status: 'success' },
  { id: 5, action: '发布失败', detail: '快手账号"宁波房产"发布失败，准备重试', time: '20分钟前', status: 'error' },
]

const accountStatus = [
  { platform: '抖音', accounts: 45, online: 42, warning: 2, error: 1 },
  { platform: '快手', accounts: 32, online: 30, warning: 1, error: 1 },
  { platform: '视频号', accounts: 28, online: 28, warning: 0, error: 0 },
  { platform: '小红书', accounts: 23, online: 22, warning: 1, error: 0 },
]

function Dashboard() {
  return (
    <div className="dashboard-page">
      {/* 页面标题 */}
      <div className="page-header">
        <div>
          <Title level={4} style={{ margin: 0 }}>数据总览</Title>
          <Text type="secondary">实时监控您的矩阵运营数据</Text>
        </div>
        <Space>
          <Button icon={<SyncOutlined />}>刷新数据</Button>
          <Button type="primary" icon={<PlusOutlined />}>快速操作</Button>
        </Space>
      </div>

      {/* 核心数据卡片 */}
      <Row gutter={[16, 16]} className="stats-row">
        {statsData.map((stat, index) => (
          <Col xs={24} sm={12} lg={6} key={index}>
            <Card className="stat-card" bordered={false}>
              <div className="stat-header">
                <div className="stat-icon" style={{ backgroundColor: `${stat.color}20`, color: stat.color }}>
                  {stat.icon}
                </div>
                <div className={`stat-trend ${stat.up ? 'up' : 'down'}`}>
                  {stat.up ? <ArrowUpOutlined /> : <ArrowDownOutlined />}
                  {stat.trend}
                </div>
              </div>
              <Statistic
                title={stat.title}
                value={stat.value}
                valueStyle={{ fontSize: '28px', fontWeight: 600 }}
              />
            </Card>
          </Col>
        ))}
      </Row>

      {/* 主要内容区 */}
      <Row gutter={[16, 16]} className="main-row">
        {/* 账号状态 */}
        <Col xs={24} lg={12}>
          <Card
            title="账号矩阵状态"
            extra={<Button type="link">查看全部</Button>}
            className="dashboard-card"
          >
            <div className="platform-status-list">
              {accountStatus.map((item, index) => (
                <div key={index} className="platform-status-item">
                  <div className="platform-info">
                    <Avatar size="small" style={{ backgroundColor: '#1677ff' }}>
                      {item.platform[0]}
                    </Avatar>
                    <span className="platform-name">{item.platform}</span>
                    <Tag>{item.accounts}个账号</Tag>
                  </div>
                  <div className="platform-stats">
                    <Badge status="success" text={`${item.online}在线`} />
                    {item.warning > 0 && <Badge status="warning" text={`${item.warning}警告`} style={{ marginLeft: 12 }} />}
                    {item.error > 0 && <Badge status="error" text={`${item.error}异常`} style={{ marginLeft: 12 }} />}
                  </div>
                </div>
              ))}
            </div>
          </Card>
        </Col>

        {/* 实时动态 */}
        <Col xs={24} lg={12}>
          <Card
            title="实时动态"
            extra={<Button type="link">查看日志</Button>}
            className="dashboard-card"
          >
            <List
              dataSource={recentActivity}
              renderItem={(item) => (
                <List.Item className="activity-item">
                  <List.Item.Meta
                    avatar={
                      <Avatar
                        size="small"
                        style={{
                          backgroundColor:
                            item.status === 'success' ? '#52c41a20' :
                            item.status === 'error' ? '#f5222d20' : '#1677ff20',
                          color:
                            item.status === 'success' ? '#52c41a' :
                            item.status === 'error' ? '#f5222d' : '#1677ff',
                        }}
                      >
                        {item.action[0]}
                      </Avatar>
                    }
                    title={<Text strong>{item.action}</Text>}
                    description={item.detail}
                  />
                  <Text type="secondary" className="activity-time">{item.time}</Text>
                </List.Item>
              )}
            />
          </Card>
        </Col>
      </Row>

      {/* 快捷操作区 */}
      <Card title="快捷操作" className="dashboard-card quick-actions">
        <Space wrap size="middle">
          <Button type="primary" size="large" icon={<VideoCameraOutlined />}>
            AI生成视频
          </Button>
          <Button size="large" icon={<PlusOutlined />}>
            添加账号
          </Button>
          <Button size="large" icon={<SyncOutlined />}>
            批量发布
          </Button>
          <Button size="large" icon={<MessageOutlined />}>
            查看私信
          </Button>
        </Space>
      </Card>
    </div>
  )
}

export default Dashboard
