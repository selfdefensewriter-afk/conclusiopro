"""
Test suite for Pieces (Pièces jointes) API endpoints
Tests: POST/GET/PUT/DELETE /api/conclusions/{id}/pieces
       PUT /api/conclusions/{id}/pieces/reorder
       GET /api/pieces/{id}/download
"""
import pytest
import requests
import os
import io

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
SESSION_TOKEN = "test_session_pieces_1770651174398"
USER_ID = "test-user-pieces-1770651174398"

# Global state to track created resources for cleanup
created_conclusions = []
created_pieces = []

@pytest.fixture(scope="module")
def api_client():
    """Shared requests session with auth"""
    session = requests.Session()
    session.headers.update({
        "Content-Type": "application/json",
        "Authorization": f"Bearer {SESSION_TOKEN}"
    })
    session.cookies.set("session_token", SESSION_TOKEN)
    return session


@pytest.fixture(scope="module")
def test_conclusion(api_client):
    """Create a test conclusion for piece testing"""
    response = api_client.post(f"{BASE_URL}/api/conclusions", json={
        "type": "jaf",
        "parties": {
            "tribunal": "Test Tribunal",
            "numeroRG": "TEST-123",
            "demandeur": "Test Demandeur",
            "defendeur": "Test Defendeur"
        },
        "faits": "Test faits for pieces testing",
        "demandes": "Test demandes for pieces testing"
    })
    
    assert response.status_code in [200, 201], f"Failed to create test conclusion: {response.text}"
    conclusion = response.json()
    created_conclusions.append(conclusion["conclusion_id"])
    yield conclusion
    
    # Cleanup
    try:
        api_client.delete(f"{BASE_URL}/api/conclusions/{conclusion['conclusion_id']}")
    except:
        pass


class TestPiecesAuthentication:
    """Test authentication requirements for pieces endpoints"""
    
    def test_pieces_requires_auth(self):
        """Verify pieces endpoints require authentication"""
        response = requests.get(f"{BASE_URL}/api/conclusions/fake_id/pieces")
        assert response.status_code == 401, "Should require authentication"
        print("✅ Pieces endpoint requires authentication")


class TestPiecesUpload:
    """Test piece upload functionality"""
    
    def test_upload_piece_success(self, api_client, test_conclusion):
        """Test successful file upload with form data"""
        conclusion_id = test_conclusion["conclusion_id"]
        
        # Create a test file
        file_content = b"Test file content for piece upload testing"
        files = {
            "file": ("test_piece.txt", io.BytesIO(file_content), "text/plain")
        }
        data = {
            "nom": "TEST_Document de test",
            "description": "Description du document test"
        }
        
        # Remove Content-Type header for multipart
        headers = {"Authorization": f"Bearer {SESSION_TOKEN}"}
        
        response = requests.post(
            f"{BASE_URL}/api/conclusions/{conclusion_id}/pieces",
            files=files,
            data=data,
            headers=headers,
            cookies={"session_token": SESSION_TOKEN}
        )
        
        assert response.status_code == 201, f"Upload failed: {response.text}"
        piece = response.json()
        
        # Validate response structure
        assert "piece_id" in piece, "Missing piece_id"
        assert piece["conclusion_id"] == conclusion_id, "Wrong conclusion_id"
        assert piece["nom"] == "TEST_Document de test", "Wrong nom"
        assert piece["description"] == "Description du document test", "Wrong description"
        assert piece["numero"] == 1, "First piece should be numero 1"
        assert piece["file_size"] == len(file_content), "Wrong file size"
        assert piece["original_filename"] == "test_piece.txt", "Wrong original_filename"
        
        created_pieces.append(piece["piece_id"])
        print(f"✅ Piece uploaded successfully: {piece['piece_id']}")
        return piece
    
    def test_upload_piece_no_conclusion(self, api_client):
        """Test upload to non-existent conclusion"""
        file_content = b"Test content"
        files = {"file": ("test.txt", io.BytesIO(file_content), "text/plain")}
        data = {"nom": "Test", "description": ""}
        
        headers = {"Authorization": f"Bearer {SESSION_TOKEN}"}
        response = requests.post(
            f"{BASE_URL}/api/conclusions/fake_conclusion_id/pieces",
            files=files,
            data=data,
            headers=headers,
            cookies={"session_token": SESSION_TOKEN}
        )
        
        assert response.status_code == 404, "Should return 404 for non-existent conclusion"
        print("✅ Upload to non-existent conclusion returns 404")
    
    def test_upload_piece_exceeds_max_size(self, api_client, test_conclusion):
        """Test that files over 10MB are rejected"""
        conclusion_id = test_conclusion["conclusion_id"]
        
        # Create a file slightly over 10MB
        file_content = b"x" * (10 * 1024 * 1024 + 1000)
        files = {"file": ("large_file.txt", io.BytesIO(file_content), "text/plain")}
        data = {"nom": "Large File", "description": ""}
        
        headers = {"Authorization": f"Bearer {SESSION_TOKEN}"}
        response = requests.post(
            f"{BASE_URL}/api/conclusions/{conclusion_id}/pieces",
            files=files,
            data=data,
            headers=headers,
            cookies={"session_token": SESSION_TOKEN}
        )
        
        assert response.status_code == 400, f"Should reject large files: {response.text}"
        assert "10 Mo" in response.text or "10 MB" in response.text.lower() or "taille" in response.text.lower(), "Error message should mention size limit"
        print("✅ Large files (>10MB) are rejected")


