import axios from 'axios';
import { Job, JobApplication, CreateJobDto, ApplyToJobDto } from '../types/job';
import { TokenStorage } from './tokenStorage';

const BASE_URL = 'http://talentlink.local/api/jobs';

export class JobService {
  private static getAuthHeaders() {
    const token = TokenStorage.getAccessToken();
    return {
      Authorization: `Bearer ${token}`,
    };
  }

  // Job endpoints
  static async createJob(data: CreateJobDto): Promise<Job> {
    try {
      const response = await axios.post<Job>(`${BASE_URL}`, data, {
        headers: this.getAuthHeaders(),
      });
      return response.data;
    } catch (error: any) {
      const message = error.response?.data?.error || 'Failed to create job';
      throw new Error(message);
    }
  }

  static async getAllJobs(): Promise<Job[]> {
    try {
      const response = await axios.get<Job[]>(`${BASE_URL}`, {
        headers: this.getAuthHeaders(),
      });
      return response.data;
    } catch (error: any) {
      // If service is unavailable, return empty array instead of throwing
      if (error.code === 'ERR_NETWORK' || !error.response) {
        console.warn('Job service unavailable, returning empty list');
        return [];
      }
      const message = error.response?.data?.error || 'Failed to fetch jobs';
      throw new Error(message);
    }
  }

  static async getJob(jobId: number): Promise<Job> {
    try {
      const response = await axios.get<Job>(`${BASE_URL}/${jobId}`, {
        headers: this.getAuthHeaders(),
      });
      return response.data;
    } catch (error: any) {
      const message = error.response?.data?.error || 'Failed to fetch job';
      throw new Error(message);
    }
  }

  static async getJobsByEmployer(employerId: string): Promise<Job[]> {
    try {
      const response = await axios.get<Job[]>(`${BASE_URL}/employer/${employerId}`, {
        headers: this.getAuthHeaders(),
      });
      return response.data;
    } catch (error: any) {
      // If service is unavailable, return empty array instead of throwing
      if (error.code === 'ERR_NETWORK' || !error.response) {
        console.warn('Job service unavailable, returning empty list');
        return [];
      }
      const message = error.response?.data?.error || 'Failed to fetch jobs';
      throw new Error(message);
    }
  }

  static async updateJob(jobId: number, data: Partial<CreateJobDto>): Promise<Job> {
    try {
      const response = await axios.put<Job>(`${BASE_URL}/${jobId}`, data, {
        headers: this.getAuthHeaders(),
      });
      return response.data;
    } catch (error: any) {
      const message = error.response?.data?.error || 'Failed to update job';
      throw new Error(message);
    }
  }

  static async deleteJob(jobId: number, employerId: string): Promise<void> {
    try {
      await axios.delete(`${BASE_URL}/${jobId}`, {
        headers: this.getAuthHeaders(),
        data: { employer_id: employerId },
      });
    } catch (error: any) {
      const message = error.response?.data?.error || 'Failed to delete job';
      throw new Error(message);
    }
  }

  // Application endpoints
  static async applyToJob(jobId: number, data: ApplyToJobDto): Promise<JobApplication> {
    try {
      const response = await axios.post<JobApplication>(`${BASE_URL}/${jobId}/apply`, data, {
        headers: this.getAuthHeaders(),
      });
      return response.data;
    } catch (error: any) {
      const message = error.response?.data?.error || 'Failed to submit application';
      throw new Error(message);
    }
  }

  static async getJobApplications(jobId: number, employerId: string): Promise<JobApplication[]> {
    try {
      const response = await axios.get<JobApplication[]>(
        `${BASE_URL}/${jobId}/applications?employer_id=${employerId}`,
        {
          headers: this.getAuthHeaders(),
        }
      );
      return response.data;
    } catch (error: any) {
      const message = error.response?.data?.error || 'Failed to fetch applications';
      throw new Error(message);
    }
  }

  static async getEmployeeApplications(employeeId: string): Promise<JobApplication[]> {
    try {
      const response = await axios.get<JobApplication[]>(
        `${BASE_URL.replace('/jobs', '/applications')}/employee/${employeeId}`,
        {
          headers: this.getAuthHeaders(),
        }
      );
      return response.data;
    } catch (error: any) {
      // If service is unavailable, return empty array instead of throwing
      if (error.code === 'ERR_NETWORK' || !error.response) {
        console.warn('Job service unavailable, returning empty list');
        return [];
      }
      const message = error.response?.data?.error || 'Failed to fetch applications';
      throw new Error(message);
    }
  }

  static async updateApplicationStatus(
    applicationId: number,
    employerId: string,
    status: 'pending' | 'accepted' | 'rejected'
  ): Promise<JobApplication> {
    try {
      const response = await axios.put<JobApplication>(
        `${BASE_URL.replace('/jobs', '/applications')}/${applicationId}/status`,
        { employer_id: employerId, status },
        {
          headers: this.getAuthHeaders(),
        }
      );
      return response.data;
    } catch (error: any) {
      const message = error.response?.data?.error || 'Failed to update application';
      throw new Error(message);
    }
  }

  // Helper function to convert file to base64
  static async fileToBase64(file: File): Promise<string> {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.readAsDataURL(file);
      reader.onload = () => {
        const result = reader.result as string;
        // Remove the data URL prefix (e.g., "data:application/pdf;base64,")
        const base64 = result.split(',')[1];
        resolve(base64);
      };
      reader.onerror = (error) => reject(error);
    });
  }
}
