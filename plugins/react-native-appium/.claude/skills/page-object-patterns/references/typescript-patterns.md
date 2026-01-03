# TypeScript Patterns for Appium Page Objects

## Type Definitions

### WebDriverIO Types

```typescript
// Import types from webdriverio
import type { Browser } from 'webdriverio';

// Element type for selectors
type AppiumElement = ReturnType<Browser['$']>;

// Or use the chainable promise type
import type { ChainablePromiseElement } from 'webdriverio';
```

### Custom Types

```typescript
// Capability types
interface AndroidCapabilities {
  platformName: 'Android';
  'appium:automationName': 'UiAutomator2';
  'appium:deviceName': string;
  'appium:app': string;
  'appium:appPackage'?: string;
  'appium:appActivity'?: string;
  'appium:autoGrantPermissions'?: boolean;
  'appium:newCommandTimeout'?: number;
}

interface IOSCapabilities {
  platformName: 'iOS';
  'appium:automationName': 'XCUITest';
  'appium:deviceName': string;
  'appium:platformVersion': string;
  'appium:app': string;
  'appium:bundleId'?: string;
  'appium:autoAcceptAlerts'?: boolean;
}

type AppiumCapabilities = AndroidCapabilities | IOSCapabilities;
```

### Test Data Types

```typescript
// User data for tests
interface TestUser {
  email: string;
  password: string;
  name?: string;
}

// Product data
interface TestProduct {
  id: string;
  name: string;
  price: number;
}

// Test fixtures
interface TestFixtures {
  users: {
    valid: TestUser;
    invalid: TestUser;
    new: TestUser;
  };
  products: TestProduct[];
}
```

## Generic Page Object

```typescript
// Base screen with generics for type-safe navigation
abstract class Screen<TReturn = void> {
  protected driver: WebdriverIO.Browser;

  constructor(driver: WebdriverIO.Browser) {
    this.driver = driver;
  }

  abstract get screenIdentifier(): ChainablePromiseElement;

  async waitForDisplayed(timeout = 10000): Promise<this> {
    await this.screenIdentifier.waitForDisplayed({ timeout });
    return this;
  }
}

// Screen that returns another screen on action
class LoginScreen extends Screen {
  // ... selectors

  async login(email: string, password: string): Promise<HomeScreen> {
    await this.enterEmail(email);
    await this.enterPassword(password);
    await this.tapLoginButton();

    const home = new HomeScreen(this.driver);
    await home.waitForDisplayed();
    return home;
  }
}
```

## Builder Pattern for Screens

```typescript
class CartScreenBuilder {
  private driver: WebdriverIO.Browser;
  private items: Array<{ name: string; quantity: number }> = [];

  constructor(driver: WebdriverIO.Browser) {
    this.driver = driver;
  }

  withItem(name: string, quantity = 1): this {
    this.items.push({ name, quantity });
    return this;
  }

  async build(): Promise<CartScreen> {
    const homeScreen = new HomeScreen(this.driver);
    await homeScreen.waitForDisplayed();

    for (const item of this.items) {
      await homeScreen.addProductToCart(item.name, item.quantity);
    }

    await homeScreen.openCart();
    const cartScreen = new CartScreen(this.driver);
    await cartScreen.waitForDisplayed();
    return cartScreen;
  }
}

// Usage
const cart = await new CartScreenBuilder(driver)
  .withItem('iPhone', 1)
  .withItem('Case', 2)
  .build();
```

## Factory Pattern

```typescript
// Screen factory for dynamic screen creation
class ScreenFactory {
  private driver: WebdriverIO.Browser;

  constructor(driver: WebdriverIO.Browser) {
    this.driver = driver;
  }

  create<T extends Screen>(ScreenClass: new (driver: WebdriverIO.Browser) => T): T {
    return new ScreenClass(this.driver);
  }

  async createAndWait<T extends Screen>(
    ScreenClass: new (driver: WebdriverIO.Browser) => T,
    timeout = 10000
  ): Promise<T> {
    const screen = this.create(ScreenClass);
    await screen.waitForDisplayed(timeout);
    return screen;
  }
}

// Usage
const factory = new ScreenFactory(driver);
const login = await factory.createAndWait(LoginScreen);
```

## Decorator Pattern for Logging

