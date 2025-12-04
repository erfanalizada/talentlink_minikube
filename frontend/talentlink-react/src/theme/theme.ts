export const theme = {
  colors: {
    primaryBlue: '#2563EB',
    primaryDark: '#1E40AF',
    primaryLight: '#60A5FA',
    secondaryPurple: '#7C3AED',
    secondaryPink: '#EC4899',
    success: '#10B981',
    warning: '#F59E0B',
    error: '#EF4444',
    info: '#3B82F6',
    backgroundLight: '#F8FAFC',
    backgroundWhite: '#FFFFFF',
    cardBackground: '#FFFFFF',
    textPrimary: '#0F172A',
    textSecondary: '#64748B',
    textTertiary: '#94A3B8',
    border: '#E2E8F0',
    divider: '#F1F5F9',
  },
  gradients: {
    primary: 'linear-gradient(135deg, #2563EB 0%, #7C3AED 100%)',
    success: 'linear-gradient(135deg, #10B981 0%, #059669 100%)',
  },
  shadows: {
    card: '0 4px 10px rgba(0, 0, 0, 0.05)',
    button: '0 6px 12px rgba(37, 99, 235, 0.3)',
  },
  borderRadius: {
    small: '8px',
    medium: '12px',
    large: '16px',
    full: '9999px',
  },
  spacing: {
    xs: '4px',
    sm: '8px',
    md: '12px',
    lg: '16px',
    xl: '20px',
    xxl: '24px',
    xxxl: '32px',
  },
};

export type Theme = typeof theme;
