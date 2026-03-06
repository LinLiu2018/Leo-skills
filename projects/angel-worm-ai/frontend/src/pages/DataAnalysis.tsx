import { useEffect, useRef } from 'react'
import { Card, Row, Col, Statistic, DatePicker, Select, Table, Tag, Button, Space } from 'antd'
import {
  BarChartOutlined, LineChartOutlined, PieChartOutlined,
  RiseOutlined, FallOutlined, DownloadOutlined, FilterOutlined
} from '@ant-design/icons'
import type { Dayjs } from 'dayjs'
import { Column, Line, Pie } from '@antv/g2plot'

const { RangePicker } = DatePicker

// 数据概览
const overviewData = [
  { title: '总播放量', value: 1258000, trend: '+15%', up: true },
  { title: '总点赞数', value: 45800, trend: '+8%', up: true },
  { title: '总评论数', value: 8900, trend: '-2%', up: false },
  { title: '总分享数', value: 3200, trend: '+12%', up: true },
]

// 平台数据
const platformData = [
  { platform: '抖音', plays: 580000, likes: 25000, comments: 4200, shares: 1800 },
  { platform: '快手', plays: 320000, likes: 12000, comments: 2100, shares: 800 },
  { platform: '视频号', plays: 210000, likes: 6000, comments: 1500, shares: 400 },
  { platform: '小红书', plays: 148000, likes: 2800, comments: 1100, shares: 200 },
]

// 内容排行
const contentRanking = [
  { id: 1, title: '宁波别墅市场分析', platform: '抖音', plays: 125000, likes: 5800, date: '2026-03-01' },
  { id: 2, title: '法拍房避坑指南', platform: '快手', plays: 98000, likes: 4200, date: '2026-03-01' },
  { id: 3, title: '商业投资推荐', platform: '视频号', plays: 76000, likes: 3100, date: '2026-02-28' },
  { id: 4, title: '别墅装修案例', platform: '小红书', plays: 45000, likes: 1800, date: '2026-02-28' },
  { id: 5, title: '房产政策解读', platform: '抖音', plays: 42000, likes: 1500, date: '2026-02-27' },
]

function DataAnalysis() {
  const trendChartRef = useRef<HTMLDivElement>(null)
  const platformChartRef = useRef<HTMLDivElement>(null)
  const pieChartRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (trendChartRef.current) {
      const line = new Line(trendChartRef.current, {
        data: [
          { date: '02-24', value: 120000, type: '播放量' },
          { date: '02-25', value: 150000, type: '播放量' },
          { date: '02-26', value: 135000, type: '播放量' },
          { date: '02-27', value: 180000, type: '播放量' },
          { date: '02-28', value: 220000, type: '播放量' },
          { date: '03-01', value: 195000, type: '播放量' },
          { date: '03-02', value: 258000, type: '播放量' },
        ],
        xField: 'date',
        yField: 'value',
        smooth: true,
        color: '#1677ff',
      })
      line.render()

      return () => line.destroy()
    }
  }, [])

  useEffect(() => {
    if (platformChartRef.current) {
      const column = new Column(platformChartRef.current, {
        data: platformData.map(d => ({
          platform: d.platform,
          value: d.plays,
        })),
        xField: 'platform',
        yField: 'value',
        color: '#1677ff',
        label: {
          position: 'top',
        },
      })
      column.render()

      return () => column.destroy()
    }
  }, [])

  useEffect(() => {
    if (pieChartRef.current) {
      const pie = new Pie(pieChartRef.current, {
        data: [
          { type: '抖音', value: 46 },
          { type: '快手', value: 26 },
          { type: '视频号', value: 17 },
          { type: '小红书', value: 11 },
        ],
        angleField: 'value',
        colorField: 'type',
        radius: 0.8,
        legend: {
          position: 'right',
        },
      })
      pie.render()

      return () => pie.destroy()
    }
  }, [])

  const columns = [
    {
      title: '排名',
      dataIndex: 'id',
      key: 'id',
      render: (id: number) => (
        <Tag color={id <= 3 ? 'gold' : 'default'}>{id}</Tag>
      ),
    },
    {
      title: '内容标题',
      dataIndex: 'title',
      key: 'title',
    },
    {
      title: '平台',
      dataIndex: 'platform',
      key: 'platform',
      render: (platform: string) => <Tag>{platform}</Tag>,
    },
    {
      title: '播放量',
      dataIndex: 'plays',
      key: 'plays',
      render: (plays: number) => (plays / 10000).toFixed(1) + '万',
    },
    {
      title: '点赞数',
      dataIndex: 'likes',
      key: 'likes',
    },
    {
      title: '发布日期',
      dataIndex: 'date',
      key: 'date',
    },
  ]

  return (
    <div className="data-analysis-page">
      {/* 筛选栏 */}
      <Card style={{ marginBottom: 24 }}>
        <Space>
          <RangePicker />
          <Select defaultValue="all" style={{ width: 120 }}>
            <Select.Option value="all">全部平台</Select.Option>
            <Select.Option value="douyin">抖音</Select.Option>
            <Select.Option value="kuaishou">快手</Select.Option>
            <Select.Option value="shipinhao">视频号</Select.Option>
            <Select.Option value="xiaohongshu">小红书</Select.Option>
          </Select>
          <Button icon={<FilterOutlined />}>筛选</Button>
          <Button icon={<DownloadOutlined />}>导出报告</Button>
        </Space>
      </Card>

      {/* 数据概览 */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        {overviewData.map((item, index) => (
          <Col span={6} key={index}>
            <Card>
              <Statistic
                title={item.title}
                value={item.value}
                valueStyle={{ fontSize: 24 }}
                prefix={item.up ? <RiseOutlined style={{ color: '#52c41a' }} /> : <FallOutlined style={{ color: '#f5222d' }} />}
                suffix={<Tag color={item.up ? 'success' : 'error'}>{item.trend}</Tag>}
              />
            </Card>
          </Col>
        ))}
      </Row>

      {/* 图表区 */}
      <Row gutter={24} style={{ marginBottom: 24 }}>
        <Col span={16}>
          <Card title="播放趋势" extra={<LineChartOutlined />}>
            <div ref={trendChartRef} style={{ height: 300 }} />
          </Card>
        </Col>
        <Col span={8}>
          <Card title="平台占比" extra={<PieChartOutlined />}>
            <div ref={pieChartRef} style={{ height: 300 }} />
          </Card>
        </Col>
      </Row>

      <Row gutter={24} style={{ marginBottom: 24 }}>
        <Col span={12}>
          <Card title="平台数据对比" extra={<BarChartOutlined />}>
            <div ref={platformChartRef} style={{ height: 300 }} />
          </Card>
        </Col>
        <Col span={12}>
          <Card title="平台详细数据">
            <Table dataSource={platformData} rowKey="platform" pagination={false} size="small">
              <Table.Column title="平台" dataIndex="platform" />
              <Table.Column title="播放量" dataIndex="plays" render={(v: number) => (v / 10000).toFixed(1) + '万'} />
              <Table.Column title="点赞数" dataIndex="likes" />
              <Table.Column title="评论数" dataIndex="comments" />
            </Table>
          </Card>
        </Col>
      </Row>

      {/* 内容排行 */}
      <Card title="内容排行榜">
        <Table
          columns={columns}
          dataSource={contentRanking}
          rowKey="id"
          pagination={{ pageSize: 10 }}
        />
      </Card>
    </div>
  )
}

export default DataAnalysis
