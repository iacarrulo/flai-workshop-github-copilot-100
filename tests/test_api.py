"""
Test suite for the High School Management System API
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities data before each test"""
    # Store original state
    original_activities = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Basketball Team": {
            "description": "Join the school basketball team and compete in inter-school tournaments",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 6:00 PM",
            "max_participants": 15,
            "participants": ["james@mergington.edu", "lucas@mergington.edu"]
        },
        "Swimming Club": {
            "description": "Develop swimming skills and train for competitions",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 25,
            "participants": ["ava@mergington.edu", "mia@mergington.edu"]
        },
        "Drama Club": {
            "description": "Participate in theatrical performances and learn acting skills",
            "schedule": "Wednesdays, 3:30 PM - 5:30 PM",
            "max_participants": 20,
            "participants": ["noah@mergington.edu", "isabella@mergington.edu"]
        },
        "Art Studio": {
            "description": "Explore painting, drawing, and various art mediums",
            "schedule": "Thursdays, 3:00 PM - 5:00 PM",
            "max_participants": 15,
            "participants": ["liam@mergington.edu", "charlotte@mergington.edu"]
        },
        "Debate Team": {
            "description": "Develop critical thinking and public speaking through competitive debates",
            "schedule": "Tuesdays, 3:30 PM - 5:00 PM",
            "max_participants": 16,
            "participants": ["ethan@mergington.edu", "amelia@mergington.edu"]
        },
        "Science Club": {
            "description": "Conduct experiments and explore scientific concepts through hands-on projects",
            "schedule": "Fridays, 3:00 PM - 4:30 PM",
            "max_participants": 18,
            "participants": ["william@mergington.edu", "harper@mergington.edu"]
        }
    }
    
    # Reset activities to original state
    activities.clear()
    activities.update(original_activities)
    yield


class TestRootEndpoint:
    """Tests for the root endpoint"""
    
    def test_root_redirects_to_static(self, client):
        """Test that root redirects to static index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestGetActivities:
    """Tests for GET /activities endpoint"""
    
    def test_get_activities_returns_all_activities(self, client):
        """Test that GET /activities returns all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 9
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Gym Class" in data
    
    def test_get_activities_includes_activity_details(self, client):
        """Test that activities include all required fields"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        
        chess_club = data["Chess Club"]
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club
        assert isinstance(chess_club["participants"], list)


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_for_valid_activity(self, client):
        """Test successful signup for an activity"""
        email = "test@mergington.edu"
        response = client.post("/activities/Chess Club/signup?email=" + email)
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == f"Signed up {email} for Chess Club"
        
        # Verify the student was added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email in activities_data["Chess Club"]["participants"]
    
    def test_signup_for_nonexistent_activity(self, client):
        """Test signup for an activity that doesn't exist"""
        response = client.post("/activities/Nonexistent Club/signup?email=test@mergington.edu")
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Activity not found"
    
    def test_signup_already_registered_student(self, client):
        """Test signup for an activity the student is already registered for"""
        email = "michael@mergington.edu"  # Already in Chess Club
        response = client.post("/activities/Chess Club/signup?email=" + email)
        assert response.status_code == 400
        data = response.json()
        assert data["detail"] == "Student already signed up for this activity"
    
    def test_signup_multiple_students_same_activity(self, client):
        """Test that multiple students can sign up for the same activity"""
        student1 = "student1@mergington.edu"
        student2 = "student2@mergington.edu"
        
        response1 = client.post(f"/activities/Chess Club/signup?email={student1}")
        assert response1.status_code == 200
        
        response2 = client.post(f"/activities/Chess Club/signup?email={student2}")
        assert response2.status_code == 200
        
        # Verify both were added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert student1 in activities_data["Chess Club"]["participants"]
        assert student2 in activities_data["Chess Club"]["participants"]
    
    def test_signup_student_multiple_activities(self, client):
        """Test that a student can sign up for multiple activities"""
        email = "multitasker@mergington.edu"
        
        response1 = client.post(f"/activities/Chess Club/signup?email={email}")
        assert response1.status_code == 200
        
        response2 = client.post(f"/activities/Drama Club/signup?email={email}")
        assert response2.status_code == 200
        
        # Verify the student is in both activities
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email in activities_data["Chess Club"]["participants"]
        assert email in activities_data["Drama Club"]["participants"]