class TestPiecesList:
    """Test GET pieces list endpoint"""
    
    def test_get_pieces_list(self, api_client, test_conclusion):
        """Test getting list of pieces for a conclusion"""
        conclusion_id = test_conclusion["conclusion_id"]
        
        response = api_client.get(f"{BASE_URL}/api/conclusions/{conclusion_id}/pieces")
        
        assert response.status_code == 200, f"Failed to get pieces: {response.text}"
        pieces = response.json()
        
        assert isinstance(pieces, list), "Response should be a list"
        print(f"✅ Get pieces list returned {len(pieces)} pieces")
        return pieces
    
    def test_get_pieces_nonexistent_conclusion(self, api_client):
        """Test getting pieces for non-existent conclusion"""
        response = api_client.get(f"{BASE_URL}/api/conclusions/nonexistent_id/pieces")
        
        assert response.status_code == 404, "Should return 404 for non-existent conclusion"
        print("✅ Get pieces for non-existent conclusion returns 404")


class TestPiecesUpdate:
    """Test PUT piece update endpoint"""
    
    def test_update_piece_name(self, api_client, test_conclusion):
        """Test updating piece name"""
        conclusion_id = test_conclusion["conclusion_id"]
        
        # First upload a piece
        file_content = b"Test content for update"
        files = {"file": ("update_test.txt", io.BytesIO(file_content), "text/plain")}
        data = {"nom": "TEST_Original Name", "description": "Original description"}
        
        headers = {"Authorization": f"Bearer {SESSION_TOKEN}"}
        upload_response = requests.post(
            f"{BASE_URL}/api/conclusions/{conclusion_id}/pieces",
            files=files,
            data=data,
            headers=headers,
            cookies={"session_token": SESSION_TOKEN}
        )
        
        assert upload_response.status_code == 201
        piece = upload_response.json()
        piece_id = piece["piece_id"]
        created_pieces.append(piece_id)
        
        # Update the piece
        update_response = api_client.put(
            f"{BASE_URL}/api/conclusions/{conclusion_id}/pieces/{piece_id}",
            json={"nom": "TEST_Updated Name", "description": "Updated description"}
        )
        
        assert update_response.status_code == 200, f"Update failed: {update_response.text}"
        updated_piece = update_response.json()
        
        assert updated_piece["nom"] == "TEST_Updated Name", "Name not updated"
        assert updated_piece["description"] == "Updated description", "Description not updated"
        
        # Verify persistence with GET
        get_response = api_client.get(f"{BASE_URL}/api/conclusions/{conclusion_id}/pieces")
        pieces = get_response.json()
        found_piece = next((p for p in pieces if p["piece_id"] == piece_id), None)
        
        assert found_piece is not None, "Piece not found after update"
        assert found_piece["nom"] == "TEST_Updated Name", "Update not persisted"
        print("✅ Piece update and persistence verified")
    
    def test_update_nonexistent_piece(self, api_client, test_conclusion):
        """Test updating non-existent piece"""
        conclusion_id = test_conclusion["conclusion_id"]
        
        response = api_client.put(
            f"{BASE_URL}/api/conclusions/{conclusion_id}/pieces/nonexistent_piece",
            json={"nom": "New Name"}
        )
        
        assert response.status_code == 404, "Should return 404 for non-existent piece"
        print("✅ Update non-existent piece returns 404")


