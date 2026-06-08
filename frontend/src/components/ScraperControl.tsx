import { useState } from "react";
import { Play, Loader2, AlertCircle, CheckCircle } from "lucide-react";
import { CompanyCategory } from "../types";
import "./ScraperControl.css";

export function ScraperControl() {
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState<{type: 'idle' | 'success' | 'error', msg: string}>({ type: 'idle', msg: '' });
  const [selectedCategory, setSelectedCategory] = useState<string>(CompanyCategory.MAIN);

  const handleScrape = async () => {
    setLoading(true);
    setStatus({ type: 'idle', msg: '' });
    
    try {
      const response = await fetch('/api/v1/scrape/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          category: selectedCategory,
          headless: true
        })
      });

      if (!response.ok) {
        throw new Error(`Error: ${response.status}`);
      }

      const data = await response.json();
      setStatus({ 
        type: 'success', 
        msg: `Task started successfully. ID: ${data.task_id.substring(0, 8)}...` 
      });
    } catch (err: any) {
      setStatus({ type: 'error', msg: err.message || "Failed to trigger scraper" });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="scraper-control glass-panel">
      <div className="control-header">
        <h3>Trigger Crawler</h3>
        <p>Dispatch background Celery workers to scrape new jobs.</p>
      </div>

      <div className="control-actions">
        <select 
          className="glass-select"
          value={selectedCategory}
          onChange={(e) => setSelectedCategory(e.target.value)}
        >
          <option value={CompanyCategory.MAIN}>Tier 1 & 2 (Main)</option>
          <option value={CompanyCategory.INDIAN_PRODUCT}>Indian Product</option>
          <option value={CompanyCategory.SERVICE}>Service / Consultancies</option>
        </select>

        <button 
          className="btn btn-primary" 
          onClick={handleScrape}
          disabled={loading}
        >
          {loading ? <Loader2 size={18} className="spin" /> : <Play size={18} />}
          <span>{loading ? "Dispatching..." : "Start Scrape"}</span>
        </button>
      </div>

      {status.type !== 'idle' && (
        <div className={`status-message ${status.type} animate-fade-in`}>
          {status.type === 'success' ? <CheckCircle size={16} /> : <AlertCircle size={16} />}
          <span>{status.msg}</span>
        </div>
      )}
    </div>
  );
}
