import { useContext } from 'react';
import { MessageBoxContext } from '../components/MessageBoxProvider';

export const useMessageBox = () => {
  const context = useContext(MessageBoxContext);

  if (!context) {
    throw new Error('useMessageBox must be used within a MessageBoxProvider');
  }

  return context;
};
