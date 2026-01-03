---
name: new-appium-test
description: Create a new Appium E2E test file with boilerplate
args: <screen-name> [test-description]
---

# Create New Appium Test

Create a new Appium E2E test file for the specified screen.

## Arguments
- `screen-name`: Name of the screen to test (e.g., "Login", "Profile", "Cart")
- `test-description` (optional): Brief description of what to test

## Steps

1. **Analyze the Screen**
   - Read the screen component file at `src/screens/{ScreenName}Screen.tsx` or similar
   - Identify all interactive elements and their testIDs
   - Understand the screen's purpose and user flows

2. **Check for Existing Page Object**
   - Look in `tests/e2e/screens/{ScreenName}Screen.ts`
   - If it doesn't exist, create it

3. **Create Test File**
   - Create `tests/e2e/specs/{screen-name}.spec.ts`
   - Include common test scenarios based on screen analysis

4. **List Missing testIDs**
   - Report any interactive elements without testIDs
   - Suggest testID values following the naming convention

## Output Structure

```
tests/e2e/
├── specs/
│   └── {screen-name}.spec.ts    # New test file
├── screens/
│   └── {ScreenName}Screen.ts    # Page object (if needed)
└── wdio.conf.ts                 # Verify config exists
```

## Test Template

```typescript
import { ${ScreenName}Screen } from '../screens/${ScreenName}Screen';

describe('${ScreenName} Screen', () => {
  let screen: ${ScreenName}Screen;

  beforeEach(async () => {
    screen = new ${ScreenName}Screen(driver);
    await screen.waitForDisplayed();
  });

  afterEach(async function() {
    if (this.currentTest?.state === 'failed') {
      const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
      await driver.saveScreenshot(`./screenshots/${screen-name}-\${timestamp}.png`);
    }
  });

  describe('initial state', () => {
    it('should display the screen correctly', async () => {
      // Add assertions for visible elements
    });
  });

  describe('user interactions', () => {
    it('should handle primary action', async () => {
      // Add test for main user flow
    });
  });

  describe('error states', () => {
    it('should show error message on invalid input', async () => {
      // Add test for error handling
    });
  });
});
```

## Run Command

After creating the test:

```bash
# Run the new test
npx wdio run wdio.conf.ts --spec tests/e2e/specs/${screen-name}.spec.ts
```
