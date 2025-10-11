import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

void main() {
  runApp(const MaterialApp(
    debugShowCheckedModeBanner: false,
    home: ServiceHealthPage(),
  ));
}

class ServiceHealthPage extends StatefulWidget {
  const ServiceHealthPage({super.key});

  @override
  State<ServiceHealthPage> createState() => _ServiceHealthPageState();
}

class _ServiceHealthPageState extends State<ServiceHealthPage> {
  final Map<String, String> _results = {};

  // List of services and endpoints to check
  final List<Map<String, String>> _services = [
    {"name": "Auth Service", "url": "/api/auth/health"},
    {"name": "User Service", "url": "/api/users/health"},
    {"name": "Job Service", "url": "/api/jobs/health"},
    {"name": "CV Service", "url": "/api/cv/health"},
    {"name": "Matching Service", "url": "/api/matching/health"},
    {"name": "Notification Service", "url": "/api/notifications/health"},
  ];

  Future<void> _checkHealth(String name, String url) async {
    setState(() => _results[name] = "⏳ Checking...");
    try {
      final res = await http.get(Uri.parse(url));
      if (res.statusCode == 200) {
        setState(() => _results[name] = "✅ OK: ${res.body}");
      } else {
        setState(() => _results[name] = "❌ Error ${res.statusCode}");
      }
    } catch (e) {
      setState(() => _results[name] = "⚠️ Failed: $e");
    }
  }

  Future<void> _checkAll() async {
    for (var svc in _services) {
      await _checkHealth(svc["name"]!, svc["url"]!);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("TalentLink Service Health")),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: ListView(
          children: [
            ElevatedButton(
              onPressed: _checkAll,
              child: const Text("🔄 Check All Services"),
            ),
            const SizedBox(height: 20),
            ..._services.map((svc) {
              final name = svc["name"]!;
              final url = svc["url"]!;
              final status = _results[name] ?? "Not checked yet";
              return Card(
                margin: const EdgeInsets.symmetric(vertical: 6),
                child: ListTile(
                  title: Text(name),
                  subtitle: Text(status),
                  trailing: IconButton(
                    icon: const Icon(Icons.refresh),
                    onPressed: () => _checkHealth(name, url),
                  ),
                ),
              );
            }),
          ],
        ),
      ),
    );
  }
}
