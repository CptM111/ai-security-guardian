"""
Skill Marketplace Manager

Manages skill discovery, installation, updates, and ratings in the
AI Security Guardian Skill Marketplace.
"""

import json
import os
import shutil
import hashlib
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path

class SkillMarketplace:
    """Skill Marketplace Manager"""
    
    def __init__(self, registry_path: str = None, skills_dir: str = None):
        """
        Initialize marketplace
        
        Args:
            registry_path: Path to skills registry JSON
            skills_dir: Directory containing installed skills
        """
        self.base_dir = Path(__file__).parent.parent
        self.registry_path = registry_path or self.base_dir / "marketplace/registry/skills.json"
        self.skills_dir = skills_dir or self.base_dir / "skills"
        self.cache_dir = self.base_dir / "marketplace/.cache"
        
        # Create cache directory
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Load registry
        self.registry = self._load_registry()
    
    def _load_registry(self) -> Dict:
        """Load skills registry"""
        try:
            with open(self.registry_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {
                "version": "1.0.0",
                "skills": [],
                "categories": [],
                "featured_skills": [],
                "new_skills": [],
                "popular_skills": []
            }
    
    def _save_registry(self):
        """Save skills registry"""
        with open(self.registry_path, 'w') as f:
            json.dump(self.registry, f, indent=2)
    
    def list_skills(self, category: Optional[str] = None, 
                    status: Optional[str] = None) -> List[Dict]:
        """
        List available skills
        
        Args:
            category: Filter by category
            status: Filter by status (stable, beta, alpha)
            
        Returns:
            List of skill metadata
        """
        skills = self.registry.get('skills', [])
        
        # Apply filters
        if category:
            skills = [s for s in skills if s.get('category') == category]
        if status:
            skills = [s for s in skills if s.get('status') == status]
        
        return skills
    
    def search_skills(self, query: str) -> List[Dict]:
        """
        Search for skills
        
        Args:
            query: Search query
            
        Returns:
            Matching skills
        """
        query_lower = query.lower()
        results = []
        
        for skill in self.registry.get('skills', []):
            # Search in name, description, and tags
            if (query_lower in skill.get('name', '').lower() or
                query_lower in skill.get('description', '').lower() or
                any(query_lower in tag.lower() for tag in skill.get('tags', []))):
                results.append(skill)
        
        return results
    
    def get_skill(self, skill_id: str) -> Optional[Dict]:
        """
        Get skill details
        
        Args:
            skill_id: Skill identifier
            
        Returns:
            Skill metadata or None
        """
        for skill in self.registry.get('skills', []):
            if skill.get('id') == skill_id:
                return skill
        return None
    
    def is_installed(self, skill_id: str) -> bool:
        """
        Check if skill is installed
        
        Args:
            skill_id: Skill identifier
            
        Returns:
            True if installed
        """
        skill_path = self.skills_dir / skill_id
        return skill_path.exists() and (skill_path / "skill.yaml").exists()
    
    def get_installed_version(self, skill_id: str) -> Optional[str]:
        """
        Get installed skill version
        
        Args:
            skill_id: Skill identifier
            
        Returns:
            Version string or None
        """
        if not self.is_installed(skill_id):
            return None
        
        version_file = self.skills_dir / skill_id / "VERSION"
        if version_file.exists():
            return version_file.read_text().strip()
        return None
    
    def install_skill(self, skill_id: str, force: bool = False) -> Dict:
        """
        Install a skill
        
        Args:
            skill_id: Skill identifier
            force: Force reinstall if already installed
            
        Returns:
            Installation result
        """
        # Get skill metadata
        skill = self.get_skill(skill_id)
        if not skill:
            return {
                "success": False,
                "error": f"Skill '{skill_id}' not found in marketplace"
            }
        
        # Check if already installed
        if self.is_installed(skill_id) and not force:
            return {
                "success": False,
                "error": f"Skill '{skill_id}' is already installed. Use force=True to reinstall."
            }
        
        # In a real implementation, this would download from repository
        # For now, we assume skills are already in the skills directory
        skill_path = self.skills_dir / skill_id
        
        if not skill_path.exists():
            return {
                "success": False,
                "error": f"Skill directory not found: {skill_path}"
            }
        
        # Verify skill integrity
        if not self._verify_skill(skill_path):
            return {
                "success": False,
                "error": "Skill integrity verification failed"
            }
        
        # Install dependencies
        deps_result = self._install_dependencies(skill)
        if not deps_result['success']:
            return deps_result
        
        # Update installation record
        self._record_installation(skill_id, skill['version'])
        
        # Increment download count
        for s in self.registry['skills']:
            if s['id'] == skill_id:
                s['downloads'] = s.get('downloads', 0) + 1
                break
        self._save_registry()
        
        return {
            "success": True,
            "skill_id": skill_id,
            "version": skill['version'],
            "message": f"Successfully installed {skill['name']} v{skill['version']}"
        }
    
    def uninstall_skill(self, skill_id: str) -> Dict:
        """
        Uninstall a skill
        
        Args:
            skill_id: Skill identifier
            
        Returns:
            Uninstallation result
        """
        if not self.is_installed(skill_id):
            return {
                "success": False,
                "error": f"Skill '{skill_id}' is not installed"
            }
        
        # Remove skill directory
        skill_path = self.skills_dir / skill_id
        try:
            shutil.rmtree(skill_path)
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to remove skill directory: {str(e)}"
            }
        
        # Remove installation record
        self._remove_installation(skill_id)
        
        return {
            "success": True,
            "skill_id": skill_id,
            "message": f"Successfully uninstalled skill '{skill_id}'"
        }
    
    def update_skill(self, skill_id: str) -> Dict:
        """
        Update a skill to latest version
        
        Args:
            skill_id: Skill identifier
            
        Returns:
            Update result
        """
        if not self.is_installed(skill_id):
            return {
                "success": False,
                "error": f"Skill '{skill_id}' is not installed"
            }
        
        # Get current and latest versions
        current_version = self.get_installed_version(skill_id)
        skill = self.get_skill(skill_id)
        latest_version = skill['version']
        
        if current_version == latest_version:
            return {
                "success": True,
                "message": f"Skill '{skill_id}' is already at latest version {latest_version}",
                "updated": False
            }
        
        # Reinstall with latest version
        result = self.install_skill(skill_id, force=True)
        if result['success']:
            result['updated'] = True
            result['old_version'] = current_version
            result['new_version'] = latest_version
        
        return result
    
    def check_updates(self) -> List[Dict]:
        """
        Check for skill updates
        
        Returns:
            List of skills with available updates
        """
        updates = []
        
        for skill in self.registry.get('skills', []):
            skill_id = skill['id']
            if self.is_installed(skill_id):
                current_version = self.get_installed_version(skill_id)
                latest_version = skill['version']
                
                if current_version != latest_version:
                    updates.append({
                        'skill_id': skill_id,
                        'name': skill['name'],
                        'current_version': current_version,
                        'latest_version': latest_version
                    })
        
        return updates
    
    def rate_skill(self, skill_id: str, rating: float, review: Optional[str] = None) -> Dict:
        """
        Rate a skill
        
        Args:
            skill_id: Skill identifier
            rating: Rating (1.0 to 5.0)
            review: Optional review text
            
        Returns:
            Rating result
        """
        if not 1.0 <= rating <= 5.0:
            return {
                "success": False,
                "error": "Rating must be between 1.0 and 5.0"
            }
        
        skill = self.get_skill(skill_id)
        if not skill:
            return {
                "success": False,
                "error": f"Skill '{skill_id}' not found"
            }
        
        # In a real implementation, this would store ratings in a database
        # For now, we just update the average rating
        current_rating = skill.get('rating', 0.0)
        rating_count = skill.get('rating_count', 0)
        
        new_rating = ((current_rating * rating_count) + rating) / (rating_count + 1)
        
        for s in self.registry['skills']:
            if s['id'] == skill_id:
                s['rating'] = round(new_rating, 2)
                s['rating_count'] = rating_count + 1
                break
        
        self._save_registry()
        
        return {
            "success": True,
            "skill_id": skill_id,
            "new_rating": round(new_rating, 2),
            "rating_count": rating_count + 1
        }
    
    def get_categories(self) -> List[Dict]:
        """Get all skill categories"""
        return self.registry.get('categories', [])
    
    def get_featured_skills(self) -> List[Dict]:
        """Get featured skills"""
        featured_ids = self.registry.get('featured_skills', [])
        return [self.get_skill(sid) for sid in featured_ids if self.get_skill(sid)]
    
    def get_popular_skills(self, limit: int = 10) -> List[Dict]:
        """
        Get popular skills by download count
        
        Args:
            limit: Maximum number of skills to return
            
        Returns:
            List of popular skills
        """
        skills = self.registry.get('skills', [])
        sorted_skills = sorted(skills, key=lambda s: s.get('downloads', 0), reverse=True)
        return sorted_skills[:limit]
    
    def get_new_skills(self, limit: int = 10) -> List[Dict]:
        """
        Get newest skills
        
        Args:
            limit: Maximum number of skills to return
            
        Returns:
            List of new skills
        """
        skills = self.registry.get('skills', [])
        sorted_skills = sorted(skills, key=lambda s: s.get('created_at', ''), reverse=True)
        return sorted_skills[:limit]
    
    def _verify_skill(self, skill_path: Path) -> bool:
        """Verify skill integrity"""
        # Check required files
        required_files = ['skill.yaml', 'detector.py', 'VERSION']
        for file in required_files:
            if not (skill_path / file).exists():
                return False
        return True
    
    def _install_dependencies(self, skill: Dict) -> Dict:
        """Install skill dependencies"""
        # In a real implementation, this would install Python packages
        # For now, we just check if they're available
        deps = skill.get('dependencies', {}).get('python', [])
        
        if deps:
            # Log dependencies that need to be installed
            return {
                "success": True,
                "message": f"Dependencies to install: {', '.join(deps)}"
            }
        
        return {"success": True}
    
    def _record_installation(self, skill_id: str, version: str):
        """Record skill installation"""
        install_file = self.cache_dir / "installed.json"
        
        if install_file.exists():
            with open(install_file, 'r') as f:
                installed = json.load(f)
        else:
            installed = {}
        
        installed[skill_id] = {
            "version": version,
            "installed_at": datetime.now().isoformat()
        }
        
        with open(install_file, 'w') as f:
            json.dump(installed, f, indent=2)
    
    def _remove_installation(self, skill_id: str):
        """Remove installation record"""
        install_file = self.cache_dir / "installed.json"
        
        if install_file.exists():
            with open(install_file, 'r') as f:
                installed = json.load(f)
            
            if skill_id in installed:
                del installed[skill_id]
            
            with open(install_file, 'w') as f:
                json.dump(installed, f, indent=2)
    
    def get_marketplace_stats(self) -> Dict:
        """Get marketplace statistics"""
        skills = self.registry.get('skills', [])
        
        total_downloads = sum(s.get('downloads', 0) for s in skills)
        avg_rating = sum(s.get('rating', 0) for s in skills) / len(skills) if skills else 0
        
        return {
            "total_skills": len(skills),
            "total_categories": len(self.registry.get('categories', [])),
            "total_downloads": total_downloads,
            "average_rating": round(avg_rating, 2),
            "featured_skills": len(self.registry.get('featured_skills', [])),
            "new_skills": len(self.registry.get('new_skills', []))
        }
