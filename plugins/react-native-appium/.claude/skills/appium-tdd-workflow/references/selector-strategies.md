# Appium Selector Strategies for React Native

## Overview

Choosing the right selector strategy is critical for reliable, maintainable E2E tests. This guide covers all available strategies with React Native/Expo specific recommendations.

## Selector Priority (Most to Least Preferred)

### 1. Accessibility ID (Recommended)

Maps directly to React Native's `testID` prop.

```typescript
// React Native
<Button testID="login-submit-button" title="Login" />

// Appium selector
const button = await driver.$('~login-submit-button');
```

**Pros:**
- Cross-platform (works on iOS and Android)
- Fast lookup
- Stable across UI changes
- Semantic meaning

**Cons:**
- Requires adding testID to components

### 2. iOS Predicate String (iOS Only)

Uses NSPredicate syntax for complex queries.

```typescript
// Find by name
const element = await driver.$('-ios predicate string:name == "Login"');

// Find by type and name
const button = await driver.$('-ios predicate string:type == "XCUIElementTypeButton" AND name == "Login"');

// Contains match
const text = await driver.$('-ios predicate string:label CONTAINS "Welcome"');
```

**Common Predicates:**
| Predicate | Example |
|-----------|---------|
| `name == "X"` | Exact name match |
| `label CONTAINS "X"` | Label contains text |
| `type == "XCUIElementTypeButton"` | Element type |
| `value == "X"` | Input value |
| `enabled == true` | Element state |

### 3. iOS Class Chain (iOS Only)

XPath-like syntax optimized for iOS.

```typescript
// Direct child
const button = await driver.$('-ios class chain:**/XCUIElementTypeButton[`name == "Login"`]');

// Descendant at any level
const text = await driver.$('-ios class chain:**/XCUIElementTypeStaticText[`label == "Welcome"`]');

// Index-based
const firstButton = await driver.$('-ios class chain:**/XCUIElementTypeButton[1]');
```

### 4. Android UiSelector (Android Only)

Uses Android's UiAutomator selector syntax.

```typescript
// By resource ID
const button = await driver.$('android=new UiSelector().resourceId("com.app:id/login_button")');

// By text
const element = await driver.$('android=new UiSelector().text("Login")');

// By description (accessibility)
const icon = await driver.$('android=new UiSelector().description("Menu icon")');

// Chained selectors
const child = await driver.$('android=new UiSelector().className("android.widget.LinearLayout").childSelector(new UiSelector().text("Submit"))');
```

**Common UiSelector Methods:**
| Method | Example |
|--------|---------|
| `.resourceId("id")` | Find by resource ID |
| `.text("text")` | Exact text match |
| `.textContains("text")` | Text contains |
| `.description("desc")` | Content description |
| `.className("class")` | By class name |
| `.index(0)` | By index |
| `.clickable(true)` | By clickability |

### 5. XPath (Last Resort)

Most flexible but slowest and most brittle.

```typescript
// By text
const element = await driver.$('//android.widget.TextView[@text="Login"]');

// By resource ID
const button = await driver.$('//android.widget.Button[@resource-id="login_button"]');

// By partial attribute
const text = await driver.$('//*[contains(@text, "Welcome")]');

// iOS XPath
const iosButton = await driver.$('//XCUIElementTypeButton[@name="Login"]');
```

**When to Use XPath:**
- No testID available and can't add one
- Complex element relationships
- Text-based finding as last resort

## Cross-Platform Selector Pattern

```typescript
export class LoginScreen extends Screen {
  // Platform-agnostic (preferred)
  get emailInput() {
    return this.driver.$('~login-email-input');
  }

  // Platform-specific when needed
  get submitButton() {
    if (this.driver.isIOS) {
      return this.driver.$('-ios predicate string:name == "Submit" AND type == "XCUIElementTypeButton"');
    }
    return this.driver.$('android=new UiSelector().text("Submit").className("android.widget.Button")');
  }

  // Fallback chain
  async findElement(testId: string, fallbackText: string) {
    try {
      const element = await this.driver.$(`~${testId}`);
      if (await element.isExisting()) return element;
    } catch {}

    // Fallback to text
    if (this.driver.isIOS) {
      return this.driver.$(`-ios predicate string:label == "${fallbackText}"`);
    }
    return this.driver.$(`android=new UiSelector().text("${fallbackText}")`);
  }
}
```

## React Native Specific Considerations

### FlatList/ScrollView Items

```tsx
// React Native - indexed testIDs for list items
<FlatList
  data={items}
  renderItem={({ item, index }) => (
    <ListItem
      testID={`list-item-${index}`}
      testID-title={`list-item-${index}-title`}
      testID-delete={`list-item-${index}-delete`}
    />
  )}
/>
```

```typescript
// Appium - find specific list item
async getListItem(index: number) {
  return this.driver.$(`~list-item-${index}`);
}

async tapDeleteOnItem(index: number) {
  const deleteBtn = await this.driver.$(`~list-item-${index}-delete`);
  await deleteBtn.click();
}
```

### Modal Components

```tsx
// React Native
<Modal
  testID="confirmation-modal"
  visible={showModal}
>
  <View testID="confirmation-modal-content">
    <Button testID="confirmation-modal-confirm" title="Yes" />
    <Button testID="confirmation-modal-cancel" title="No" />
  </View>
</Modal>
```

### Text Input Fields

```tsx
// React Native - both testID and accessibility props
<TextInput
  testID="login-email-input"
  accessibilityLabel="Email address"
  accessibilityHint="Enter your email to sign in"
  placeholder="email@example.com"
/>
```

## Performance Comparison

| Strategy | iOS Speed | Android Speed | Reliability |
|----------|-----------|---------------|-------------|
| Accessibility ID | Fast | Fast | High |
| iOS Predicate | Fast | N/A | High |
| iOS Class Chain | Medium | N/A | Medium |
| Android UiSelector | N/A | Fast | High |
| XPath | Slow | Slow | Low |

## Debugging Selectors

### Using Appium Inspector

1. Start Appium Inspector
2. Connect to running app
3. Click on elements to see available attributes
4. Test selectors before using in code

### Console Debugging

```typescript
// Log all elements of a type
const buttons = await driver.$$('android.widget.Button');
for (const btn of buttons) {
  console.log(await btn.getAttribute('text'));
  console.log(await btn.getAttribute('resource-id'));
}

// Check element hierarchy
const source = await driver.getPageSource();
console.log(source);
```

## Selector Anti-Patterns

| Anti-Pattern | Problem | Better Approach |
|-------------|---------|-----------------|
| `//Button[1]` | Index changes | Use testID |
| Long XPath chains | Brittle | Shorter unique selector |
| Text in selector | Fails with i18n | Use testID |
| Generated class names | Change on rebuild | Use testID |
| Absolute paths | Break on layout changes | Relative with testID |
