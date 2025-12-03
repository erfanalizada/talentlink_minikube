import 'dart:convert';
import 'package:http/http.dart' as http;

class AuthService {
  // Correct endpoint for Kubernetes Ingress
  static const String _baseUrl = "http://talentlink.local/api/auth";

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
      final decoded = jsonDecode(response.body);
      throw Exception(decoded['error'] ?? 'Login failed');
    }
  }

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
      final decoded = jsonDecode(response.body);
      throw Exception(decoded['error'] ?? 'Registration failed');
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
