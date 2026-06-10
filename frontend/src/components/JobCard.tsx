import { ExternalLink, Calendar, MapPin, Building2, CheckCircle2 } from "lucide-react";
import type { JobListing } from "../types";
import "./JobCard.css";

interface JobCardProps {
  job: JobListing;
}

export function JobCard({ job }: JobCardProps) {
  // Extract domain from URL for display
  const domain = new URL(job.application_url).hostname.replace("www.", "");

  return (
    <div className="job-card glass-card animate-slide-up">
      <div className="job-card-header">
        <div className="company-info">
          <div className="company-icon">
            <Building2 size={20} className="text-gradient" />
          </div>
          <div>
            <h3 className="job-title">{job.job_title}</h3>
            <div className="company-meta">
              <span className="company-name">{job.company_name}</span>
              <span className="dot-divider">•</span>
              <span className="company-tier">{job.company_tier.replace(/_/g, ' ')}</span>
            </div>
          </div>
        </div>
      </div>

      <div className="job-tags">
        <div className="tag">
          <MapPin size={14} />
          {job.location || "Remote"}
        </div>
        {job.date_posted && (
          <div className="tag">
            <Calendar size={14} />
            {job.date_posted}
          </div>
        )}
        {job.passed_gates.slice(0, 2).map((gate, i) => (
          <div key={i} className="tag gate-tag">
            <CheckCircle2 size={14} />
            {gate}
          </div>
        ))}
        {job.passed_gates.length > 2 && (
          <div className="tag gate-tag">
            +{job.passed_gates.length - 2} more
          </div>
        )}
      </div>


      <div className="job-card-footer">
        <a 
          href={job.application_url} 
          target="_blank" 
          rel="noopener noreferrer"
          className="btn btn-primary apply-btn"
        >
          <span>Apply on {domain}</span>
          <ExternalLink size={16} />
        </a>
      </div>
    </div>
  );
}
