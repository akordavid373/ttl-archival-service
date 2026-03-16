import { Routes, Route } from 'react-router-dom'
import { Layout } from './components/Layout'
import { Dashboard } from './pages/Dashboard'
import { Policies } from './pages/Policies'
import { Archives } from './pages/Archives'
import { Blockchain } from './pages/Blockchain'
import { Settings } from './pages/Settings'

function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/policies" element={<Policies />} />
        <Route path="/archives" element={<Archives />} />
        <Route path="/blockchain" element={<Blockchain />} />
        <Route path="/settings" element={<Settings />} />
      </Routes>
    </Layout>
  )
}

export default App
