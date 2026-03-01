import { Routes, Route, Navigate } from 'react-router-dom';
import { Layout } from './components/Layout';
import { Dashboard } from './pages/Dashboard';
import { Skills } from './pages/Skills';
import { Agents } from './pages/Agents';
import { Workflows } from './pages/Workflows';
import { Memory } from './pages/Memory';
import { Intent } from './pages/Intent';
import { Evolution } from './pages/Evolution';
import { Settings } from './pages/Settings';
import { SmartExecutor } from './pages/SmartExecutor';

function App() {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<Dashboard />} />
        <Route path="skills" element={<Skills />} />
        <Route path="skills/new" element={<Skills />} />
        <Route path="agents" element={<Agents />} />
        <Route path="agents/new" element={<Agents />} />
        <Route path="workflows" element={<Workflows />} />
        <Route path="workflows/new" element={<Workflows />} />
        <Route path="smart" element={<SmartExecutor />} />
        <Route path="memory" element={<Memory />} />
        <Route path="intent" element={<Intent />} />
        <Route path="evolution" element={<Evolution />} />
        <Route path="settings" element={<Settings />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  );
}

export default App;
