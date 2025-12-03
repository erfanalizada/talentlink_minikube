/// User profile model
/// Single Responsibility: Represents user profile data
class UserProfile {
  final String userId;
  final String username;
  final String email;
  final UserRole role;
  final String? description;
  final String? phoneNumber;
  final String? secondaryEmail;
  final String? address;
  final String? profilePictureUrl;
  final DateTime? createdAt;
  final DateTime? updatedAt;

  UserProfile({
    required this.userId,
    required this.username,
    required this.email,
    required this.role,
    this.description,
    this.phoneNumber,
    this.secondaryEmail,
    this.address,
    this.profilePictureUrl,
    this.createdAt,
    this.updatedAt,
  });

  factory UserProfile.fromJson(Map<String, dynamic> json) {
    return UserProfile(
      userId: json['user_id'] ?? '',
      username: json['username'] ?? '',
      email: json['email'] ?? '',
      role: UserRole.fromString(json['role']),
      description: json['description'],
      phoneNumber: json['phone_number'],
      secondaryEmail: json['secondary_email'],
      address: json['address'],
      profilePictureUrl: json['profile_picture_url'],
      createdAt: json['created_at'] != null
          ? DateTime.tryParse(json['created_at'])
          : null,
      updatedAt: json['updated_at'] != null
          ? DateTime.tryParse(json['updated_at'])
          : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'user_id': userId,
      'username': username,
      'email': email,
      'role': role.value,
      'description': description,
      'phone_number': phoneNumber,
      'secondary_email': secondaryEmail,
      'address': address,
      'profile_picture_url': profilePictureUrl,
    };
  }

  UserProfile copyWith({
    String? userId,
    String? username,
    String? email,
    UserRole? role,
    String? description,
    String? phoneNumber,
    String? secondaryEmail,
    String? address,
    String? profilePictureUrl,
  }) {
    return UserProfile(
      userId: userId ?? this.userId,
      username: username ?? this.username,
      email: email ?? this.email,
      role: role ?? this.role,
      description: description ?? this.description,
      phoneNumber: phoneNumber ?? this.phoneNumber,
      secondaryEmail: secondaryEmail ?? this.secondaryEmail,
      address: address ?? this.address,
      profilePictureUrl: profilePictureUrl ?? this.profilePictureUrl,
      createdAt: createdAt,
      updatedAt: DateTime.now(),
    );
  }
}

enum UserRole {
  employee,
  employer;

  String get value => name;

  static UserRole fromString(String? value) {
    switch (value?.toLowerCase()) {
      case 'employee':
        return UserRole.employee;
      case 'employer':
        return UserRole.employer;
      default:
        return UserRole.employee;
    }
  }
}
