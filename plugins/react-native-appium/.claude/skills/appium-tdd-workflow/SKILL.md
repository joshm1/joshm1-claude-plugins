---
name: appium-tdd-workflow
description: Complete TDD workflow for writing Appium E2E tests in React Native/Expo projects. Covers red-green-refactor cycle, test organization, and CI/CD integration.
---

# Appium TDD Workflow

A comprehensive guide to Test-Driven Development with Appium for React Native and Expo applications.

## Quick Start

```
1. Write failing test (RED)
2. Add minimum code to pass (GREEN)
3. Refactor for quality (REFACTOR)
4. Repeat
```

## Triggers

Use this skill when you hear:
- "TDD for appium"
- "test driven development react native"
- "red green refactor e2e"
- "appium testing workflow"
- "e2e test first approach"

---

## Quick Reference

| Phase | Action | Verification |
|-------|--------|--------------|
| RED | Write failing test | Test fails with expected error |
| GREEN | Implement minimum code | Test passes |
| REFACTOR | Clean up without changing behavior | Test still passes |

---

## The TDD Cycle

### Phase 1: RED - Write the Failing Test

Before writing any feature code, write a test that describes the expected behavior.

```typescript
// tests/e2e/specs/checkout.spec.ts
describe('Checkout Flow', () => {
  it('should complete purchase with valid card', async () => {
    // This test will FAIL because the feature doesn't exist yet
    const cartScreen = new CartScreen(driver);
    const checkoutScreen = new CheckoutScreen(driver);
    const confirmationScreen = new ConfirmationScreen(driver);

    await cartScreen.tapCheckoutButton();
    await checkoutScreen.enterCardDetails('4242424242424242', '12/25', '123');
    await checkoutScreen.tapPayButton();

    // Assert we reach confirmation
    await expect(confirmationScreen.successMessage).toBeDisplayed();
    await expect(confirmationScreen.orderNumber).toHaveTextContaining('ORD-');
  });
});
```

