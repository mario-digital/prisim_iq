"""Integration tests for evidence endpoints."""

from fastapi.testclient import TestClient


class TestEvidenceEndpoint:
    """Tests for GET /api/v1/evidence endpoint."""

    def test_evidence_returns_200(self, client: TestClient) -> None:
        """Test evidence endpoint returns 200 OK."""
        response = client.get("/api/v1/evidence")
        assert response.status_code == 200

    def test_evidence_returns_model_cards(self, client: TestClient) -> None:
        """Test evidence endpoint returns model cards array."""
        response = client.get("/api/v1/evidence")
        data = response.json()

        assert "model_cards" in data
        assert isinstance(data["model_cards"], list)
        assert len(data["model_cards"]) >= 1  # At least one model card

    def test_evidence_model_card_has_required_fields(self, client: TestClient) -> None:
        """Test model cards have required fields."""
        response = client.get("/api/v1/evidence")
        data = response.json()

        if data["model_cards"]:
            card = data["model_cards"][0]
            assert "model_name" in card
            assert "model_version" in card
            assert "model_details" in card
            assert "metrics" in card
            assert "feature_importance" in card
            assert "limitations" in card

    def test_evidence_returns_data_card(self, client: TestClient) -> None:
        """Test evidence endpoint returns data card."""
        response = client.get("/api/v1/evidence")
        data = response.json()

        assert "data_card" in data
        data_card = data["data_card"]
        assert "dataset_name" in data_card
        assert "version" in data_card
        assert "features" in data_card
        assert "statistics" in data_card

    def test_evidence_returns_methodology(self, client: TestClient) -> None:
        """Test evidence endpoint returns methodology documentation."""
        response = client.get("/api/v1/evidence")
        data = response.json()

        assert "methodology" in data
        methodology = data["methodology"]
        assert "title" in methodology
        assert "sections" in methodology
        assert len(methodology["sections"]) >= 1

    def test_evidence_returns_cache_ttl(self, client: TestClient) -> None:
        """Test evidence endpoint returns cache TTL."""
        response = client.get("/api/v1/evidence")
        data = response.json()

        assert "cache_ttl_seconds" in data
        assert data["cache_ttl_seconds"] == 86400  # 24 hours

    def test_evidence_returns_generated_at(self, client: TestClient) -> None:
        """Test evidence endpoint returns generated_at timestamp."""
        response = client.get("/api/v1/evidence")
        data = response.json()

        assert "generated_at" in data
        assert data["generated_at"] is not None

    def test_evidence_format_markdown_via_query(self, client: TestClient) -> None:
        """Test evidence endpoint returns markdown via query param."""
        response = client.get("/api/v1/evidence?format=markdown")
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/markdown; charset=utf-8"

        content = response.text
        assert "# PrismIQ Evidence Documentation" in content
        assert "## Model Cards" in content

    def test_evidence_format_markdown_via_accept_header(self, client: TestClient) -> None:
        """Test evidence endpoint returns markdown via Accept header."""
        response = client.get(
            "/api/v1/evidence",
            headers={"Accept": "text/markdown"},
        )
        assert response.status_code == 200
        assert "text/markdown" in response.headers["content-type"]

    def test_evidence_default_format_is_json(self, client: TestClient) -> None:
        """Test evidence endpoint defaults to JSON format."""
        response = client.get("/api/v1/evidence")
        assert response.status_code == 200
        # Should be valid JSON
        data = response.json()
        assert isinstance(data, dict)


class TestHoneywellMappingEndpoint:
    """Tests for GET /api/v1/honeywell_mapping endpoint."""

    def test_honeywell_mapping_returns_200(self, client: TestClient) -> None:
        """Test Honeywell mapping endpoint returns 200 OK."""
        response = client.get("/api/v1/honeywell_mapping")
        assert response.status_code == 200

    def test_honeywell_mapping_has_title(self, client: TestClient) -> None:
        """Test Honeywell mapping has title."""
        response = client.get("/api/v1/honeywell_mapping")
        data = response.json()

        assert "title" in data
        assert "Honeywell" in data["title"]

    def test_honeywell_mapping_has_description(self, client: TestClient) -> None:
        """Test Honeywell mapping has description."""
        response = client.get("/api/v1/honeywell_mapping")
        data = response.json()

        assert "description" in data
        assert len(data["description"]) > 0

    def test_honeywell_mapping_has_mappings(self, client: TestClient) -> None:
        """Test Honeywell mapping returns mappings array."""
        response = client.get("/api/v1/honeywell_mapping")
        data = response.json()

        assert "mappings" in data
        assert isinstance(data["mappings"], list)
        assert len(data["mappings"]) >= 1

    def test_honeywell_mapping_entry_has_required_fields(
        self, client: TestClient
    ) -> None:
        """Test each mapping entry has required fields."""
        response = client.get("/api/v1/honeywell_mapping")
        data = response.json()

        for mapping in data["mappings"]:
            assert "ride_sharing_concept" in mapping
            assert "honeywell_equivalent" in mapping
            assert "category" in mapping
            assert "rationale" in mapping
            assert "applicability" in mapping

    def test_honeywell_mapping_categories_are_valid(self, client: TestClient) -> None:
        """Test mapping categories are from allowed set."""
        response = client.get("/api/v1/honeywell_mapping")
        data = response.json()

        valid_categories = {"pricing", "demand", "supply", "customer"}
        for mapping in data["mappings"]:
            assert mapping["category"] in valid_categories

    def test_honeywell_mapping_has_business_context(self, client: TestClient) -> None:
        """Test Honeywell mapping includes business context."""
        response = client.get("/api/v1/honeywell_mapping")
        data = response.json()

        assert "business_context" in data
        assert len(data["business_context"]) > 50  # Meaningful content

    def test_honeywell_mapping_format_markdown_via_query(
        self, client: TestClient
    ) -> None:
        """Test Honeywell mapping returns markdown via query param."""
        response = client.get("/api/v1/honeywell_mapping?format=markdown")
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/markdown; charset=utf-8"

        content = response.text
        assert "# Ride-Sharing to Honeywell" in content
        assert "| Ride-Sharing Concept |" in content  # Table header

    def test_honeywell_mapping_format_markdown_via_accept_header(
        self, client: TestClient
    ) -> None:
        """Test Honeywell mapping returns markdown via Accept header."""
        response = client.get(
            "/api/v1/honeywell_mapping",
            headers={"Accept": "text/markdown"},
        )
        assert response.status_code == 200
        assert "text/markdown" in response.headers["content-type"]

    def test_honeywell_mapping_default_format_is_json(self, client: TestClient) -> None:
        """Test Honeywell mapping defaults to JSON format."""
        response = client.get("/api/v1/honeywell_mapping")
        assert response.status_code == 200
        # Should be valid JSON
        data = response.json()
        assert isinstance(data, dict)


class TestEvidenceFormatSwitching:
    """Tests for format switching behavior."""

    def test_query_param_takes_precedence_over_header(
        self, client: TestClient
    ) -> None:
        """Test query parameter takes precedence over Accept header."""
        # Request markdown via header but JSON via query param
        response = client.get(
            "/api/v1/evidence?format=json",
            headers={"Accept": "text/markdown"},
        )
        assert response.status_code == 200
        # Should be JSON because query param takes precedence
        data = response.json()
        assert "model_cards" in data

    def test_text_plain_header_returns_markdown(self, client: TestClient) -> None:
        """Test text/plain Accept header returns markdown."""
        response = client.get(
            "/api/v1/evidence",
            headers={"Accept": "text/plain"},
        )
        assert response.status_code == 200
        assert "text/markdown" in response.headers["content-type"]

