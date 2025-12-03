import 'dart:convert';
import 'dart:typed_data';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import '../models/user_profile.dart';
import '../services/user_service.dart';
import '../theme/app_theme.dart';

/// Profile screen for both employee and employer roles
/// Open/Closed: Can be extended without modification
class ProfileScreen extends StatefulWidget {
  final UserService userService;
  final UserProfile? initialProfile;

  const ProfileScreen({
    super.key,
    required this.userService,
    this.initialProfile,
  });

  @override
  State<ProfileScreen> createState() => _ProfileScreenState();
}

class _ProfileScreenState extends State<ProfileScreen> {
  final _formKey = GlobalKey<FormState>();
  final _descriptionController = TextEditingController();
  final _phoneController = TextEditingController();
  final _secondaryEmailController = TextEditingController();
  final _addressController = TextEditingController();

  bool _isLoading = false;
  bool _isEditing = false;
  String? _profilePictureUrl;
  Uint8List? _tempImageBytes;

  @override
  void initState() {
    super.initState();
    _loadInitialData();
  }

  void _loadInitialData() {
    final profile = widget.initialProfile ?? widget.userService.currentProfile;
    if (profile != null) {
      _descriptionController.text = profile.description ?? '';
      _phoneController.text = profile.phoneNumber ?? '';
      _secondaryEmailController.text = profile.secondaryEmail ?? '';
      _addressController.text = profile.address ?? '';
      _profilePictureUrl = profile.profilePictureUrl;
    }
  }

  Future<void> _pickImage() async {
    final ImagePicker picker = ImagePicker();
    final XFile? image = await picker.pickImage(
      source: ImageSource.gallery,
      maxWidth: 800,
      maxHeight: 800,
      imageQuality: 85,
    );

    if (image != null) {
      final bytes = await image.readAsBytes();
      setState(() {
        _tempImageBytes = bytes;
      });
    }
  }