class TestUnregisterFromActivity:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_from_valid_activity(self, client):
        """Test successful unregistration from an activity"""
        email = "michael@mergington.edu"  # Already in Chess Club
        response = client.delete(f"/activities/Chess Club/unregister?email={email}")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == f"Unregistered {email} from Chess Club"
        
        # Verify the student was removed
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email not in activities_data["Chess Club"]["participants"]
    
    def test_unregister_from_nonexistent_activity(self, client):
        """Test unregistration from an activity that doesn't exist"""
        response = client.delete("/activities/Nonexistent Club/unregister?email=test@mergington.edu")
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Activity not found"
    
    def test_unregister_not_registered_student(self, client):
        """Test unregistration for a student not registered in the activity"""
        email = "notregistered@mergington.edu"
        response = client.delete(f"/activities/Chess Club/unregister?email={email}")
        assert response.status_code == 400
        data = response.json()
        assert data["detail"] == "Student not registered for this activity"
    
    def test_signup_then_unregister(self, client):
        """Test full lifecycle: signup and then unregister"""
        email = "temporary@mergington.edu"
        
        # Signup
        signup_response = client.post(f"/activities/Chess Club/signup?email={email}")
        assert signup_response.status_code == 200
        
        # Verify signup
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email in activities_data["Chess Club"]["participants"]
        
        # Unregister
        unregister_response = client.delete(f"/activities/Chess Club/unregister?email={email}")
        assert unregister_response.status_code == 200
        
        # Verify unregistration
        activities_response2 = client.get("/activities")
        activities_data2 = activities_response2.json()
        assert email not in activities_data2["Chess Club"]["participants"]
    
    def test_unregister_preserves_other_participants(self, client):
        """Test that unregistering one student doesn't affect others"""
        # Get initial participants
        initial_response = client.get("/activities")
        initial_data = initial_response.json()
        initial_participants = initial_data["Chess Club"]["participants"].copy()
        
        # Unregister one student
        email_to_remove = initial_participants[0]
        response = client.delete(f"/activities/Chess Club/unregister?email={email_to_remove}")
        assert response.status_code == 200
        
        # Verify other participants are still there
        final_response = client.get("/activities")
        final_data = final_response.json()
        final_participants = final_data["Chess Club"]["participants"]
        
        assert email_to_remove not in final_participants
        for participant in initial_participants[1:]:
            assert participant in final_participants


class TestActivityNameWithSpaces:
    """Tests for activity names with spaces in URLs"""
    
    def test_signup_activity_name_with_spaces(self, client):
        """Test that activity names with spaces work correctly in URLs"""
        email = "spacetester@mergington.edu"
        # FastAPI handles URL encoding automatically
        response = client.post(f"/activities/Chess Club/signup?email={email}")
        assert response.status_code == 200
    
    def test_unregister_activity_name_with_spaces(self, client):
        """Test unregister with activity names containing spaces"""
        email = "daniel@mergington.edu"  # Already in Chess Club
        response = client.delete(f"/activities/Chess Club/unregister?email={email}")
        assert response.status_code == 200


class TestEdgeCases:
    """Tests for edge cases and boundary conditions"""
    
    def test_get_activities_returns_fresh_data_after_signup(self, client):
        """Test that GET /activities returns updated data after modifications"""
        email = "newstudent@mergington.edu"
        
        # Get initial count
        initial_response = client.get("/activities")
        initial_count = len(initial_response.json()["Chess Club"]["participants"])
        
        # Signup
        client.post(f"/activities/Chess Club/signup?email={email}")
        
        # Get updated count
        updated_response = client.get("/activities")
        updated_count = len(updated_response.json()["Chess Club"]["participants"])
        
        assert updated_count == initial_count + 1
    
    def test_activity_names_are_case_sensitive(self, client):
        """Test that activity names are case-sensitive"""
        email = "test@mergington.edu"
        # Try with incorrect casing
        response = client.post(f"/activities/chess club/signup?email={email}")
        assert response.status_code == 404
