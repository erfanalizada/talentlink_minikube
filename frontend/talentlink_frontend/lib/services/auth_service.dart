import 'dart:convert';
import 'package:http/http.dart' as http;

class AuthService {
  // Use http://localhost:5000/api/auth if testing locally without Minikube
  static const String _baseUrl = "http://localhost:5000/api/auth";

  /// Login existing user
  Future<Map<String, dynamic>> login(String username, String password) async {
    final uri = Uri.parse("$_baseUrl/login");
    final response = await http.post(
      uri,
      headers: {"Content-Type": "application/json"},
      body: jsonEncode({"username": username, "password": password}),
    );

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      try {
        final decoded = jsonDecode(response.body);
        throw Exception(decoded['error'] ?? 'Login failed');
      } catch (_) {
        throw Exception('Login failed (status ${response.statusCode})');
      }
    }
  }

  /// Register new user
  Future<Map<String, dynamic>> register({
    required String username,
    required String email,
    required String password,
    required String role,
  }) async {
    final uri = Uri.parse("$_baseUrl/register");
    final response = await http.post(
      uri,
      headers: {"Content-Type": "application/json"},
      body: jsonEncode({
        "username": username,
        "email": email,
        "password": password,
        "role": role,
      }),
    );

    if (response.statusCode == 201) {
      return jsonDecode(response.body);
    } else {
      try {
        final decoded = jsonDecode(response.body);
        throw Exception(decoded['error'] ?? 'Registration failed');
      } catch (_) {
        throw Exception('Registration failed (status ${response.statusCode})');
      }
    }
  }

  Future<bool> checkHealth() async {
    try {
      final res = await http.get(Uri.parse("$_baseUrl/health"));
      return res.statusCode == 200;
    } catch (_) {
      return false;
    }
  }
}