  Future<void> _uploadImage() async {
    if (_tempImageBytes == null) return;

    setState(() => _isLoading = true);

    try {
      final base64Image = base64Encode(_tempImageBytes!);
      final url = await widget.userService.uploadProfilePicture(base64Image);

      setState(() {
        _profilePictureUrl = url;
        _tempImageBytes = null;
      });

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Profile picture updated!')),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error: ${e.toString()}')),
        );
      }
    } finally {
      setState(() => _isLoading = false);
    }
  }

  Future<void> _saveProfile() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() => _isLoading = true);

    try {
      await widget.userService.updateProfile({
        'description': _descriptionController.text.trim(),
        'phone_number': _phoneController.text.trim(),
        'secondary_email': _secondaryEmailController.text.trim(),
        'address': _addressController.text.trim(),
      });

      setState(() => _isEditing = false);

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Profile updated successfully!')),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error: ${e.toString()}')),
        );
      }
    } finally {
      setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final profile = widget.userService.currentProfile;
    if (profile == null) {
      return Scaffold(
        appBar: AppBar(title: const Text('Profile')),
        body: const Center(child: Text('No profile loaded')),
      );
    }

    return Scaffold(
      appBar: AppBar(
        title: const Text('My Profile'),
        actions: [
          if (!_isEditing)
            IconButton(
              icon: const Icon(Icons.edit),
              onPressed: () => setState(() => _isEditing = true),
            )
          else
            TextButton(
              onPressed: _isLoading ? null : _saveProfile,
              child: const Text('Save'),
            ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20),
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              _buildProfilePictureSection(),
              const SizedBox(height: 24),
              _buildInfoCard(profile),
              const SizedBox(height: 24),
              _buildDetailsSection(),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildProfilePictureSection() {
    return Center(
      child: Stack(
        children: [
          Container(
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              gradient: AppTheme.primaryGradient,
              boxShadow: AppTheme.cardShadow,
            ),
            padding: const EdgeInsets.all(4),
            child: CircleAvatar(
              radius: 60,
              backgroundColor: Colors.white,
              backgroundImage: _tempImageBytes != null
                  ? MemoryImage(_tempImageBytes!)
                  : _profilePictureUrl != null
                      ? NetworkImage(_profilePictureUrl!)
                      : null,
              child: _tempImageBytes == null && _profilePictureUrl == null
                  ? const Icon(Icons.person, size: 60, color: AppTheme.textSecondary)
                  : null,
            ),
          ),
          if (_isEditing)
            Positioned(
              bottom: 0,
              right: 0,
              child: Container(
                decoration: BoxDecoration(
                  color: AppTheme.primaryBlue,
                  shape: BoxShape.circle,
                  boxShadow: AppTheme.buttonShadow,
                ),
                child: IconButton(
                  icon: const Icon(Icons.camera_alt, color: Colors.white, size: 20),
                  onPressed: _isLoading ? null : () async {
                    await _pickImage();
                    if (_tempImageBytes != null) {
                      await _uploadImage();
                    }
                  },
                ),
              ),
            ),
        ],
      ),
    );
  }

  Widget _buildInfoCard(UserProfile profile) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          children: [
            Text(
              profile.username,
              style: Theme.of(context).textTheme.headlineMedium,
            ),
            const SizedBox(height: 8),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 6),
              decoration: BoxDecoration(
                gradient: profile.role == UserRole.employer
                    ? AppTheme.primaryGradient
                    : AppTheme.successGradient,
                borderRadius: BorderRadius.circular(20),
              ),
              child: Text(
                profile.role == UserRole.employer ? 'Employer' : 'Employee',
                style: const TextStyle(
                  color: Colors.white,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ),
            const SizedBox(height: 16),
            _buildInfoRow(Icons.email, profile.email),
          ],
        ),
      ),
    );
  }

  Widget _buildDetailsSection() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Details',
              style: Theme.of(context).textTheme.headlineSmall,
            ),
            const SizedBox(height: 20),
            _buildTextField(
              controller: _descriptionController,
              label: 'About Me',
              icon: Icons.info_outline,
              maxLines: 4,
              enabled: _isEditing,
            ),
            const SizedBox(height: 16),
            _buildTextField(
              controller: _phoneController,
              label: 'Phone Number',
              icon: Icons.phone,
              enabled: _isEditing,
              keyboardType: TextInputType.phone,
            ),
            const SizedBox(height: 16),
            _buildTextField(
              controller: _secondaryEmailController,
              label: 'Secondary Email',
              icon: Icons.alternate_email,
              enabled: _isEditing,
              keyboardType: TextInputType.emailAddress,
            ),
            const SizedBox(height: 16),
            _buildTextField(
              controller: _addressController,
              label: 'Address',
              icon: Icons.location_on,
              enabled: _isEditing,
              maxLines: 3,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildTextField({
    required TextEditingController controller,
    required String label,
    required IconData icon,
    bool enabled = true,
    int maxLines = 1,
    TextInputType? keyboardType,
  }) {
    return TextFormField(
      controller: controller,
      enabled: enabled,
      maxLines: maxLines,
      keyboardType: keyboardType,
      decoration: InputDecoration(
        labelText: label,
        prefixIcon: Icon(icon),
        filled: !enabled,
        fillColor: enabled ? Colors.white : AppTheme.backgroundLight,
      ),
    );
  }

  Widget _buildInfoRow(IconData icon, String text) {
    return Row(
      children: [
        Icon(icon, size: 18, color: AppTheme.textSecondary),
        const SizedBox(width: 8),
        Expanded(
          child: Text(
            text,
            style: Theme.of(context).textTheme.bodyMedium,
          ),
        ),
      ],
    );
  }

  @override
  void dispose() {
    _descriptionController.dispose();
    _phoneController.dispose();
    _secondaryEmailController.dispose();
    _addressController.dispose();
    super.dispose();
  }
}
