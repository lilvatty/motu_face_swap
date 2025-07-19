import { Routes, Route } from 'react-router-dom'
import App from './App.jsx'
import CSV from './pages/CSV.jsx'
import Print from './pages/Print.jsx'

function AppRouter() {
  return (
    <>
      <Routes>
        <Route path="/" element={<App />} />
        <Route path="/csv" element={<CSV />} />
        <Route path="/print" element={<Print />} />
        {/* Fallback route - redirect to home */}
        <Route path="*" element={<App />} />
      </Routes>
    </>
  )
}

export default AppRouter 