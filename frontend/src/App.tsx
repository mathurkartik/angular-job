import { useState } from 'react'
import { Sidebar } from './components/Sidebar'
import { ScraperControl } from './components/ScraperControl'
import { Dashboard } from './components/Dashboard'

function App() {
  const [activeCategory, setActiveCategory] = useState<string>("all")

  return (
    <div className="app-container">
      <Sidebar 
        activeCategory={activeCategory} 
        setActiveCategory={setActiveCategory} 
      />
      
      <main className="main-content">
        <header style={{ marginBottom: '2rem' }}>
          <h1 className="text-gradient">AngularHunt Command Center</h1>
          <p className="text-secondary" style={{ marginTop: '0.5rem' }}>
            Monitor and manage automated job scraping tasks across tier 1, big tech, and global remote boards.
          </p>
        </header>
        
        <ScraperControl />
        <Dashboard activeCategory={activeCategory} />
      </main>
    </div>
  )
}

export default App
