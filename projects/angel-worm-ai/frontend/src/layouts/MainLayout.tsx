import { useState } from 'react'
import { Layout, Menu, Avatar, Badge, Space, Typography, Button, Tooltip } from 'antd'
import {
  DashboardOutlined,
  TeamOutlined,
  VideoCameraOutlined,
  ScheduleOutlined,
  RobotOutlined,
  WechatOutlined,
  MessageOutlined,
  BarChartOutlined,
  SettingOutlined,
  BellOutlined,
  QuestionCircleOutlined,
  MenuFoldOutlined,
  MenuUnfoldOutlined,
} from '@ant-design/icons'
import { Outlet, useLocation, useNavigate } from 'react-router-dom'
import './MainLayout.css'

const { Header, Sider, Content } = Layout
const { Text } = Typography

// 导航菜单配置
const menuItems = [
  { key: '/', icon: <DashboardOutlined />, label: '数据总览' },
  { key: '/accounts', icon: <TeamOutlined />, label: '账号矩阵' },
  { key: '/content', icon: <VideoCameraOutlined />, label: '内容创作' },
  { key: '/publish', icon: <ScheduleOutlined />, label: '智能发布' },
  { key: '/auto-op', icon: <RobotOutlined />, label: '自动化运营' },
  { key: '/private', icon: <WechatOutlined />, label: '私域管理' },
  { key: '/ai-command', icon: <MessageOutlined />, label: 'AI指令台' },
  { key: '/analytics', icon: <BarChartOutlined />, label: '数据分析' },
  { key: '/settings', icon: <SettingOutlined />, label: '系统设置' },
]

function MainLayout() {
  const [collapsed, setCollapsed] = useState(false)
  const location = useLocation()
  const navigate = useNavigate()

  return (
    <Layout className="main-layout">
      {/* 顶部导航栏 */}
      <Header className="main-header">
        <div className="header-left">
          <div className="logo">
            <img src="/logo.png" alt="天使虫AI" className="logo-img" />
            <Text strong className="logo-text">天使虫AI操盘手</Text>
          </div>
        </div>
        <div className="header-right">
          <Space size={16}>
            <Tooltip title="帮助文档">
              <Button type="text" icon={<QuestionCircleOutlined />} />
            </Tooltip>
            <Tooltip title="通知">
              <Badge count={5} size="small">
                <Button type="text" icon={<BellOutlined />} />
              </Badge>
            </Tooltip>
            <div className="user-info">
              <Avatar size="small" style={{ backgroundColor: '#1677FF' }}>
                L
              </Avatar>
              <Text className="username">Leo</Text>
            </div>
          </Space>
        </div>
      </Header>

      <Layout className="main-content-layout">
        {/* 左侧导航栏 */}
        <Sider
          trigger={null}
          collapsible
          collapsed={collapsed}
          className="main-sider"
          width={200}
        >
          <Button
            type="text"
            icon={collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
            onClick={() => setCollapsed(!collapsed)}
            className="collapse-btn"
          />
          <Menu
            mode="inline"
            selectedKeys={[location.pathname]}
            items={menuItems}
            onClick={({ key }) => navigate(key)}
            className="main-menu"
          />
        </Sider>

        {/* 主内容区 */}
        <Content className="main-content">
          <Outlet />
        </Content>
      </Layout>
    </Layout>
  )
}

export default MainLayout
