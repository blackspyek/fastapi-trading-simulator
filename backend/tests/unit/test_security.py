from datetime import timedelta
from app.api.core.security import verify_password, hash_password, create_access_token, decode_token


class TestPasswordHashing:
    """Password hashing tests."""

    def test_given_plain_password_when_hash_then_different_string(self) -> None:
        """Password -> hash -> different value."""
        password = "testpassword123"
        hashed = hash_password(password)
        
        assert hashed != password
        assert len(hashed) > 20

    def test_given_correct_password_when_verify_then_true(self) -> None:
        """Correct password -> verify -> True."""
        password = "testpassword123"
        hashed = hash_password(password)
        
        assert verify_password(password, hashed) is True

    def test_given_wrong_password_when_verify_then_false(self) -> None:
        """Wrong password -> verify -> False."""
        password = "testpassword123"
        hashed = hash_password(password)
        
        assert verify_password("wrongpassword", hashed) is False

    def test_given_same_password_when_hash_twice_then_different_hashes(self) -> None:
        """Same password -> two hashes -> different (bcrypt salt)."""
        password = "testpassword123"
        hash1 = hash_password(password)
        hash2 = hash_password(password)
        
        assert hash1 != hash2

    def test_given_empty_password_when_hash_then_valid_hash(self) -> None:
        """Empty password -> hash -> valid hash."""
        password = ""
        hashed = hash_password(password)
        
        assert verify_password(password, hashed) is True


class TestJWT:
    """JWT token tests."""

    def test_given_data_when_create_token_then_token_returned(self) -> None:
        """Data -> create_access_token -> token string."""
        data = {"sub": "123"}
        token = create_access_token(data)
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    def test_given_valid_token_when_decode_then_payload_returned(self) -> None:
        """Valid token -> decode -> payload with data."""
        data = {"sub": "123", "extra": "data"}
        token = create_access_token(data)
        
        decoded = decode_token(token)
        
        assert decoded is not None
        assert decoded["sub"] == "123"
        assert decoded["extra"] == "data"
        assert "exp" in decoded

    def test_given_invalid_token_when_decode_then_none_returned(self) -> None:
        """Invalid token -> decode -> None."""
        decoded = decode_token("invalid_token")
        assert decoded is None

    def test_given_malformed_token_when_decode_then_none_returned(self) -> None:
        """Malformed token -> decode -> None."""
        decoded = decode_token("not.a.valid.jwt.token")
        assert decoded is None

    def test_given_custom_expiry_when_create_token_then_valid_token(self) -> None:
        """Custom expiry time -> valid token."""
        data = {"sub": "123"}
        token = create_access_token(data, expires_after=timedelta(minutes=5))
        
        decoded = decode_token(token)
        
        assert decoded is not None
        assert decoded["sub"] == "123"

    def test_given_complex_data_when_create_token_then_data_preserved(self) -> None:
        """Complex data -> create_access_token -> data preserved."""
        data = {"sub": "user_123", "role": "admin", "permissions": ["read", "write"]}
        token = create_access_token(data)
        
        decoded = decode_token(token)
        
        assert decoded["sub"] == "user_123"
        assert decoded["role"] == "admin"
        assert decoded["permissions"] == ["read", "write"]
