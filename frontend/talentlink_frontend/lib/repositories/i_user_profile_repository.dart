import '../models/user_profile.dart';

/// Repository interface for user profile operations
/// Interface Segregation: Defines contract for profile data access
/// Dependency Inversion: Depend on abstraction, not implementation
abstract class IUserProfileRepository {
  Future<UserProfile> createProfile({
    required String userId,
    required String username,
    required String email,
    required UserRole role,
  });

  Future<UserProfile> getProfile(String userId);

  Future<UserProfile> updateProfile(
    String userId,
    Map<String, dynamic> updates,
  );

  Future<String> uploadProfilePicture(String userId, String base64Image);

  Future<void> deleteProfile(String userId);
}
