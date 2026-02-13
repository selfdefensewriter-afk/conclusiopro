import requests
import sys
from datetime import datetime
import json
import os

BACKEND_URL = "https://conclusion-pro.preview.emergentagent.com"

class LegalAppTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session_token = None
        self.user_id = None
        self.tests_run = 0
        self.tests_passed = 0
        self.created_conclusion_id = None
        
    def log(self, message):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")
    
    def run_test(self, name, method, endpoint, expected_status, data=None, files=None):
        """Run a single API test"""
        url = f"{self.base_url}/api/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        if self.session_token:
            headers['Authorization'] = f'Bearer {self.session_token}'
        
        self.tests_run += 1
        self.log(f"🔍 Testing {name}...")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=30)
            elif method == 'POST':
                if files:
                    headers.pop('Content-Type', None)  # Let requests set this for multipart
                    response = requests.post(url, files=files, headers=headers, timeout=30)
                else:
                    response = requests.post(url, json=data, headers=headers, timeout=30)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=30)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=30)
            
            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                self.log(f"✅ {name} - Status: {response.status_code}")
                try:
                    return True, response.json()
                except:
                    return True, response.text
            else:
                self.log(f"❌ {name} - Expected {expected_status}, got {response.status_code}")
                self.log(f"Response: {response.text[:200]}")
                return False, {}
                
        except Exception as e:
            self.log(f"❌ {name} - Error: {str(e)}")
            return False, {}
    
    def setup_test_user(self):
        """Create test user in MongoDB"""
        self.log("🔧 Setting up test user in MongoDB...")
        
        try:
            import pymongo
            client = pymongo.MongoClient("mongodb://localhost:27017")
            db = client.test_database
            
            # Generate unique test data
            timestamp = int(datetime.now().timestamp())
            self.user_id = f"test-user-{timestamp}"
            self.session_token = f"test_session_{timestamp}"
            
            # Create user
            user_doc = {
                "user_id": self.user_id,
                "email": f"test.user.{timestamp}@example.com",
                "name": "Test User",
                "picture": "https://via.placeholder.com/150",
                "created_at": datetime.now()
            }
            db.users.insert_one(user_doc)
            
            # Create session
            session_doc = {
                "user_id": self.user_id,
                "session_token": self.session_token,
                "expires_at": datetime.now().replace(day=datetime.now().day + 7),
                "created_at": datetime.now()
            }
            db.user_sessions.insert_one(session_doc)
            
            self.log(f"✅ Test user created: {self.user_id}")
            self.log(f"✅ Session token: {self.session_token}")
            return True
            
        except Exception as e:
            self.log(f"❌ Failed to setup test user: {str(e)}")
            self.log("⚠️  Continuing with API tests only...")
            return False
    
    def test_auth_endpoints(self):
        """Test authentication endpoints"""
        self.log("\n🔐 Testing Authentication Endpoints...")
        
        # Test /auth/me with valid token
        if self.session_token:
            success, response = self.run_test(
                "Get Current User (/auth/me)",
                "GET", "auth/me", 200
            )
            if success and 'user_id' in response:
                self.log(f"✅ User authenticated: {response.get('name', 'Unknown')}")
            
        # Test /auth/me without token (should fail)
        temp_token = self.session_token
        self.session_token = None
        self.run_test(
            "Get Current User (no auth)",
            "GET", "auth/me", 401
        )
        self.session_token = temp_token
        
        # Test logout
        if self.session_token:
            self.run_test(
                "Logout",
                "POST", "auth/logout", 200
            )
    
    def test_code_civil_endpoints(self):
        """Test Code Civil search endpoints"""
        self.log("\n📚 Testing Code Civil Endpoints...")
        
        if not self.session_token:
            self.log("⚠️ Skipping Code Civil tests - no auth token")
            return
            
        # Test search
        self.run_test(
            "Search Code Civil (famille)",
            "GET", "code-civil/search?q=famille", 200
        )
        
        self.run_test(
            "Search Code Civil (mariage)",
            "GET", "code-civil/search?q=mariage", 200
        )
        
        # Test get all articles
        self.run_test(
            "Get All Articles",
            "GET", "code-civil/articles", 200
        )
        
        self.run_test(
            "Get Articles by Category",
            "GET", "code-civil/articles?category=famille", 200
        )
    
    def test_conclusions_crud(self):
        """Test conclusions CRUD operations"""
        self.log("\n📝 Testing Conclusions CRUD...")
        
        if not self.session_token:
            self.log("⚠️ Skipping conclusions tests - no auth token")
            return
        
        # Test create conclusion
        conclusion_data = {
            "type": "jaf",
            "parties": {
                "demandeur": {
                    "nom": "MARTIN",
                    "prenom": "Jean",
                    "adresse": "123 Rue de la Paix, 75001 Paris"
                },
                "defendeur": {
                    "nom": "MARTIN",
                    "prenom": "Marie",
                    "adresse": "456 Avenue de la République, 75002 Paris"
                }
            },
            "faits": "Demande de garde alternée suite à divorce.",
            "demandes": "Garde alternée des enfants mineurs."
        }
        
        success, response = self.run_test(
            "Create Conclusion",
            "POST", "conclusions", 201, data=conclusion_data
        )
        
        if success and 'conclusion_id' in response:
            self.created_conclusion_id = response['conclusion_id']
            self.log(f"✅ Conclusion created: {self.created_conclusion_id}")
            
            # Test get single conclusion
            self.run_test(
                "Get Single Conclusion",
                "GET", f"conclusions/{self.created_conclusion_id}", 200
            )
            
            # Test update conclusion
            update_data = {
                "conclusion_text": "Conclusion mise à jour par les tests automatisés.",
                "status": "completed"
            }
            self.run_test(
                "Update Conclusion",
                "PUT", f"conclusions/{self.created_conclusion_id}", 200, data=update_data
            )
        
        # Test get all conclusions
        self.run_test(
            "Get All Conclusions",
            "GET", "conclusions", 200
        )
        
        # Test delete conclusion
        if self.created_conclusion_id:
            self.run_test(
                "Delete Conclusion",
                "DELETE", f"conclusions/{self.created_conclusion_id}", 200
            )
    
    def test_ai_generation(self):
        """Test AI conclusion generation"""
        self.log("\n🤖 Testing AI Generation...")
        
        if not self.session_token:
            self.log("⚠️ Skipping AI generation tests - no auth token")
            return
        
        # Test JAF conclusion generation
        jaf_data = {
            "type": "jaf",
            "parties": {
                "demandeur": {
                    "nom": "DUBOIS",
                    "prenom": "Pierre",
                    "adresse": "789 Rue du Test, 75003 Paris"
                },
                "defendeur": {
                    "nom": "DUBOIS",
                    "prenom": "Sophie",
                    "adresse": "321 Boulevard Automatisé, 75004 Paris"
                }
            },
            "faits": "Conflit sur la pension alimentaire suite à modification des revenus.",
            "demandes": "Révision du montant de la pension alimentaire."
        }
        
        success, response = self.run_test(
            "Generate JAF Conclusion",
            "POST", "generate/conclusion", 200, data=jaf_data
        )
        
        if success and 'conclusion_text' in response:
            conclusion_text = response['conclusion_text']
            self.log(f"✅ Generated conclusion ({len(conclusion_text)} chars)")
            
            # Check for key legal elements
            key_elements = ["PLAISE AU TRIBUNAL", "EN DROIT", "PAR CES MOTIFS", "DISPOSITIF"]
            found_elements = [elem for elem in key_elements if elem in conclusion_text.upper()]
            self.log(f"✅ Legal elements found: {found_elements}")
            
            if len(found_elements) >= 2:
                self.log("✅ AI generation produces properly structured legal document")
            else:
                self.log("⚠️ AI generation may not follow proper legal structure")
        
        # Test penal conclusion generation
        penal_data = {
            "type": "penal",
            "parties": {
                "demandeur": {
                    "nom": "LEROY",
                    "prenom": "Michel",
                    "adresse": "555 Place du Droit, 75005 Paris"
                }
            },
            "faits": "Vol de véhicule sans violence.",
            "demandes": "Relaxe ou peine avec sursis."
        }
        
        self.run_test(
            "Generate Penal Conclusion",
            "POST", "generate/conclusion", 200, data=penal_data
        )
    
    def test_pdf_export(self):
        """Test PDF export functionality"""
        self.log("\n📄 Testing PDF Export...")
        
        if not self.session_token:
            self.log("⚠️ Skipping PDF export tests - no auth token")
            return
        
        # First create a test conclusion
        conclusion_data = {
            "type": "jaf",
            "parties": {"test": "data"},
            "faits": "Test facts for PDF export",
            "demandes": "Test demands for PDF export"
        }
        
        success, response = self.run_test(
            "Create Test Conclusion for PDF",
            "POST", "conclusions", 201, data=conclusion_data
        )
        
        if success and 'conclusion_id' in response:
            conclusion_id = response['conclusion_id']
            
            # Update with some text
            update_data = {
                "conclusion_text": "This is a test conclusion for PDF export functionality."
            }
            self.run_test(
                "Update Conclusion Text",
                "PUT", f"conclusions/{conclusion_id}", 200, data=update_data
            )
            
            # Test PDF export
            try:
                url = f"{self.base_url}/api/conclusions/{conclusion_id}/pdf"
                headers = {'Authorization': f'Bearer {self.session_token}'}
                response = requests.get(url, headers=headers, timeout=30)
                
                if response.status_code == 200:
                    content_type = response.headers.get('content-type', '')
                    if 'pdf' in content_type.lower():
                        self.tests_passed += 1
                        self.log("✅ PDF Export - Generated PDF successfully")
                    else:
                        self.log(f"❌ PDF Export - Wrong content type: {content_type}")
                else:
                    self.log(f"❌ PDF Export - Status: {response.status_code}")
                
                self.tests_run += 1
                
            except Exception as e:
                self.log(f"❌ PDF Export - Error: {str(e)}")
                self.tests_run += 1
            
            # Clean up
            self.run_test(
                "Delete Test Conclusion",
                "DELETE", f"conclusions/{conclusion_id}", 200
            )
    
    def run_all_tests(self):
        """Run complete test suite"""
        self.log("🚀 Starting Legal App Backend Testing...")
        self.log(f"Backend URL: {self.base_url}")
        
        # Setup test data
        auth_setup = self.setup_test_user()
        
        # Run tests
        self.test_auth_endpoints()
        self.test_code_civil_endpoints()
        self.test_conclusions_crud()
        self.test_ai_generation()
        self.test_pdf_export()
        
        # Summary
        self.log(f"\n📊 Test Results:")
        self.log(f"Tests Run: {self.tests_run}")
        self.log(f"Tests Passed: {self.tests_passed}")
        self.log(f"Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%" if self.tests_run > 0 else "No tests run")
        
        if auth_setup:
            self.cleanup_test_data()
        
        return self.tests_passed, self.tests_run
    
    def cleanup_test_data(self):
        """Clean up test data"""
        try:
            import pymongo
            client = pymongo.MongoClient("mongodb://localhost:27017")
            db = client.test_database
            
            db.users.delete_many({"user_id": {"$regex": "^test-user-"}})
            db.user_sessions.delete_many({"session_token": {"$regex": "^test_session_"}})
            
            self.log("✅ Test data cleaned up")
        except Exception as e:
            self.log(f"⚠️ Cleanup error: {str(e)}")

def main():
    tester = LegalAppTester()
    passed, total = tester.run_all_tests()
    
    # Exit with appropriate code
    return 0 if passed == total and total > 0 else 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)