```typescript
// Method decorator for logging actions
function logAction(target: any, propertyKey: string, descriptor: PropertyDescriptor) {
  const originalMethod = descriptor.value;

  descriptor.value = async function (...args: any[]) {
    console.log(`[Action] ${propertyKey} started`);
    const start = Date.now();
    try {
      const result = await originalMethod.apply(this, args);
      console.log(`[Action] ${propertyKey} completed in ${Date.now() - start}ms`);
      return result;
    } catch (error) {
      console.error(`[Action] ${propertyKey} failed:`, error);
      throw error;
    }
  };

  return descriptor;
}

// Usage
class LoginScreen extends Screen {
  @logAction
  async login(email: string, password: string): Promise<void> {
    // ... implementation
  }
}
```

## Conditional Types for Platform-Specific Code

```typescript
type Platform = 'ios' | 'android';

interface PlatformSelectors<P extends Platform> {
  submit: P extends 'ios'
    ? `-ios predicate string:name == "Submit"`
    : `android=new UiSelector().text("Submit")`;
}

class PlatformAwareScreen<P extends Platform> extends Screen {
  readonly platform: P;

  constructor(driver: WebdriverIO.Browser, platform: P) {
    super(driver);
    this.platform = platform;
  }

  getSelector<K extends keyof PlatformSelectors<P>>(key: K): string {
    const selectors: PlatformSelectors<P> = {
      submit: this.platform === 'ios'
        ? `-ios predicate string:name == "Submit"`
        : `android=new UiSelector().text("Submit")`,
    } as PlatformSelectors<P>;

    return selectors[key];
  }
}
```

## Assertion Helpers

```typescript
// Type-safe assertion helper
class ScreenAssertions<T extends Screen> {
  private screen: T;

  constructor(screen: T) {
    this.screen = screen;
  }

  async toBeDisplayed(timeout = 10000): Promise<void> {
    await this.screen.waitForDisplayed(timeout);
  }

  async toHaveText(
    element: ChainablePromiseElement,
    expected: string
  ): Promise<void> {
    await element.waitForDisplayed();
    const actual = await element.getText();
    if (actual !== expected) {
      throw new Error(`Expected "${expected}" but got "${actual}"`);
    }
  }

  async toContainText(
    element: ChainablePromiseElement,
    expected: string
  ): Promise<void> {
    await element.waitForDisplayed();
    const actual = await element.getText();
    if (!actual.includes(expected)) {
      throw new Error(`Expected to contain "${expected}" but got "${actual}"`);
    }
  }
}

// Usage
const loginAssert = new ScreenAssertions(loginScreen);
await loginAssert.toBeDisplayed();
await loginAssert.toHaveText(loginScreen.errorMessage, 'Invalid credentials');
```

## State Machine Pattern

```typescript
// For complex flows with state management
type AuthState = 'logged_out' | 'logging_in' | 'logged_in' | 'error';

class AuthStateMachine {
  private driver: WebdriverIO.Browser;
  private state: AuthState = 'logged_out';

  constructor(driver: WebdriverIO.Browser) {
    this.driver = driver;
  }

  get currentState(): AuthState {
    return this.state;
  }

  async login(email: string, password: string): Promise<boolean> {
    if (this.state !== 'logged_out') {
      throw new Error(`Cannot login from state: ${this.state}`);
    }

    this.state = 'logging_in';

    try {
      const loginScreen = new LoginScreen(this.driver);
      await loginScreen.login(email, password);

      const homeScreen = new HomeScreen(this.driver);
      if (await homeScreen.isDisplayed()) {
        this.state = 'logged_in';
        return true;
      } else {
        this.state = 'error';
        return false;
      }
    } catch {
      this.state = 'error';
      return false;
    }
  }

  async logout(): Promise<void> {
    if (this.state !== 'logged_in') {
      throw new Error(`Cannot logout from state: ${this.state}`);
    }

    const homeScreen = new HomeScreen(this.driver);
    await homeScreen.logout();
    this.state = 'logged_out';
  }
}
```

## Utility Types

```typescript
// Make specific properties required
type WithRequired<T, K extends keyof T> = T & { [P in K]-?: T[P] };

// Make specific properties optional
type WithOptional<T, K extends keyof T> = Omit<T, K> & Partial<Pick<T, K>>;

// Extract screen method names
type ScreenMethods<T extends Screen> = {
  [K in keyof T]: T[K] extends (...args: any[]) => any ? K : never;
}[keyof T];

// Usage
type LoginMethods = ScreenMethods<LoginScreen>;
// Result: 'login' | 'enterEmail' | 'enterPassword' | 'tapLoginButton' | ...
```
