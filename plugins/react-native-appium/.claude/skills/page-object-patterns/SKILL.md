---
name: page-object-patterns
description: Page Object Model patterns for Appium testing with React Native. Provides reusable abstractions for screen interactions, element management, and cross-platform testing.
---

# Page Object Patterns for Appium

The Page Object Model (POM) is a design pattern that creates an abstraction layer between test scripts and the application UI. This skill covers best practices for implementing POM in React Native Appium tests.

## Quick Start

```typescript
// Instead of this (BAD):
await driver.$('~login-button').click();
await driver.$('~email-input').setValue('test@example.com');

// Do this (GOOD):
const loginScreen = new LoginScreen(driver);
await loginScreen.enterEmail('test@example.com');
await loginScreen.tapLoginButton();
```

## Triggers

Use this skill when:
- "page object pattern"
- "screen abstraction"
- "organize appium tests"
- "reusable test components"
- "POM for react native"

---

## Quick Reference

| Concept | Purpose |
|---------|---------|
| Screen Class | Represents a single app screen |
| Base Screen | Common functionality for all screens |
| Getters | Define element selectors |
| Actions | User interactions (tap, type, scroll) |
| Assertions | Verify screen state |
| Components | Reusable UI component abstractions |

---

## Base Screen Class

Every page object extends a base class with common functionality:

```typescript
// tests/e2e/screens/Screen.ts
export abstract class Screen {
  protected driver: WebdriverIO.Browser;

  constructor(driver: WebdriverIO.Browser) {
    this.driver = driver;
  }

  // Abstract method - each screen defines its own
  abstract get screenIdentifier(): ChainablePromiseElement;

  /**
   * Wait for screen to be displayed
   */
  async waitForDisplayed(timeout = 10000): Promise<void> {
    await this.screenIdentifier.waitForDisplayed({ timeout });
  }

  /**
   * Check if screen is currently displayed
   */
  async isDisplayed(): Promise<boolean> {
    try {
      return await this.screenIdentifier.isDisplayed();
    } catch {
      return false;
    }
  }

  /**
   * Take a screenshot
   */
  async takeScreenshot(name: string): Promise<void> {
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    await this.driver.saveScreenshot(`./screenshots/${name}-${timestamp}.png`);
  }

  /**
   * Dismiss keyboard if visible
   */
  async dismissKeyboard(): Promise<void> {
    try {
      if (this.driver.isIOS) {
        await this.driver.execute('mobile: hideKeyboard', {});
      } else {
        await this.driver.hideKeyboard();
      }
    } catch {
      // Keyboard might not be visible
    }
  }

  /**
   * Scroll down on the screen
   */
  async scrollDown(percentage = 0.6): Promise<void> {
    const { height, width } = await this.driver.getWindowSize();
    await this.driver.touchAction([
      { action: 'press', x: width / 2, y: height * 0.8 },
      { action: 'wait', ms: 100 },
      { action: 'moveTo', x: width / 2, y: height * (1 - percentage) },
      { action: 'release' }
    ]);
  }

  /**
   * Scroll up on the screen
   */
  async scrollUp(percentage = 0.6): Promise<void> {
    const { height, width } = await this.driver.getWindowSize();
    await this.driver.touchAction([
      { action: 'press', x: width / 2, y: height * 0.2 },
      { action: 'wait', ms: 100 },
      { action: 'moveTo', x: width / 2, y: height * percentage },
      { action: 'release' }
    ]);
  }

  /**
   * Scroll element into view
   */
  async scrollToElement(element: ChainablePromiseElement): Promise<void> {
    let attempts = 0;
    while (attempts < 5) {
      if (await element.isDisplayed()) {
        return;
      }
      await this.scrollDown(0.3);
      attempts++;
    }
  }

  /**
   * Wait for element and get its text
   */
  async getTextOf(element: ChainablePromiseElement, timeout = 5000): Promise<string> {
    await element.waitForDisplayed({ timeout });
    return element.getText();
  }

  /**
   * Safely tap element with wait
   */
  async tap(element: ChainablePromiseElement, timeout = 5000): Promise<void> {
    await element.waitForDisplayed({ timeout });
    await element.waitForEnabled({ timeout });
    await element.click();
  }

  /**
   * Type text into element
   */
  async typeInto(
    element: ChainablePromiseElement,
    text: string,
    clearFirst = true
  ): Promise<void> {
    await element.waitForDisplayed();
    if (clearFirst) {
      await element.clearValue();
    }
    await element.setValue(text);
  }
}
```

