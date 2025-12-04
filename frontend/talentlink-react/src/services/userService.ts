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
      const token = TokenStorage.getAccessToken();
      const response = await axios.put<any>(
        `${BASE_URL}/profile/${userId}`,
        {
          description: updates.description,
          phone_number: updates.phoneNumber,
          secondary_email: updates.secondaryEmail,
          address: updates.address,
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
      throw new Error(error.response?.data?.error || 'Failed to update profile');
    }
  }

  static async uploadProfilePicture(userId: string, base64Image: string): Promise<string> {
    try {
      const token = TokenStorage.getAccessToken();
      const response = await axios.post<{ profile_picture_url: string }>(
        `${BASE_URL}/profile/${userId}/picture`,
        { image: base64Image },
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      return response.data.profile_picture_url;
    } catch (error: any) {
      throw new Error(error.response?.data?.error || 'Failed to upload profile picture');
    }
  }
}
