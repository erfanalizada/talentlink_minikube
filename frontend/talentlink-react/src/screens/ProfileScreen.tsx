import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { UserService } from '../services/userService';
import { TokenStorage } from '../services/tokenStorage';
import { UserProfile, UserRole } from '../types/user';
import { Card } from '../components/Card';
import { Input } from '../components/Input';
import styles from './ProfileScreen.module.css';

export const ProfileScreen: React.FC = () => {
  const navigate = useNavigate();
  const fileInputRef = useRef<HTMLInputElement>(null);

  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isEditing, setIsEditing] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const [description, setDescription] = useState('');
  const [phoneNumber, setPhoneNumber] = useState('');
  const [secondaryEmail, setSecondaryEmail] = useState('');
  const [address, setAddress] = useState('');
  const [tempImageUrl, setTempImageUrl] = useState<string | null>(null);

  useEffect(() => {
    loadProfile();
  }, []);

  const loadProfile = async () => {
    const userId = TokenStorage.getUserId();
    if (!userId) {
      navigate('/login');
      return;
    }

    try {
      const profileData = await UserService.loadProfile(userId);
      setProfile(profileData);
      setDescription(profileData.description || '');
      setPhoneNumber(profileData.phoneNumber || '');
      setSecondaryEmail(profileData.secondaryEmail || '');
      setAddress(profileData.address || '');
    } catch (e: any) {
      setError(e.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleImageSelect = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const userId = TokenStorage.getUserId();
    if (!userId) return;

    setIsSaving(true);
    setError(null);

    try {
      // Convert to base64
      const reader = new FileReader();
      reader.onloadend = async () => {
        const base64String = (reader.result as string).split(',')[1];

        try {
          const url = await UserService.uploadProfilePicture(userId, base64String);
          setProfile((prev) => (prev ? { ...prev, profilePictureUrl: url } : prev));
          setSuccess('Profile picture updated!');
          setTimeout(() => setSuccess(null), 3000);
        } catch (e: any) {
          setError(e.message);
        } finally {
          setIsSaving(false);
        }
      };
      reader.readAsDataURL(file);
    } catch (e: any) {
      setError(e.message);
      setIsSaving(false);
    }
  };

  const handleSaveProfile = async () => {
    const userId = TokenStorage.getUserId();
    if (!userId) return;

    setIsSaving(true);
    setError(null);

    try {
      const updatedProfile = await UserService.updateProfile(userId, {
        description,
        phoneNumber,
        secondaryEmail,
        address,
      });
      setProfile(updatedProfile);
      setIsEditing(false);
      setSuccess('Profile updated successfully!');
      setTimeout(() => setSuccess(null), 3000);
    } catch (e: any) {
      setError(e.message);
    } finally {
      setIsSaving(false);
    }
  };

  if (isLoading) {
    return (
      <div className={styles.container}>
        <div className={styles.appBar}>
          <div className={styles.appBarLeft}>
            <button className={styles.backButton} onClick={() => navigate('/home')}>
              ←
            </button>
            <h1 className={styles.title}>My Profile</h1>
          </div>
        </div>
        <div className={styles.loading}>Loading profile...</div>
      </div>
    );
  }

  if (!profile) {
    return (
      <div className={styles.container}>
        <div className={styles.appBar}>
          <div className={styles.appBarLeft}>
            <button className={styles.backButton} onClick={() => navigate('/home')}>
              ←
            </button>
            <h1 className={styles.title}>My Profile</h1>
          </div>
        </div>
        <div className={styles.loading}>No profile loaded</div>
      </div>
    );
  }

  return (
    <div className={styles.container}>
      <div className={styles.appBar}>
        <div className={styles.appBarLeft}>
          <button className={styles.backButton} onClick={() => navigate('/home')}>
            ←
          </button>
          <h1 className={styles.title}>My Profile</h1>
        </div>
        {!isEditing ? (
          <button className={styles.editButton} onClick={() => setIsEditing(true)}>
            Edit
          </button>
        ) : (
          <button
            className={styles.editButton}
            onClick={handleSaveProfile}
            disabled={isSaving}
          >
            {isSaving ? 'Saving...' : 'Save'}
          </button>
        )}
      </div>

      <div className={styles.content}>
        {/* Profile Picture */}
        <div className={styles.profilePictureSection}>
          <div className={styles.avatarWrapper}>
            <div className={styles.avatarContainer}>
              <div className={styles.avatar}>
                {profile.profilePictureUrl ? (
                  <img
                    src={profile.profilePictureUrl}
                    alt="Profile"
                    className={styles.avatarImage}
                  />
                ) : (
                  <span className={styles.avatarPlaceholder}>👤</span>
                )}
              </div>
            </div>
            {isEditing && (
              <>
                <button
                  className={styles.cameraButton}
                  onClick={() => fileInputRef.current?.click()}
                  disabled={isSaving}
                >
                  📷
                </button>
                <input
                  ref={fileInputRef}
                  type="file"
                  accept="image/*"
                  onChange={handleImageSelect}
                  className={styles.hiddenInput}
                />
              </>
            )}
          </div>
        </div>

        {/* Info Card */}
        <Card className={styles.infoCard}>
          <div className={styles.profileInfo}>
            <h2 className={styles.profileName}>{profile.username}</h2>
            <div
              className={`${styles.roleBadge} ${
                profile.role === UserRole.EMPLOYER
                  ? styles.employerBadge
                  : styles.employeeBadge
              }`}
            >
              {profile.role === UserRole.EMPLOYER ? 'Employer' : 'Employee'}
            </div>
            <div className={styles.infoRow}>
              <span>📧</span>
              <span>{profile.email}</span>
            </div>
          </div>
        </Card>

        {/* Details Card */}
        <Card className={styles.detailsCard}>
          <h3 className={styles.detailsTitle}>Details</h3>

          {error && (
            <div className={styles.errorMessage}>
              <span>⚠️</span>
              <span>{error}</span>
            </div>
          )}

          {success && (
            <div className={styles.successMessage}>
              <span>✅</span>
              <span>{success}</span>
            </div>
          )}

          <div style={{ marginBottom: '16px' }}>
            <label style={{ fontSize: '15px', fontWeight: 500, color: '#64748B', display: 'block', marginBottom: '8px' }}>
              About Me
            </label>
            <textarea
              className={styles.textArea}
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              disabled={!isEditing}
              placeholder="Tell us about yourself..."
            />
          </div>

          <Input
            label="Phone Number"
            value={phoneNumber}
            onChange={setPhoneNumber}
            icon={<span>📱</span>}
            disabled={!isEditing}
            placeholder="Phone number"
          />

          <Input
            label="Secondary Email"
            type="email"
            value={secondaryEmail}
            onChange={setSecondaryEmail}
            icon={<span>📧</span>}
            disabled={!isEditing}
            placeholder="Secondary email"
          />

          <div style={{ marginBottom: '0' }}>
            <label style={{ fontSize: '15px', fontWeight: 500, color: '#64748B', display: 'block', marginBottom: '8px' }}>
              Address
            </label>
            <textarea
              className={styles.textArea}
              value={address}
              onChange={(e) => setAddress(e.target.value)}
              disabled={!isEditing}
              placeholder="Your address..."
              style={{ minHeight: '80px', marginBottom: 0 }}
            />
          </div>
        </Card>
      </div>
    </div>
  );
};
