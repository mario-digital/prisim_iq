# 16. Testing Strategy

## 16.1 Testing Pyramid

```
                    ┌─────────────┐
                    │   E2E Tests │  ← 5-10 tests
                    │  Playwright │
                    └──────┬──────┘
              ┌────────────┴────────────┐
              │   Integration Tests     │  ← 20-30 tests
              │   pytest + Bun Test     │
              └────────────┬────────────┘
    ┌──────────────────────┴──────────────────────┐
    │              Unit Tests                      │  ← 50-100 tests
    │      pytest (backend) + Bun Test (frontend) │
    └─────────────────────────────────────────────┘
```

## 16.2 Test Categories

**Backend Unit Tests:**
```python
# tests/unit/test_ml/test_model_manager.py
def test_price_prediction_returns_valid_range():
    manager = ModelManager()
    context = create_test_context()
    result = manager.predict(context)
    assert 5.0 <= result.price <= 200.0
    assert 0.0 <= result.confidence <= 1.0
```

**Frontend Unit Tests:**
```typescript
// tests/unit/stores/chatStore.test.ts
import { useChatStore } from '@/stores/chatStore';

test('addMessage appends to messages', () => {
  const { addMessage, messages } = useChatStore.getState();
  addMessage({ id: '1', role: 'user', content: 'test' });
  expect(messages).toHaveLength(1);
});
```

**Integration Tests:**
```python
# tests/integration/test_api/test_pricing.py
async def test_optimize_price_endpoint():
    async with AsyncClient(app=app) as client:
        response = await client.post(
            "/api/v1/optimize_price",
            json={"context": valid_context}
        )
        assert response.status_code == 200
        assert "recommendedPrice" in response.json()
```

**E2E Tests:**
```typescript
// tests/e2e/pricing-flow.spec.ts
test('user can get price recommendation', async ({ page }) => {
  await page.goto('/workspace');
  await page.fill('[data-testid="chat-input"]', 'What is the optimal price?');
  await page.click('[data-testid="send-button"]');
  await expect(page.locator('[data-testid="price-gauge"]')).toBeVisible();
});
```

## 16.3 Test Commands

```bash
# Backend
cd backend
pytest                           # All tests
pytest tests/unit               # Unit only
pytest -m "not slow"            # Skip slow tests
pytest --cov=src --cov-report=html  # Coverage

# Frontend
cd frontend
bun test                        # All tests
bun test --watch               # Watch mode
bun run test:e2e               # Playwright E2E
```

---