class TestPiecesDelete:
    """Test DELETE piece endpoint and auto-renumbering"""
    
    def test_delete_piece_and_renumber(self, api_client, test_conclusion):
        """Test deleting piece and verifying automatic renumbering"""
        conclusion_id = test_conclusion["conclusion_id"]
        
        # Upload 3 pieces
        piece_ids = []
        for i in range(1, 4):
            file_content = f"Content for piece {i}".encode()
            files = {"file": (f"piece_{i}.txt", io.BytesIO(file_content), "text/plain")}
            data = {"nom": f"TEST_Piece {i}", "description": f"Description {i}"}
            
            headers = {"Authorization": f"Bearer {SESSION_TOKEN}"}
            response = requests.post(
                f"{BASE_URL}/api/conclusions/{conclusion_id}/pieces",
                files=files,
                data=data,
                headers=headers,
                cookies={"session_token": SESSION_TOKEN}
            )
            
            assert response.status_code == 201, f"Upload {i} failed: {response.text}"
            piece_ids.append(response.json()["piece_id"])
            created_pieces.append(piece_ids[-1])
        
        # Verify initial numbering
        pieces_before = api_client.get(f"{BASE_URL}/api/conclusions/{conclusion_id}/pieces").json()
        initial_numbers = {p["piece_id"]: p["numero"] for p in pieces_before}
        print(f"Initial numbering: {initial_numbers}")
        
        # Delete the second piece (middle one)
        delete_response = api_client.delete(
            f"{BASE_URL}/api/conclusions/{conclusion_id}/pieces/{piece_ids[1]}"
        )
        
        assert delete_response.status_code == 200, f"Delete failed: {delete_response.text}"
        
        # Verify renumbering
        pieces_after = api_client.get(f"{BASE_URL}/api/conclusions/{conclusion_id}/pieces").json()
        
        # Should have 2 pieces now, numbered 1 and 2
        assert len(pieces_after) == len(pieces_before) - 1, "Piece count should decrease by 1"
        
        # Check renumbering
        numeros = sorted([p["numero"] for p in pieces_after])
        expected = list(range(1, len(pieces_after) + 1))
        
        assert numeros == expected, f"Renumbering incorrect: got {numeros}, expected {expected}"
        print("✅ Delete piece and automatic renumbering verified")
    
    def test_delete_nonexistent_piece(self, api_client, test_conclusion):
        """Test deleting non-existent piece"""
        conclusion_id = test_conclusion["conclusion_id"]
        
        response = api_client.delete(
            f"{BASE_URL}/api/conclusions/{conclusion_id}/pieces/nonexistent_piece"
        )
        
        assert response.status_code == 404, "Should return 404 for non-existent piece"
        print("✅ Delete non-existent piece returns 404")


class TestPiecesReorder:
    """Test pieces reorder endpoint"""
    
    def test_reorder_pieces(self, api_client):
        """Test reordering pieces - creates its own isolated conclusion"""
        # Create a dedicated conclusion for reorder test
        conclusion_response = api_client.post(f"{BASE_URL}/api/conclusions", json={
            "type": "jaf",
            "parties": {"tribunal": "Reorder Test"},
            "faits": "Reorder test faits",
            "demandes": "Reorder test demandes"
        })
        assert conclusion_response.status_code in [200, 201]
        conclusion_id = conclusion_response.json()["conclusion_id"]
        created_conclusions.append(conclusion_id)
        
        # Upload 3 pieces for this test
        piece_ids = []
        for i in range(3):
            file_content = f"Reorder test content {i}".encode()
            files = {"file": (f"reorder_{i}.txt", io.BytesIO(file_content), "text/plain")}
            data = {"nom": f"TEST_Reorder Piece {i}", "description": ""}
            
            headers = {"Authorization": f"Bearer {SESSION_TOKEN}"}
            response = requests.post(
                f"{BASE_URL}/api/conclusions/{conclusion_id}/pieces",
                files=files,
                data=data,
                headers=headers,
                cookies={"session_token": SESSION_TOKEN}
            )
            assert response.status_code == 201, f"Upload {i} failed: {response.text}"
            piece_ids.append(response.json()["piece_id"])
        
        # Get initial pieces and their order
        pieces = api_client.get(f"{BASE_URL}/api/conclusions/{conclusion_id}/pieces").json()
        original_order = [p["piece_id"] for p in sorted(pieces, key=lambda x: x["numero"])]
        
        # Reverse the order
        new_order = list(reversed(original_order))
        
        # Reorder
        response = api_client.put(
            f"{BASE_URL}/api/conclusions/{conclusion_id}/pieces/reorder",
            json={"piece_ids": new_order}
        )
        
        assert response.status_code == 200, f"Reorder failed: {response.text}"
        
        # Verify new order
        updated_pieces = api_client.get(f"{BASE_URL}/api/conclusions/{conclusion_id}/pieces").json()
        
        for idx, piece in enumerate(sorted(updated_pieces, key=lambda x: x["numero"])):
            expected_id = new_order[idx]
            assert piece["piece_id"] == expected_id, f"Order mismatch at index {idx}"
            assert piece["numero"] == idx + 1, f"Numero should be {idx + 1}"
        
        print("✅ Pieces reorder verified")


