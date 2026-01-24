// DataTable 类型定义

export interface DataTableProps {
  data: any[]
  columns: any[]
  loading?: boolean
  pagination?: boolean
}

export interface DataTableEmits {
  (e: 'row-click', value: any): void
  (e: 'page-change', value: any): void
}