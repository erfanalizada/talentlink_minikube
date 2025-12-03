import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/user_profile.dart';
import 'i_user_profile_repository.dart';

/// HTTP implementation of user profile repository
/// Single Responsibility: Handles only HTTP API calls for profiles
/// Dependency Inversion: Implements interface, can be replaced with mock
class UserProfileRepository implements IUserProfileRepository {
  final String baseUrl;
  final http.Client client;

  UserProfileRepository({
    required this.baseUrl,
    http.Client? client,
  }) : client = client ?? http.Client();

  @override
  Future<UserProfile> createProfile({
    required String userId,
    required String username,
    required String email,
    required UserRole role,
  }) async {
    final uri = Uri.parse('$baseUrl/profile');
    final response = await client.post(
      uri,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'user_id': userId,
        'username': username,
        'email': email,
        'role': role.value,
      }),
    );

    if (response.statusCode == 201) {
      final data = jsonDecode(response.body);
      return UserProfile.fromJson(data['profile']);
    } else {
      final error = jsonDecode(response.body);
      throw Exception(error['error'] ?? 'Failed to create profile');
    }
  }

  @override
  Future<UserProfile> getProfile(String userId) async {
    final uri = Uri.parse('$baseUrl/profile/$userId');
    final response = await client.get(uri);

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      return UserProfile.fromJson(data['profile']);
    } else if (response.statusCode == 404) {
      throw ProfileNotFoundException('Profile not found');
    } else {
      final error = jsonDecode(response.body);
      throw Exception(error['error'] ?? 'Failed to get profile');
    }
  }

  @override
  Future<UserProfile> updateProfile(
    String userId,
    Map<String, dynamic> updates,
  ) async {
    final uri = Uri.parse('$baseUrl/profile/$userId');
    final response = await client.put(
      uri,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode(updates),
    );

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      return UserProfile.fromJson(data['profile']);
    } else if (response.statusCode == 404) {
      throw ProfileNotFoundException('Profile not found');
    } else {
      final error = jsonDecode(response.body);
      throw Exception(error['error'] ?? 'Failed to update profile');
    }
  }

  @override
  Future<String> uploadProfilePicture(String userId, String base64Image) async {
    final uri = Uri.parse('$baseUrl/profile/$userId/picture');
    final response = await client.post(
      uri,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'image': base64Image}),
    );

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      return data['url'];
    } else {
      final error = jsonDecode(response.body);
      throw Exception(error['error'] ?? 'Failed to upload picture');
    }
  }

  @override
  Future<void> deleteProfile(String userId) async {
    final uri = Uri.parse('$baseUrl/profile/$userId');
    final response = await client.delete(uri);

    if (response.statusCode != 200) {
      final error = jsonDecode(response.body);
      throw Exception(error['error'] ?? 'Failed to delete profile');
    }
  }
}

class ProfileNotFoundException implements Exception {
  final String message;
  ProfileNotFoundException(this.message);

  @override
  String toString() => message;
}
