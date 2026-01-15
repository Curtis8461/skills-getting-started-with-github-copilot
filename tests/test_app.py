"""
Tests for the Mergington High School Activities API
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


class TestGetActivities:
    """Tests for the GET /activities endpoint"""
    
    def test_get_activities_returns_dict(self, client):
        """Test that GET /activities returns a dictionary"""
        response = client.get("/activities")
        assert response.status_code == 200
        assert isinstance(response.json(), dict)
    
    def test_get_activities_contains_chess_club(self, client):
        """Test that activities include Chess Club"""
        response = client.get("/activities")
        activities = response.json()
        assert "Chess Club" in activities
    
    def test_get_activities_has_required_fields(self, client):
        """Test that each activity has required fields"""
        response = client.get("/activities")
        activities = response.json()
        
        for activity_name, activity_data in activities.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)


class TestSignupForActivity:
    """Tests for the POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_for_activity_success(self, client):
        """Test successful signup for an activity"""
        response = client.post(
            "/activities/Chess%20Club/signup?email=test@mergington.edu"
        )
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]
    
    def test_signup_already_registered(self, client):
        """Test that duplicate signup returns error"""
        email = "test_duplicate@mergington.edu"
        
        # First signup should succeed
        response1 = client.post(
            f"/activities/Programming%20Class/signup?email={email}"
        )
        assert response1.status_code == 200
        
        # Second signup should fail
        response2 = client.post(
            f"/activities/Programming%20Class/signup?email={email}"
        )
        assert response2.status_code == 400
        assert "already signed up" in response2.json()["detail"]
    
    def test_signup_activity_not_found(self, client):
        """Test signup for non-existent activity"""
        response = client.post(
            "/activities/Nonexistent%20Club/signup?email=test@mergington.edu"
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]
    
    def test_signup_updates_participants_list(self, client):
        """Test that signup adds participant to activities list"""
        email = "new_participant@mergington.edu"
        activity_name = "Art Studio"
        
        # Get initial participant count
        response1 = client.get("/activities")
        initial_count = len(response1.json()[activity_name]["participants"])
        
        # Sign up
        client.post(
            f"/activities/{activity_name.replace(' ', '%20')}/signup?email={email}"
        )
        
        # Get updated participant count
        response2 = client.get("/activities")
        updated_count = len(response2.json()[activity_name]["participants"])
        
        assert updated_count == initial_count + 1
        assert email in response2.json()[activity_name]["participants"]


class TestUnregisterFromActivity:
    """Tests for the POST /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_success(self, client):
        """Test successful unregistration from an activity"""
        email = "unregister_test@mergington.edu"
        activity_name = "Drama Club"
        
        # Sign up first
        client.post(
            f"/activities/{activity_name.replace(' ', '%20')}/signup?email={email}"
        )
        
        # Then unregister
        response = client.post(
            f"/activities/{activity_name.replace(' ', '%20')}/unregister?email={email}"
        )
        assert response.status_code == 200
        assert "Unregistered" in response.json()["message"]
    
    def test_unregister_not_registered(self, client):
        """Test unregistering someone not registered"""
        response = client.post(
            "/activities/Chess%20Club/unregister?email=notregistered@mergington.edu"
        )
        assert response.status_code == 400
        assert "not registered" in response.json()["detail"]
    
    def test_unregister_activity_not_found(self, client):
        """Test unregistering from non-existent activity"""
        response = client.post(
            "/activities/Nonexistent%20Club/unregister?email=test@mergington.edu"
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]
    
    def test_unregister_removes_participant(self, client):
        """Test that unregister removes participant from activities list"""
        email = "remove_test@mergington.edu"
        activity_name = "Tennis Club"
        
        # Sign up
        client.post(
            f"/activities/{activity_name.replace(' ', '%20')}/signup?email={email}"
        )
        
        # Verify signup
        response1 = client.get("/activities")
        assert email in response1.json()[activity_name]["participants"]
        
        # Unregister
        client.post(
            f"/activities/{activity_name.replace(' ', '%20')}/unregister?email={email}"
        )
        
        # Verify removal
        response2 = client.get("/activities")
        assert email not in response2.json()[activity_name]["participants"]


class TestRootRedirect:
    """Tests for the root endpoint"""
    
    def test_root_redirects_to_static(self, client):
        """Test that root endpoint redirects to static/index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"
