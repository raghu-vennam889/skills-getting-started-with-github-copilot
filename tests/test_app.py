"""
Tests for the Mergington High School Activities API.
Uses the AAA (Arrange-Act-Assert) pattern for test structure.
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app


client = TestClient(app)


class TestGetActivities:
    """Tests for GET /activities endpoint"""

    def test_get_activities_returns_all_activities(self):
        # Arrange: No setup needed, data is pre-populated in app
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        activities = response.json()
        assert isinstance(activities, dict)
        assert "Chess Club" in activities
        assert "Programming Class" in activities

    def test_get_activities_contains_activity_details(self):
        # Arrange
        # Act
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        chess_club = activities["Chess Club"]
        assert chess_club["description"] == "Learn strategies and compete in chess tournaments"
        assert chess_club["schedule"] == "Fridays, 3:30 PM - 5:00 PM"
        assert chess_club["max_participants"] == 12
        assert isinstance(chess_club["participants"], list)


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_successful(self):
        # Arrange
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Signed up {email} for {activity_name}"

    def test_signup_adds_participant_to_activity(self):
        # Arrange
        activity_name = "Programming Class"
        email = "frank@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert - Verify signup was successful
        assert response.status_code == 200
        
        # Verify participant is in the list
        activities_response = client.get("/activities")
        assert email in activities_response.json()[activity_name]["participants"]

    def test_signup_nonexistent_activity_returns_404(self):
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "student@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_signup_duplicate_participant_returns_400(self):
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already signed up
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 400
        assert response.json()["detail"] == "Student already signed up"


class TestRemoveFromActivity:
    """Tests for POST /activities/{activity_name}/remove endpoint"""

    def test_remove_participant_successful(self):
        # Arrange
        activity_name = "Gym Class"
        email = "john@mergington.edu"  # Already signed up
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/remove",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Removed {email} from {activity_name}"

    def test_remove_participant_actually_removes(self):
        # Arrange
        activity_name = "Art Studio"
        email = "mia@mergington.edu"  # Already signed up
        
        # Act - Remove participant
        response = client.post(
            f"/activities/{activity_name}/remove",
            params={"email": email}
        )
        
        # Assert - Verify removal was successful
        assert response.status_code == 200
        
        # Verify participant is no longer in the list
        activities_response = client.get("/activities")
        assert email not in activities_response.json()[activity_name]["participants"]

    def test_remove_from_nonexistent_activity_returns_404(self):
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "student@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/remove",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_remove_nonexistent_participant_returns_400(self):
        # Arrange
        activity_name = "Science Club"
        email = "notregistered@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/remove",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 400
        assert response.json()["detail"] == "Student not signed up for this activity"
