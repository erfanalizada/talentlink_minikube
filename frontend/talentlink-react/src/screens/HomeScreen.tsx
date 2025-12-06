import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { TokenStorage } from '../services/tokenStorage';
import { UserService } from '../services/userService';
import { JobService } from '../services/jobService';
import { Job } from '../types/job';
import { UserRole } from '../types/user';
import { Card } from '../components/Card';
import { Button } from '../components/Button';
import { useMessageBox } from '../hooks/useMessageBox';
import styles from './HomeScreen.module.css';

export const HomeScreen: React.FC = () => {
  const navigate = useNavigate();
  const { showSuccess } = useMessageBox();
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [username, setUsername] = useState<string>('Loading...');
  const [userRole, setUserRole] = useState<UserRole | null>(null);
  const [profilePictureUrl, setProfilePictureUrl] = useState<string | null>(null);
  const [jobs, setJobs] = useState<Job[]>([]);
  const [myJobs, setMyJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedJob, setSelectedJob] = useState<Job | null>(null);
  const [showApplicationModal, setShowApplicationModal] = useState(false);
  const [deletingJobId, setDeletingJobId] = useState<number | null>(null);

  useEffect(() => {
    loadUserInfo();
    loadJobs();
  }, [userRole]);

  const loadUserInfo = async () => {
    const decodedToken = TokenStorage.getDecodedToken();
    if (decodedToken) {
      setUsername(decodedToken.preferred_username || 'User');

      // Get user role from token
      const roles = decodedToken.realm_access?.roles || [];
      if (roles.includes('employer')) {
        setUserRole(UserRole.EMPLOYER);
      } else if (roles.includes('employee')) {
        setUserRole(UserRole.EMPLOYEE);
      }

      // Load profile picture
      const userId = TokenStorage.getUserId();
      if (userId) {
        try {
          const profile = await UserService.loadProfile(userId);
          setProfilePictureUrl(profile.profilePictureUrl || null);
          console.log('📷 Loaded profile picture URL:', profile.profilePictureUrl);
        } catch (err) {
          console.error('Failed to load profile picture:', err);
        }
      }
    }
  };

  const loadJobs = async () => {
    try {
      setLoading(true);
      const userId = TokenStorage.getUserId();

      // Load all jobs for everyone
      const allJobs = await JobService.getAllJobs();
      setJobs(allJobs);

      // If employer, also load their own jobs
      if (userRole === UserRole.EMPLOYER && userId) {
        const employerJobs = await JobService.getJobsByEmployer(userId);
        setMyJobs(employerJobs);
      }
    } catch (err) {
      console.error('Failed to load jobs', err);
      // Set empty array on error so UI shows "no jobs" instead of error
      setJobs([]);
      setMyJobs([]);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteJob = async (jobId: number) => {
    const confirmed = window.confirm('Are you sure you want to delete this job? This action cannot be undone.');
    if (!confirmed) return;

    try {
      setDeletingJobId(jobId);
      const userId = TokenStorage.getUserId();
      if (!userId) {
        showSuccess('User not authenticated');
        return;
      }

      await JobService.deleteJob(jobId, userId);
      showSuccess('Job deleted successfully!');

      // Reload jobs
      loadJobs();
    } catch (err: any) {
      showSuccess(err.message || 'Failed to delete job');
    } finally {
      setDeletingJobId(null);
    }
  };

  const handleLogout = () => {
    TokenStorage.clearTokens();
    navigate('/login');
  };

  const handleNavigateToProfile = async () => {
    setDrawerOpen(false);
    const userId = TokenStorage.getUserId();
    if (userId) {
      navigate('/profile');
    }
  };

  const handleApplyClick = (job: Job) => {
    setSelectedJob(job);
    setShowApplicationModal(true);
  };

  const closeDrawer = () => {
    setDrawerOpen(false);
  };

  return (
    <div className={styles.container}>
      {/* App Bar */}
      <div className={styles.appBar}>
        <div className={styles.appBarLeft}>
          <button className={styles.menuButton} onClick={() => setDrawerOpen(true)}>
            ☰
          </button>
          <h1 className={styles.title}>TalentLink</h1>
        </div>
      </div>

      {/* Main Content */}
      <div className={styles.content}>
        {/* My Jobs Section (Employer Only) */}
        {userRole === UserRole.EMPLOYER && (
          <div className={styles.jobsSection}>
            <h2 className={styles.sectionTitle}>My Posted Jobs</h2>

            {loading ? (
              <div className={styles.loading}>Loading your jobs...</div>
            ) : myJobs.length === 0 ? (
              <Card>
                <div className={styles.empty}>
                  <p>You haven't posted any jobs yet.</p>
                  <Button onClick={() => navigate('/post-job')}>Post Your First Job</Button>
                </div>
              </Card>
            ) : (
              <div className={styles.jobsList}>
                {myJobs.map((job) => (
                  <Card key={job.job_id}>
                    <div className={styles.jobCard}>
                      <div className={styles.jobHeader}>
                        <h3>{job.title}</h3>
                        {job.salary && (
                          <span className={styles.salary}>${job.salary.toLocaleString()}</span>
                        )}
                      </div>
                      <p className={styles.jobDescription}>{job.description}</p>
                      {job.skills && job.skills.length > 0 && (
                        <div className={styles.skillsContainer}>
                          {job.skills.map((skill, index) => (
                            <span key={index} className={styles.skillBadge}>
                              {skill}
                            </span>
                          ))}
                        </div>
                      )}
                      <div className={styles.jobFooter}>
                        <span className={styles.postedDate}>
                          Posted {new Date(job.created_at).toLocaleDateString()}
                        </span>
                        <div className={styles.jobActions}>
                          <Button
                            variant="outlined"
                            onClick={() => handleDeleteJob(job.job_id)}
                            loading={deletingJobId === job.job_id}
                          >
                            🗑️ Delete
                          </Button>
                        </div>
                      </div>
                    </div>
                  </Card>
                ))}
              </div>
            )}
          </div>
        )}

        {/* All Jobs Section - Only show for employees */}
        {userRole === UserRole.EMPLOYEE && (
          <div className={styles.jobsSection}>
            <h2 className={styles.sectionTitle}>Available Jobs</h2>

            {loading ? (
              <div className={styles.loading}>Loading jobs...</div>
            ) : jobs.length === 0 ? (
              <Card>
                <div className={styles.empty}>
                  <p>No jobs available at the moment.</p>
                </div>
              </Card>
            ) : (
              <div className={styles.jobsList}>
                {jobs.map((job) => (
                  <Card key={job.job_id}>
                    <div className={styles.jobCard}>
                      <div className={styles.jobHeader}>
                        <h3>{job.title}</h3>
                        {job.salary && (
                          <span className={styles.salary}>${job.salary.toLocaleString()}</span>
                        )}
                      </div>
                      <p className={styles.jobDescription}>{job.description}</p>
                      {job.skills && job.skills.length > 0 && (
                        <div className={styles.skillsContainer}>
                          {job.skills.map((skill, index) => (
                            <span key={index} className={styles.skillBadge}>
                              {skill}
                            </span>
                          ))}
                        </div>
                      )}
                      <div className={styles.jobFooter}>
                        <span className={styles.postedDate}>
                          Posted {new Date(job.created_at).toLocaleDateString()}
                        </span>
                        <Button onClick={() => handleApplyClick(job)}>Apply Now</Button>
                      </div>
                    </div>
                  </Card>
                ))}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Application Modal */}
      {showApplicationModal && selectedJob && (
        <ApplicationModal
          job={selectedJob}
          onClose={() => {
            setShowApplicationModal(false);
            setSelectedJob(null);
          }}
          onSuccess={() => {
            setShowApplicationModal(false);
            setSelectedJob(null);
            showSuccess('Application submitted successfully!');
          }}
        />
      )}

      {/* Drawer Overlay */}
      <div
        className={`${styles.drawerOverlay} ${drawerOpen ? styles.open : ''}`}
        onClick={closeDrawer}
      />

      {/* Drawer */}
      <div className={`${styles.drawer} ${drawerOpen ? styles.open : ''}`}>
        <div className={styles.drawerHeader}>
          <div className={styles.avatar}>
            {profilePictureUrl ? (
              <img
                src={`http://talentlink.local${profilePictureUrl}`}
                alt="Profile"
                style={{ width: '100%', height: '100%', objectFit: 'cover', borderRadius: '50%' }}
                onError={(e) => {
                  console.error('❌ Failed to load drawer profile picture:', profilePictureUrl);
                  (e.target as HTMLImageElement).style.display = 'none';
                  (e.target as HTMLImageElement).parentElement!.innerHTML = '<span>👤</span>';
                }}
              />
            ) : (
              <span>👤</span>
            )}
          </div>
          <div className={styles.username}>{username}</div>
          {userRole && (
            <div className={styles.roleBadge}>
              {userRole === UserRole.EMPLOYER ? 'Employer' : 'Employee'}
            </div>
          )}
        </div>

        <ul className={styles.drawerMenu}>
          <li>
            <button className={styles.drawerItem} onClick={closeDrawer}>
              <span className={styles.drawerItemIcon}>🏠</span>
              <span>Home</span>
            </button>
          </li>
          <li>
            <button className={styles.drawerItem} onClick={handleNavigateToProfile}>
              <span className={styles.drawerItemIcon}>👤</span>
              <span>Profile</span>
            </button>
          </li>

          {/* Employer-specific menu items */}
          {userRole === UserRole.EMPLOYER && (
            <>
              <li>
                <button
                  className={styles.drawerItem}
                  onClick={() => {
                    setDrawerOpen(false);
                    navigate('/post-job');
                  }}
                >
                  <span className={styles.drawerItemIcon}>📝</span>
                  <span>Post a Job</span>
                </button>
              </li>
              <li>
                <button
                  className={styles.drawerItem}
                  onClick={() => {
                    setDrawerOpen(false);
                    navigate('/applications');
                  }}
                >
                  <span className={styles.drawerItemIcon}>📋</span>
                  <span>View Applications</span>
                </button>
              </li>
            </>
          )}

          {/* Employee-specific menu items */}
          {userRole === UserRole.EMPLOYEE && (
            <li>
              <button
                className={styles.drawerItem}
                onClick={() => {
                  setDrawerOpen(false);
                  navigate('/my-applications');
                }}
              >
                <span className={styles.drawerItemIcon}>📄</span>
                <span>My Applications</span>
              </button>
            </li>
          )}

          <li>
            <div className={styles.drawerDivider} />
          </li>
          <li>
            <button
              className={`${styles.drawerItem} ${styles.logoutItem}`}
              onClick={handleLogout}
            >
              <span className={styles.logoutIcon}>🚪</span>
              <span>Logout</span>
            </button>
          </li>
        </ul>
      </div>
    </div>
  );
};

// Application Modal Component
interface ApplicationModalProps {
  job: Job;
  onClose: () => void;
  onSuccess: () => void;
}

const ApplicationModal: React.FC<ApplicationModalProps> = ({ job, onClose, onSuccess }) => {
  const [cvFile, setCvFile] = useState<File | null>(null);
  const [portfolioUrl, setPortfolioUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleCvChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setCvFile(e.target.files[0]);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (!cvFile) {
      setError('Please upload your CV');
      return;
    }

    setLoading(true);
    try {
      const userId = TokenStorage.getUserId();
      if (!userId) {
        setError('User not authenticated');
        return;
      }

      // Convert CV to base64
      const cvBase64 = await JobService.fileToBase64(cvFile);

      await JobService.applyToJob(job.job_id, {
        employee_id: userId,
        cv: cvBase64,
        portfolio_url: portfolioUrl || undefined,
      });

      onSuccess();
    } catch (err: any) {
      setError(err.message || 'Failed to submit application');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={styles.modalOverlay} onClick={onClose}>
      <div className={styles.modal} onClick={(e) => e.stopPropagation()}>
        <div className={styles.modalHeader}>
          <h2>Apply to {job.title}</h2>
          <button className={styles.closeButton} onClick={onClose}>
            ×
          </button>
        </div>

        <form onSubmit={handleSubmit} className={styles.modalForm}>
          {error && <div className={styles.error}>{error}</div>}

          <div className={styles.formGroup}>
            <label htmlFor="cv">Upload CV (Required) *</label>
            <input
              type="file"
              id="cv"
              accept=".pdf,.doc,.docx"
              onChange={handleCvChange}
              className={styles.fileInput}
              required
            />
            {cvFile && <span className={styles.fileName}>{cvFile.name}</span>}
          </div>

          <div className={styles.formGroup}>
            <label htmlFor="portfolio">Portfolio URL (Optional)</label>
            <input
              type="url"
              id="portfolio"
              value={portfolioUrl}
              onChange={(e) => setPortfolioUrl(e.target.value)}
              placeholder="https://your-portfolio.com"
              className={styles.input}
            />
          </div>

          <div className={styles.modalActions}>
            <Button type="button" variant="outlined" onClick={onClose}>
              Cancel
            </Button>
            <Button type="submit" loading={loading}>
              Submit Application
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
};
