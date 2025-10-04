# Tests

Comprehensive test suite for DOPPELGANGER STUDIO.

## Structure

- **`unit/`** - Unit tests for individual components
- **`integration/`** - Integration tests for component interactions
- **`e2e/`** - End-to-end tests for full workflows
- **`performance/`** - Performance and load tests
- **`fixtures/`** - Test fixtures and sample data

## Running Tests

```bash
# Run all tests
pytest

# Run specific test suite
pytest tests/unit/

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/unit/test_intelligent_scraper.py

# Run tests matching pattern
pytest -k "character_transformation"
```

## Test Standards

- All tests should be async-compatible
- Aim for 90%+ code coverage
- Use fixtures from `conftest.py`
- Mock external services
- Follow naming convention: `test_<functionality>`

## Markers

Use pytest markers to organize tests:

```python
@pytest.mark.unit
@pytest.mark.integration
@pytest.mark.e2e
@pytest.mark.slow
@pytest.mark.requires_db
```
