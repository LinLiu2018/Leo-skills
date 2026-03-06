import { Routes, Route } from 'react-router-dom'
import MainLayout from './layouts/MainLayout'
import Dashboard from './pages/Dashboard'
import AccountMatrix from './pages/AccountMatrix'
import ContentCreation from './pages/ContentCreation'
import SmartPublish from './pages/SmartPublish'
import AutoOperation from './pages/AutoOperation'
import PrivateDomain from './pages/PrivateDomain'
import AICommand from './pages/AICommand'
import DataAnalysis from './pages/DataAnalysis'
import Settings from './pages/Settings'
import './App.css'

function App() {
  return (
    <Routes>
      <Route path="/" element={<MainLayout />}>
        <Route index element={<Dashboard />} />
        <Route path="accounts" element={<AccountMatrix />} />
        <Route path="content" element={<ContentCreation />} />
        <Route path="publish" element={<SmartPublish />} />
        <Route path="auto-op" element={<AutoOperation />} />
        <Route path="private" element={<PrivateDomain />} />
        <Route path="ai-command" element={<AICommand />} />
        <Route path="analytics" element={<DataAnalysis />} />
        <Route path="settings" element={<Settings />} />
      </Route>
    </Routes>
  )
}

export default App