**Verification**: Run the test and confirm it fails with a meaningful error (element not found, screen doesn't exist, etc.)

```bash
npx wdio run wdio.conf.ts --spec tests/e2e/specs/checkout.spec.ts
# Expected: FAIL - element '~checkout-button' not found
```

### Phase 2: GREEN - Make It Pass

Implement the **minimum** code needed to make the test pass.

1. **Add testIDs to React Native components:**

```tsx
// src/screens/CartScreen.tsx
<TouchableOpacity
  testID="cart-checkout-button"
  onPress={handleCheckout}
>
  <Text>Checkout</Text>
</TouchableOpacity>
```

2. **Create Page Objects:**

```typescript
// tests/e2e/screens/CartScreen.ts
export class CartScreen extends Screen {
  get checkoutButton() { return this.driver.$('~cart-checkout-button'); }

  async tapCheckoutButton(): Promise<void> {
    await this.checkoutButton.waitForDisplayed();
    await this.checkoutButton.click();
  }
}
```

3. **Implement feature logic** (if needed)

**Verification**: Run the test and confirm it passes

```bash
npx wdio run wdio.conf.ts --spec tests/e2e/specs/checkout.spec.ts
# Expected: PASS
```

### Phase 3: REFACTOR - Clean Up

With a passing test as your safety net, improve the code:

- Extract reusable methods to page objects
- Improve selector reliability
- Add better error messages
- Remove duplication

**Verification**: Run the test and confirm it still passes

```bash
npx wdio run wdio.conf.ts --spec tests/e2e/specs/checkout.spec.ts
# Expected: PASS (behavior unchanged)
```

---

## Test Organization

### Directory Structure

```
tests/e2e/
├── specs/                    # Test specifications
│   ├── auth/
│   │   ├── login.spec.ts
│   │   └── logout.spec.ts
│   ├── checkout/
│   │   ├── cart.spec.ts
│   │   └── payment.spec.ts
│   └── profile/
│       └── settings.spec.ts
├── screens/                  # Page Objects
│   ├── Screen.ts             # Base class
│   ├── LoginScreen.ts
│   ├── CartScreen.ts
│   └── CheckoutScreen.ts
├── utils/                    # Test utilities
│   ├── testData.ts
│   └── helpers.ts
└── fixtures/                 # Test data files
    └── users.json
```

### Test File Structure

```typescript
import { LoginScreen } from '../screens/LoginScreen';
import { testUsers } from '../fixtures/users';

describe('Feature: User Login', () => {
  let loginScreen: LoginScreen;

  // Setup runs once before all tests in this file
  beforeAll(async () => {
    // Global setup (e.g., clear app state)
  });

  // Setup runs before each test
  beforeEach(async () => {
    loginScreen = new LoginScreen(driver);
    await loginScreen.waitForDisplayed();
  });

  // Cleanup runs after each test
  afterEach(async function() {
    if (this.currentTest?.state === 'failed') {
      await driver.saveScreenshot(`./screenshots/${this.currentTest.title}.png`);
    }
  });

  // Group related tests
  describe('Scenario: Valid credentials', () => {
    it('should login successfully', async () => {
      // Arrange
      const user = testUsers.valid;

      // Act
      await loginScreen.login(user.email, user.password);

      // Assert
      const homeScreen = new HomeScreen(driver);
      await expect(homeScreen.welcomeMessage).toBeDisplayed();
    });
  });

  describe('Scenario: Invalid credentials', () => {
    it('should show error message', async () => {
      // Test code
    });
  });
});
```

---

## TDD Best Practices

### 1. One Assertion Per Test (Ideally)

```typescript
// Good: Focused tests
it('should display welcome message after login', async () => {
  await loginScreen.login(validUser);
  await expect(homeScreen.welcomeMessage).toBeDisplayed();
});

it('should show user name after login', async () => {
  await loginScreen.login(validUser);
  await expect(homeScreen.userName).toHaveText(validUser.name);
});

// Acceptable: Related assertions in one test
it('should complete login successfully', async () => {
  await loginScreen.login(validUser);
  await expect(homeScreen.welcomeMessage).toBeDisplayed();
  await expect(homeScreen.userName).toHaveText(validUser.name);
});
```

### 2. Test Behavior, Not Implementation

```typescript
// Good: Tests user-visible behavior
it('should show cart total when items added', async () => {
  await productScreen.addToCart();
  await expect(cartScreen.total).toHaveTextContaining('$');
});

// Bad: Tests implementation details
it('should call addItemToCart function', async () => {
  // Don't test internal function calls
});
```

### 3. Use Descriptive Test Names

```typescript
// Good: Describes scenario and expectation
describe('when user enters invalid email', () => {
  it('should display email format error', async () => {});
  it('should disable submit button', async () => {});
});

// Bad: Vague names
describe('email', () => {
  it('works', async () => {});
});
```

### 4. Keep Tests Independent

```typescript
// Good: Each test sets up its own state
beforeEach(async () => {
  await driver.reloadSession(); // Fresh start
});

// Bad: Tests depend on previous test state
it('should add item to cart', async () => {});
it('should show item in cart', async () => {}); // Assumes previous test ran
```

---

## CI/CD Integration

### GitHub Actions Example

```yaml
# .github/workflows/e2e.yml
name: E2E Tests

on:
  pull_request:
    branches: [main]

jobs:
  e2e-android:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'

      - name: Setup Java
        uses: actions/setup-java@v4
        with:
          distribution: 'temurin'
          java-version: '17'

      - name: Install dependencies
        run: npm ci

      - name: Build Android app
        run: npm run build:android:test

      - name: Start Appium
        run: |
          npm install -g appium
          appium driver install uiautomator2
          appium &
          sleep 10

      - name: Start Android Emulator
        uses: reactivecircus/android-emulator-runner@v2
        with:
          api-level: 33
          script: npm run test:e2e:android

      - name: Upload screenshots
        if: failure()
        uses: actions/upload-artifact@v4
        with:
          name: screenshots
          path: screenshots/
```

### Running Tests Locally

```bash
# Start Appium server (Terminal 1)
appium

# Start emulator/simulator (Terminal 2)
# Android
emulator -avd Pixel_6_API_33

# iOS (macOS only)
open -a Simulator

# Run tests (Terminal 3)
npm run test:e2e:android
# or
npm run test:e2e:ios
```

---

## Common Patterns

### Waiting for Navigation

```typescript
async navigateAndWait(
  action: () => Promise<void>,
  nextScreen: Screen
): Promise<void> {
  await action();
  await nextScreen.waitForDisplayed();
}

// Usage
await this.navigateAndWait(
  () => loginScreen.tapLoginButton(),
  homeScreen
);
```

### Handling Alerts

```typescript
async acceptAlertIfPresent(): Promise<void> {
  try {
    await driver.acceptAlert();
  } catch {
    // No alert present, continue
  }
}
```

### Testing Lists

```typescript
async getCartItemCount(): Promise<number> {
  const items = await driver.$$('~cart-item');
  return items.length;
}

async tapCartItem(index: number): Promise<void> {
  const item = await driver.$(`~cart-item-${index}`);
  await item.click();
}
```

---

## Anti-Patterns to Avoid

| Anti-Pattern | Problem | Solution |
|-------------|---------|----------|
| Hardcoded waits | Slow, flaky | Use explicit waits |
| XPath selectors | Brittle, slow | Use accessibility ID |
| Testing too much | Slow, hard to maintain | Focus on critical paths |
| Shared state | Flaky tests | Independent tests |
| No screenshots | Hard to debug | Capture on failure |
| Magic strings | Hard to maintain | Use constants/enums |

---

## Verification Checklist

Before considering a TDD cycle complete:

- [ ] Test failed first (RED confirmed)
- [ ] Minimum code added to pass (no over-engineering)
- [ ] Test passes consistently (no flakiness)
- [ ] Code refactored for clarity
- [ ] Page objects updated if needed
- [ ] testIDs follow naming convention
- [ ] Screenshots captured on failure
- [ ] Test runs in CI pipeline

---

## Related Commands

- `/new-appium-test <screen>` - Create new test file
- `/setup-appium` - Initialize Appium environment
- `/find-testids` - Audit testID coverage