class TestPiecesDownload:
    """Test piece download endpoint"""
    
    def test_download_piece(self, api_client, test_conclusion):
        """Test downloading a piece"""
        conclusion_id = test_conclusion["conclusion_id"]
        
        # Upload a piece first
        file_content = b"Download test content - unique identifier 12345"
        files = {"file": ("download_test.txt", io.BytesIO(file_content), "text/plain")}
        data = {"nom": "TEST_Download Test", "description": ""}
        
        headers = {"Authorization": f"Bearer {SESSION_TOKEN}"}
        upload_response = requests.post(
            f"{BASE_URL}/api/conclusions/{conclusion_id}/pieces",
            files=files,
            data=data,
            headers=headers,
            cookies={"session_token": SESSION_TOKEN}
        )
        
        assert upload_response.status_code == 201
        piece = upload_response.json()
        piece_id = piece["piece_id"]
        created_pieces.append(piece_id)
        
        # Download the piece
        download_response = requests.get(
            f"{BASE_URL}/api/pieces/{piece_id}/download",
            headers={"Authorization": f"Bearer {SESSION_TOKEN}"},
            cookies={"session_token": SESSION_TOKEN}
        )
        
        assert download_response.status_code == 200, f"Download failed: {download_response.status_code}"
        assert download_response.content == file_content, "Downloaded content doesn't match"
        
        # Check headers
        content_disp = download_response.headers.get("content-disposition", "")
        assert "download_test.txt" in content_disp, "Filename not in Content-Disposition"
        
        print("✅ Piece download verified")
    
    def test_download_nonexistent_piece(self):
        """Test downloading non-existent piece"""
        response = requests.get(
            f"{BASE_URL}/api/pieces/nonexistent_piece/download",
            headers={"Authorization": f"Bearer {SESSION_TOKEN}"},
            cookies={"session_token": SESSION_TOKEN}
        )
        
        assert response.status_code == 404, "Should return 404 for non-existent piece"
        print("✅ Download non-existent piece returns 404")


class TestPiecesAutoNumbering:
    """Test automatic piece numbering"""
    
    def test_auto_numbering_sequential(self, api_client, test_conclusion):
        """Test that pieces are numbered sequentially starting from 1"""
        conclusion_id = test_conclusion["conclusion_id"]
        
        # Get current pieces count
        existing = api_client.get(f"{BASE_URL}/api/conclusions/{conclusion_id}/pieces").json()
        current_count = len(existing)
        
        # Upload a new piece
        file_content = b"Auto number test"
        files = {"file": ("auto_num.txt", io.BytesIO(file_content), "text/plain")}
        data = {"nom": "TEST_Auto Number", "description": ""}
        
        headers = {"Authorization": f"Bearer {SESSION_TOKEN}"}
        response = requests.post(
            f"{BASE_URL}/api/conclusions/{conclusion_id}/pieces",
            files=files,
            data=data,
            headers=headers,
            cookies={"session_token": SESSION_TOKEN}
        )
        
        assert response.status_code == 201
        piece = response.json()
        created_pieces.append(piece["piece_id"])
        
        # Verify numero
        expected_numero = current_count + 1
        assert piece["numero"] == expected_numero, f"Expected numero {expected_numero}, got {piece['numero']}"
        print(f"✅ Auto numbering verified: piece got numero {piece['numero']}")


# Cleanup fixture
@pytest.fixture(scope="module", autouse=True)
def cleanup(api_client):
    """Cleanup test data after all tests"""
    yield
    
    # Cleanup conclusions (which will also delete associated pieces)
    for conclusion_id in created_conclusions:
        try:
            api_client.delete(f"{BASE_URL}/api/conclusions/{conclusion_id}")
        except:
            pass
    
    print("✅ Test cleanup completed")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
