import json
import os
from datetime import datetime

class ProfileManager:
    """Manages download profiles for series"""

    def __init__(self, profiles_file='profiles.json'):
        self.profiles_file = profiles_file
        self.profiles = self._load_profiles()

    def _load_profiles(self):
        """Load profiles from JSON file"""
        if os.path.exists(self.profiles_file):
            try:
                with open(self.profiles_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading profiles: {e}")
                return {}
        return {}

    def _save_profiles(self):
        """Save profiles to JSON file"""
        try:
            with open(self.profiles_file, 'w', encoding='utf-8') as f:
                json.dump(self.profiles, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving profiles: {e}")
            return False

    def save_profile(self, name, url, download_dir, quality='best', subtitle=True, download_type='single'):
        """Save or update a download profile"""
        profile_id = name.lower().replace(' ', '_')

        self.profiles[profile_id] = {
            'id': profile_id,
            'name': name,
            'url': url,
            'download_dir': download_dir,
            'quality': quality,
            'subtitle': subtitle,
            'download_type': download_type,
            'created_at': self.profiles.get(profile_id, {}).get('created_at', datetime.now().isoformat()),
            'updated_at': datetime.now().isoformat()
        }

        if self._save_profiles():
            return {'success': True, 'profile': self.profiles[profile_id]}
        else:
            return {'success': False, 'error': 'Failed to save profile'}

    def get_profile(self, profile_id):
        """Get a specific profile by ID"""
        if profile_id in self.profiles:
            return {'success': True, 'profile': self.profiles[profile_id]}
        else:
            return {'success': False, 'error': 'Profile not found'}

    def get_all_profiles(self):
        """Get all profiles"""
        return {
            'success': True,
            'profiles': list(self.profiles.values())
        }

    def delete_profile(self, profile_id):
        """Delete a profile"""
        if profile_id in self.profiles:
            del self.profiles[profile_id]
            if self._save_profiles():
                return {'success': True, 'message': 'Profile deleted'}
            else:
                return {'success': False, 'error': 'Failed to delete profile'}
        else:
            return {'success': False, 'error': 'Profile not found'}

    def search_profiles(self, query):
        """Search profiles by name"""
        query_lower = query.lower()
        results = [
            profile for profile in self.profiles.values()
            if query_lower in profile['name'].lower()
        ]
        return {
            'success': True,
            'profiles': results
        }