---

## Screen Class Template

Each screen in your app gets its own class:

```typescript
// tests/e2e/screens/LoginScreen.ts
import { Screen } from './Screen';

export class LoginScreen extends Screen {
  // ═══════════════════════════════════════════════════════════
  // SELECTORS - Define all elements using getters
  // ═══════════════════════════════════════════════════════════

  get screenIdentifier() {
    return this.driver.$('~login-screen');
  }

  get emailInput() {
    return this.driver.$('~login-email-input');
  }

  get passwordInput() {
    return this.driver.$('~login-password-input');
  }

  get loginButton() {
    return this.driver.$('~login-submit-button');
  }

  get forgotPasswordLink() {
    return this.driver.$('~login-forgot-password-link');
  }

  get errorMessage() {
    return this.driver.$('~login-error-message');
  }

  get loadingIndicator() {
    return this.driver.$('~login-loading');
  }

  // ═══════════════════════════════════════════════════════════
  // ACTIONS - User interactions
  // ═══════════════════════════════════════════════════════════

  /**
   * Enter email address
   */
  async enterEmail(email: string): Promise<void> {
    await this.typeInto(this.emailInput, email);
  }

  /**
   * Enter password
   */
  async enterPassword(password: string): Promise<void> {
    await this.typeInto(this.passwordInput, password);
  }

  /**
   * Tap the login button
   */
  async tapLoginButton(): Promise<void> {
    await this.dismissKeyboard();
    await this.tap(this.loginButton);
  }

  /**
   * Tap forgot password link
   */
  async tapForgotPassword(): Promise<void> {
    await this.tap(this.forgotPasswordLink);
  }

  /**
   * Perform complete login flow
   */
  async login(email: string, password: string): Promise<void> {
    await this.enterEmail(email);
    await this.enterPassword(password);
    await this.tapLoginButton();
  }

  /**
   * Wait for loading to complete
   */
  async waitForLoadingComplete(timeout = 10000): Promise<void> {
    await this.loadingIndicator.waitForDisplayed({ reverse: true, timeout });
  }

  // ═══════════════════════════════════════════════════════════
  // ASSERTIONS - State verification
  // ═══════════════════════════════════════════════════════════

  /**
   * Get error message text
   */
  async getErrorMessage(): Promise<string> {
    return this.getTextOf(this.errorMessage);
  }

  /**
   * Check if error is displayed
   */
  async isErrorDisplayed(): Promise<boolean> {
    try {
      return await this.errorMessage.isDisplayed();
    } catch {
      return false;
    }
  }

  /**
   * Check if login button is enabled
   */
  async isLoginButtonEnabled(): Promise<boolean> {
    await this.loginButton.waitForDisplayed();
    return this.loginButton.isEnabled();
  }
}
```

---

## Component Pattern

For reusable UI components that appear on multiple screens:

```typescript
// tests/e2e/components/Header.ts
export class Header {
  private driver: WebdriverIO.Browser;
  private prefix: string;

  constructor(driver: WebdriverIO.Browser, prefix = 'header') {
    this.driver = driver;
    this.prefix = prefix;
  }

  get backButton() {
    return this.driver.$(`~${this.prefix}-back-button`);
  }

  get title() {
    return this.driver.$(`~${this.prefix}-title`);
  }

  get menuButton() {
    return this.driver.$(`~${this.prefix}-menu-button`);
  }

  async tapBack(): Promise<void> {
    await this.backButton.click();
  }

  async getTitle(): Promise<string> {
    return this.title.getText();
  }

  async openMenu(): Promise<void> {
    await this.menuButton.click();
  }
}

// Usage in screen
export class ProfileScreen extends Screen {
  header = new Header(this.driver, 'profile-header');

  // ... rest of screen
}
```

---

## List Item Pattern

For handling lists with indexed testIDs:

```typescript
// tests/e2e/components/ListItem.ts
export class ListItem {
  private driver: WebdriverIO.Browser;
  private baseSelector: string;
  private index: number;

  constructor(driver: WebdriverIO.Browser, baseSelector: string, index: number) {
    this.driver = driver;
    this.baseSelector = baseSelector;
    this.index = index;
  }

  get container() {
    return this.driver.$(`~${this.baseSelector}-${this.index}`);
  }

  get title() {
    return this.driver.$(`~${this.baseSelector}-${this.index}-title`);
  }

  get deleteButton() {
    return this.driver.$(`~${this.baseSelector}-${this.index}-delete`);
  }

  async tap(): Promise<void> {
    await this.container.click();
  }

  async getTitle(): Promise<string> {
    return this.title.getText();
  }

  async delete(): Promise<void> {
    await this.deleteButton.click();
  }
}

// tests/e2e/screens/CartScreen.ts
export class CartScreen extends Screen {
  get screenIdentifier() {
    return this.driver.$('~cart-screen');
  }

  getCartItem(index: number): ListItem {
    return new ListItem(this.driver, 'cart-item', index);
  }

  async getCartItems(): Promise<ListItem[]> {
    const items: ListItem[] = [];
    let index = 0;

    while (true) {
      const item = this.getCartItem(index);
      try {
        if (await item.container.isExisting()) {
          items.push(item);
          index++;
        } else {
          break;
        }
      } catch {
        break;
      }
    }

    return items;
  }

  async getCartItemCount(): Promise<number> {
    const items = await this.getCartItems();
    return items.length;
  }

  async deleteItemAt(index: number): Promise<void> {
    const item = this.getCartItem(index);
    await item.delete();
  }
}
```

---

## Form Component Pattern

For complex forms:

```typescript
// tests/e2e/components/Form.ts
interface FormField {
  name: string;
  testId: string;
  type: 'text' | 'password' | 'email' | 'phone' | 'select' | 'checkbox';
}

export class Form {
  private driver: WebdriverIO.Browser;
  private prefix: string;
  private fields: FormField[];

  constructor(
    driver: WebdriverIO.Browser,
    prefix: string,
    fields: FormField[]
  ) {
    this.driver = driver;
    this.prefix = prefix;
    this.fields = fields;
  }

  getField(name: string) {
    const field = this.fields.find(f => f.name === name);
    if (!field) throw new Error(`Field ${name} not found`);
    return this.driver.$(`~${this.prefix}-${field.testId}`);
  }

  async fillField(name: string, value: string): Promise<void> {
    const element = this.getField(name);
    await element.waitForDisplayed();
    await element.clearValue();
    await element.setValue(value);
  }

  async fillAll(data: Record<string, string>): Promise<void> {
    for (const [name, value] of Object.entries(data)) {
      await this.fillField(name, value);
    }
  }

  async getFieldValue(name: string): Promise<string> {
    const element = this.getField(name);
    return element.getValue();
  }

  async isFieldDisplayed(name: string): Promise<boolean> {
    try {
      const element = this.getField(name);
      return await element.isDisplayed();
    } catch {
      return false;
    }
  }
}

// Usage
const checkoutForm = new Form(driver, 'checkout', [
  { name: 'cardNumber', testId: 'card-number-input', type: 'text' },
  { name: 'expiry', testId: 'expiry-input', type: 'text' },
  { name: 'cvv', testId: 'cvv-input', type: 'password' },
  { name: 'name', testId: 'name-input', type: 'text' },
]);

await checkoutForm.fillAll({
  cardNumber: '4242424242424242',
  expiry: '12/25',
  cvv: '123',
  name: 'John Doe',
});
```

