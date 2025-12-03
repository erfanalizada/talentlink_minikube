import '../models/user_profile.dart';
import '../repositories/i_user_profile_repository.dart';

/// Service for managing user profile operations
/// Single Responsibility: Handles profile business logic
/// Dependency Inversion: Depends on repository interface
class UserService {
  final IUserProfileRepository repository;
  UserProfile? _currentProfile;

  UserService({required this.repository});

  UserProfile? get currentProfile => _currentProfile;

  Future<UserProfile> loadProfile(String userId) async {
    _currentProfile = await repository.getProfile(userId);
    return _currentProfile!;
  }

  Future<UserProfile> createProfile({
    required String userId,
    required String username,
    required String email,
    required UserRole role,
  }) async {
    _currentProfile = await repository.createProfile(
      userId: userId,
      username: username,
      email: email,
      role: role,
    );
    return _currentProfile!;
  }

  Future<UserProfile> updateProfile(Map<String, dynamic> updates) async {
    if (_currentProfile == null) {
      throw Exception('No profile loaded');
    }

    _currentProfile = await repository.updateProfile(
      _currentProfile!.userId,
      updates,
    );
    return _currentProfile!;
  }

  Future<String> uploadProfilePicture(String base64Image) async {
    if (_currentProfile == null) {
      throw Exception('No profile loaded');
    }

    final url = await repository.uploadProfilePicture(
      _currentProfile!.userId,
      base64Image,
    );

    // Update local profile with new picture URL
    _currentProfile = _currentProfile!.copyWith(profilePictureUrl: url);
    return url;
  }

  void clearProfile() {
    _currentProfile = null;
  }
}
