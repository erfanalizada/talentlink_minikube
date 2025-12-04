export interface Job {
  job_id: number;
  employer_id: string;
  title: string;
  description: string;
  salary?: number;
  skills: string[];
  created_at: string;
  updated_at?: string;
}

export interface JobApplication {
  application_id: number;
  job_id: number;
  employee_id: string;
  cv_url: string;
  portfolio_url?: string;
  status: 'pending' | 'accepted' | 'rejected';
  employee_profile?: {
    username: string;
    email: string;
    phone: string | null;
    description: string | null;
  };
  created_at: string;
  updated_at?: string;
}

export interface CreateJobDto {
  employer_id: string;
  title: string;
  description: string;
  salary?: number;
  skills: string[];
}

export interface ApplyToJobDto {
  employee_id: string;
  cv: string; // base64 encoded
  portfolio_url?: string;
}
