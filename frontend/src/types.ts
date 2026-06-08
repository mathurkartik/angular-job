export enum CompanyCategory {
  MAIN = "main",
  INDIAN_PRODUCT = "indian_product",
  SERVICE = "service",
}

export interface JobListing {
  id: number;
  company_name: string;
  company_tier: string;
  category: CompanyCategory;
  job_title: string;
  location: string;
  description_text: string;
  application_url: string;
  date_posted?: string;
  scraped_at: string;
  passed_gates: string[];
  total_score: number;
  pillar_scores: Record<string, number>;
  matched_keywords: Record<string, string[]>;
  justification: string;
}
