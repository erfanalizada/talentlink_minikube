import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { TokenStorage } from '../services/tokenStorage';
import styles from './HomeScreen.module.css';

export const HomeScreen: React.FC = () => {
  const navigate = useNavigate();
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [username, setUsername] = useState<string>('Loading...');

  useEffect(() => {
    loadUserInfo();
  }, []);

  const loadUserInfo = () => {
    const decodedToken = TokenStorage.getDecodedToken();
    if (decodedToken) {
      setUsername(decodedToken.preferred_username || 'User');
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
        <div className={styles.comingSoon}>
          <div className={styles.iconContainer}>
            <span className={styles.icon}>⏳</span>
          </div>
          <h2 className={styles.comingSoonTitle}>Coming Soon</h2>
          <p className={styles.comingSoonSubtitle}>
            We're working on something amazing.
            <br />
            Stay tuned!
          </p>
        </div>
      </div>

      {/* Drawer Overlay */}
      <div
        className={`${styles.drawerOverlay} ${drawerOpen ? styles.open : ''}`}
        onClick={closeDrawer}
      />

      {/* Drawer */}
      <div className={`${styles.drawer} ${drawerOpen ? styles.open : ''}`}>
        <div className={styles.drawerHeader}>
          <div className={styles.avatar}>
            <span>👤</span>
          </div>
          <div className={styles.username}>{username}</div>
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
