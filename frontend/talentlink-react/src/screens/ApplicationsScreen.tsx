import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card } from '../components/Card';
import { Button } from '../components/Button';
import { JobService } from '../services/jobService';
import { TokenStorage } from '../services/tokenStorage';
import { Job, JobApplication } from '../types/job';
import { useMessageBox } from '../hooks/useMessageBox';
import styles from './ApplicationsScreen.module.css';

const ApplicationsScreen: React.FC = () => {
  const navigate = useNavigate();
  const { showSuccess, showError } = useMessageBox();
  const [loading, setLoading] = useState(true);
  const [jobs, setJobs] = useState<Job[]>([]);
  const [applications, setApplications] = useState<{ [jobId: number]: JobApplication[] }>({});
  const [error, setError] = useState('');

  useEffect(() => {
    loadJobsAndApplications();
  }, []);

  const loadJobsAndApplications = async () => {
    try {
      setLoading(true);
      setError('');
      const userId = TokenStorage.getUserId();
      if (!userId) {
        setError('User not authenticated');
        return;
      }

      // Load employer's jobs
      let employerJobs: Job[] = [];
      try {
        employerJobs = await JobService.getJobsByEmployer(userId);
        setJobs(employerJobs);
      } catch (err) {
        console.error('Failed to load jobs', err);
        setJobs([]);
        // Don't set error here, just show empty state
        setLoading(false);
        return;
      }

      // Only load applications if jobs exist
      if (employerJobs.length === 0) {
        setApplications({});
        setLoading(false);
        return;
      }

      // Load applications for each job
      const allApplications: { [jobId: number]: JobApplication[] } = {};
      for (const job of employerJobs) {
        try {
          const jobApps = await JobService.getJobApplications(job.job_id, userId);
          allApplications[job.job_id] = jobApps;
        } catch (err) {
          console.error(`Failed to load applications for job ${job.job_id}`, err);
          allApplications[job.job_id] = [];
        }
      }
      setApplications(allApplications);
    } catch (err: any) {
      console.error('Error loading applications:', err);
      // Don't show error to user, just log it
      setJobs([]);
      setApplications({});
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateStatus = async (
    applicationId: number,
    jobId: number,
    status: 'accepted' | 'rejected'
  ) => {
    try {
      const userId = TokenStorage.getUserId();
      if (!userId) return;

      await JobService.updateApplicationStatus(applicationId, userId, status);

      // Refresh applications for this job
      const updatedApps = await JobService.getJobApplications(jobId, userId);
      setApplications((prev) => ({
        ...prev,
        [jobId]: updatedApps,
      }));

      showSuccess(`Application ${status} successfully!`);
    } catch (err: any) {
      showError(err.message || 'Failed to update application');
    }
  };

  const getStatusBadgeClass = (status: string) => {
    switch (status) {
      case 'accepted':
        return styles.statusAccepted;
      case 'rejected':
        return styles.statusRejected;
      default:
        return styles.statusPending;
    }
  };

  if (loading) {
    return (
      <div className={styles.container}>
        <div className={styles.loading}>Loading applications...</div>
      </div>
    );
  }

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <button className={styles.backButton} onClick={() => navigate('/home')}>
          ← Back
        </button>
        <h1>Job Applications</h1>
      </div>

      {error && <div className={styles.error}>{error}</div>}

      {jobs.length === 0 ? (
        <Card>
          <div className={styles.empty}>
            <p>You haven't posted any jobs yet.</p>
            <Button onClick={() => navigate('/post-job')}>Post Your First Job</Button>
          </div>
        </Card>
      ) : (
        <div className={styles.jobsList}>
          {jobs.map((job) => (
            <Card key={job.job_id}>
              <div className={styles.jobHeader}>
                <h2>{job.title}</h2>
                <span className={styles.applicationsCount}>
                  {applications[job.job_id]?.length || 0} application(s)
                </span>
              </div>
              <p className={styles.jobDescription}>{job.description}</p>

              {applications[job.job_id] && applications[job.job_id].length > 0 ? (
                <div className={styles.applicationsList}>
                  <h3>Applications:</h3>
                  {applications[job.job_id].map((app) => (
                    <div key={app.application_id} className={styles.applicationCard}>
                      <div className={styles.applicationHeader}>
                        <span className={styles.employeeId}>
                          {app.employee_profile?.username || `Employee ID: ${app.employee_id}`}
                        </span>
                        <span className={`${styles.statusBadge} ${getStatusBadgeClass(app.status)}`}>
                          {app.status}
                        </span>
                      </div>

                      {/* Employee Profile Information */}
                      {app.employee_profile && (
                        <div className={styles.employeeProfile}>
                          {app.employee_profile.email && (
                            <div className={styles.profileItem}>
                              <strong>📧 Email:</strong> {app.employee_profile.email}
                            </div>
                          )}
                          {app.employee_profile.phone && (
                            <div className={styles.profileItem}>
                              <strong>📱 Phone:</strong> {app.employee_profile.phone}
                            </div>
                          )}
                          {app.employee_profile.description && (
                            <div className={styles.profileItem}>
                              <strong>ℹ️ About:</strong> {app.employee_profile.description}
                            </div>
                          )}
                        </div>
                      )}

                      <div className={styles.applicationDetails}>
                        <div>
                          <strong>CV:</strong>{' '}
                          <a
                            href={`http://talentlink.local${app.cv_url}`}
                            target="_blank"
                            rel="noopener noreferrer"
                            className={styles.link}
                          >
                            View CV
                          </a>
                        </div>
                        {app.portfolio_url && (
                          <div>
                            <strong>Portfolio:</strong>{' '}
                            <a
                              href={app.portfolio_url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className={styles.link}
                            >
                              {app.portfolio_url}
                            </a>
                          </div>
                        )}
                        <div className={styles.applicationDate}>
                          Applied: {new Date(app.created_at).toLocaleDateString()}
                        </div>
                      </div>

                      {app.status === 'pending' && (
                        <div className={styles.actionButtons}>
                          <Button
                            variant="outlined"
                            onClick={() =>
                              handleUpdateStatus(app.application_id, job.job_id, 'accepted')
                            }
                          >
                            Accept
                          </Button>
                          <Button
                            variant="outlined"
                            onClick={() =>
                              handleUpdateStatus(app.application_id, job.job_id, 'rejected')
                            }
                          >
                            Reject
                          </Button>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <p className={styles.noApplications}>No applications yet</p>
              )}
            </Card>
          ))}
        </div>
      )}
    </div>
  );
};

export default ApplicationsScreen;
