import { useEffect, useState } from 'react'
import './App.css'
import kuralData from '../all_thirukkural_information.json'

function getKuralNumberForToday() {
  const totalKurals = 1330
  const now = new Date()
  const start = new Date('2025-01-01T00:00:00Z')
  const daysSinceStart = Math.floor((now - start) / (1000 * 60 * 60 * 24))
  return ((daysSinceStart % totalKurals) + 1).toString()
}

function getRandomKuralNumber() {
  return (Math.floor(Math.random() * 1330) + 1).toString()
}

function getKuralDetails(num) {
  return kuralData[num]
}

function App() {
  const [kuralNum, setKuralNum] = useState(getKuralNumberForToday())
  const [kural, setKural] = useState(getKuralDetails(kuralNum))

  useEffect(() => {
    setKural(getKuralDetails(kuralNum))
  }, [kuralNum])

  const handleRefresh = () => {
    setKuralNum(getRandomKuralNumber())
  }

  if (!kural) return <div className="loader">Loading...</div>

  return (
    <div className="kural-container sleek">
      <h1 className="title">Thirukural of the Day</h1>
      <button className="refresh-btn" onClick={handleRefresh} title="Show another Kural">↻</button>
      <div className="kural-card">
        <div className="kural-number">Kural #{kural["0_number"]}</div>
        <div className="meta-block-inside">
          <span className="iyal-title"><b>இயல்:</b> {kural["4_iyal"]}</span><br />
          <span className="adikaram-title"><b>அதிகாரம்:</b> {kural["2_adikaram"]}</span>
        </div>
        <div className="kural-lines">
          <span>{kural["1_line1"]}</span><br />
          <span>{kural["1_line2"]}</span>
        </div>
        <div className="meanings">
          <div className="meaning-block">
            <div className="meaning-title">Meaning (Tamil)</div>
            <div className="meaning-text">{kural["6_mu_varatha"] ? kural["6_mu_varatha"][1] : ''}</div>
          </div>
          <div className="meaning-block">
            <div className="meaning-title">Meaning (English)</div>
            <div className="meaning-text">{kural["1_translation"]}</div>
          </div>
        </div>
      </div>
      <footer className="footer">Powered by <a href="https://github.com/vijayanandrp/Thirukkural-Tamil-Dataset" target="_blank" rel="noopener noreferrer">Thirukkural Dataset</a></footer>
    </div>
  )
}

export default App
