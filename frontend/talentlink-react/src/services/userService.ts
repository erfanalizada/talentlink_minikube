import axios from 'axios';
import { UserProfile, UserRole } from '../types/user';
import { TokenStorage } from './tokenStorage';

const BASE_URL = 'http://talentlink.local/api/users';

export class UserService {
  static async loadProfile(userId: string): Promise<UserProfile> {
    try {
      const token = TokenStorage.getAccessToken();
      const response = await axios.get<any>(`${BASE_URL}/profile/${userId}`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      return {
        userId: response.data.user_id,
        username: response.data.username,
        email: response.data.email,
        role: response.data.role as UserRole,
        description: response.data.description,
        phoneNumber: response.data.phone_number,
        secondaryEmail: response.data.secondary_email,
        address: response.data.address,
        profilePictureUrl: response.data.profile_picture_url,
        createdAt: response.data.created_at,
        updatedAt: response.data.updated_at,
      };
    } catch (error: any) {
      throw new Error(error.response?.data?.error || 'Failed to load profile');
    }
  }

  static async createProfile(
    userId: string,
    username: string,
    email: string,
    role: UserRole
  ): Promise<UserProfile> {
    try {
      const token = TokenStorage.getAccessToken();
      const response = await axios.post<any>(
        `${BASE_URL}/profile`,
        {
          user_id: userId,
          username,
          email,
          role,
        },
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      return {
        userId: response.data.user_id,
        username: response.data.username,
        email: response.data.email,
        role: response.data.role as UserRole,
        description: response.data.description,
        phoneNumber: response.data.phone_number,
        secondaryEmail: response.data.secondary_email,
        address: response.data.address,
        profilePictureUrl: response.data.profile_picture_url,
        createdAt: response.data.created_at,
        updatedAt: response.data.updated_at,
      };
    } catch (error: any) {
      throw new Error(error.response?.data?.error || 'Failed to create profile');
    }
  }

  static async updateProfile(
    userId: string,
    updates: Partial<UserProfile>
  ): Promise<UserProfile> {
    try {
      console.log('🌐 UserService.updateProfile called');
      console.log('🌐 URL:', `${BASE_URL}/profile/${userId}`);
      console.log('🌐 Updates:', updates);

      const token = TokenStorage.getAccessToken();
      console.log('🌐 Token exists:', !!token);

      const requestBody = {
        description: updates.description,
        phone_number: updates.phoneNumber,
        secondary_email: updates.secondaryEmail,
        address: updates.address,
      };
      console.log('🌐 Request body:', requestBody);

      const response = await axios.put<any>(
        `${BASE_URL}/profile/${userId}`,
        requestBody,
        {
          headers: {
            Authorization: `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        }
      );

      console.log('🌐 Response status:', response.status);
      console.log('🌐 Response data:', response.data);

      return {
        userId: response.data.user_id,
        username: response.data.username,
        email: response.data.email,
        role: response.data.role as UserRole,
        description: response.data.description,
        phoneNumber: response.data.phone_number,
        secondaryEmail: response.data.secondary_email,
        address: response.data.address,
        profilePictureUrl: response.data.profile_picture_url,
        createdAt: response.data.created_at,
        updatedAt: response.data.updated_at,
      };
    } catch (error: any) {
      console.error('🌐 API Error:', error);
      console.error('🌐 Error response:', error.response?.data);
      console.error('🌐 Error status:', error.response?.status);
      throw new Error(error.response?.data?.error || 'Failed to update profile');
    }
  }

  static async uploadProfilePicture(userId: string, base64Image: string): Promise<string> {
    try {
      console.log('📷 UserService.uploadProfilePicture called');
      console.log('📷 URL:', `${BASE_URL}/profile/${userId}/picture`);
      console.log('📷 Base64 image length:', base64Image.length);

      const token = TokenStorage.getAccessToken();
      console.log('📷 Token exists:', !!token);

      const response = await axios.post<{ profile_picture_url: string }>(
        `${BASE_URL}/profile/${userId}/picture`,
        { image: base64Image },
        {
          headers: {
            Authorization: `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        }
      );

      console.log('📷 Response status:', response.status);
      console.log('📷 Response data:', response.data);
      console.log('📷 Profile picture URL:', response.data.profile_picture_url);

      return response.data.profile_picture_url;
    } catch (error: any) {
      console.error('📷 Upload error:', error);
      console.error('📷 Error response:', error.response?.data);
      throw new Error(error.response?.data?.error || 'Failed to upload profile picture');
    }
  }

  static async deleteProfile(userId: string): Promise<void> {
    try {
      console.log('🗑️ UserService.deleteProfile called');
      console.log('🗑️ URL:', `${BASE_URL}/profile/${userId}`);

      const token = TokenStorage.getAccessToken();
      console.log('🗑️ Token exists:', !!token);

      const response = await axios.delete(
        `${BASE_URL}/profile/${userId}`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      console.log('🗑️ Response status:', response.status);
      console.log('✅ Profile deleted successfully');
    } catch (error: any) {
      console.error('🗑️ Delete error:', error);
      console.error('🗑️ Error response:', error.response?.data);
      throw new Error(error.response?.data?.error || 'Failed to delete profile');
    }
  }
}
