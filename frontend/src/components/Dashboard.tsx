import { useState, useEffect } from "react";
import { Loader2, SearchX } from "lucide-react";
import type { JobListing } from "../types";
import { JobCard } from "./JobCard";
import "./Dashboard.css";

interface DashboardProps {
  activeCategory: string;
}

export function Dashboard({ activeCategory }: DashboardProps) {
  const [jobs, setJobs] = useState<JobListing[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchJobs() {
      setLoading(true);
      setError(null);
      try {
        // Try static JSON first (GitHub Pages), fall back to live API (local Docker)
        let response = await fetch(`${import.meta.env.BASE_URL}jobs.json`);
        if (!response.ok) {
          response = await fetch('/api/v1/jobs?limit=100');
        }
        if (!response.ok) throw new Error("Failed to fetch jobs");
        const data = await response.json();
        setJobs(data);
      } catch (err: any) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }
    fetchJobs();
  }, []); // Re-fetch could be added on a button or interval

  // Filter jobs by selected category (unless "all")
  const filteredJobs = jobs.filter(job => 
    activeCategory === "all" || job.category === activeCategory
  );

  if (loading) {
    return (
      <div className="dashboard-state">
        <Loader2 size={40} className="spin text-gradient" />
        <p>Loading ranked job matches...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="dashboard-state error">
        <p>Failed to load data from database.</p>
        <p className="text-secondary">{error}</p>
      </div>
    );
  }

  if (filteredJobs.length === 0) {
    return (
      <div className="dashboard-state">
        <SearchX size={48} className="text-tertiary mb-4" />
        <h3>No jobs found for this category</h3>
        <p className="text-secondary">Try triggering a scrape or selecting a different category.</p>
      </div>
    );
  }

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h2>Recommended Matches</h2>
        <span className="job-count">{filteredJobs.length} Angular roles found</span>
      </div>
      
      <div className="job-grid">
        {filteredJobs.map((job) => (
          <JobCard key={job.id} job={job} />
        ))}
      </div>
    </div>
  );
}