---

## Navigation Helper

For common navigation patterns:

```typescript
// tests/e2e/utils/Navigator.ts
import { LoginScreen } from '../screens/LoginScreen';
import { HomeScreen } from '../screens/HomeScreen';
import { ProfileScreen } from '../screens/ProfileScreen';

export class Navigator {
  private driver: WebdriverIO.Browser;

  constructor(driver: WebdriverIO.Browser) {
    this.driver = driver;
  }

  async loginAs(email: string, password: string): Promise<HomeScreen> {
    const loginScreen = new LoginScreen(this.driver);
    await loginScreen.waitForDisplayed();
    await loginScreen.login(email, password);

    const homeScreen = new HomeScreen(this.driver);
    await homeScreen.waitForDisplayed();
    return homeScreen;
  }

  async goToProfile(): Promise<ProfileScreen> {
    const homeScreen = new HomeScreen(this.driver);
    await homeScreen.tapProfileTab();

    const profileScreen = new ProfileScreen(this.driver);
    await profileScreen.waitForDisplayed();
    return profileScreen;
  }

  async navigateTo<T extends Screen>(
    action: () => Promise<void>,
    ScreenClass: new (driver: WebdriverIO.Browser) => T
  ): Promise<T> {
    await action();
    const screen = new ScreenClass(this.driver);
    await screen.waitForDisplayed();
    return screen;
  }
}
```

---

## Best Practices

### 1. Single Responsibility

Each page object should represent ONE screen:

```typescript
// Good: One class per screen
class LoginScreen extends Screen { }
class RegistrationScreen extends Screen { }

// Bad: Multiple screens in one class
class AuthScreens extends Screen { } // Don't do this
```

### 2. Encapsulate Selectors

Never expose raw selectors outside the page object:

```typescript
// Good: Selectors are private, actions are public
async tapLoginButton(): Promise<void> {
  await this.tap(this.loginButton);
}

// Bad: Exposing selector in test
await driver.$('~login-button').click(); // Don't do this in tests
```

### 3. Meaningful Method Names

Name methods by what they do, not how:

```typescript
// Good: Describes user action
async submitOrder(): Promise<void>

// Bad: Technical implementation detail
async clickSubmitButtonAndWait(): Promise<void>
```

### 4. Return Types

Return the next screen when navigating:

```typescript
async tapCheckout(): Promise<CheckoutScreen> {
  await this.tap(this.checkoutButton);
  const checkout = new CheckoutScreen(this.driver);
  await checkout.waitForDisplayed();
  return checkout;
}
```

---

## Anti-Patterns

| Anti-Pattern | Problem | Solution |
|-------------|---------|----------|
| God Screen | One class for all screens | One class per screen |
| Hardcoded Waits | Slow, flaky | Use explicit waits |
| Public Selectors | Tests depend on implementation | Use action methods |
| No Base Class | Code duplication | Extend Screen base |
| Deep Inheritance | Complex hierarchy | Prefer composition |
| Static Methods | Hard to test in isolation | Use instance methods |

---

## File Organization

```
tests/e2e/
├── screens/
│   ├── Screen.ts          # Base class
│   ├── LoginScreen.ts
│   ├── HomeScreen.ts
│   └── ProfileScreen.ts
├── components/
│   ├── Header.ts
│   ├── Footer.ts
│   ├── ListItem.ts
│   └── Form.ts
├── utils/
│   ├── Navigator.ts
│   └── TestData.ts
└── specs/
    └── *.spec.ts
```
