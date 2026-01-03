---
name: setup-appium
description: Set up Appium testing environment for React Native/Expo project
---

# Set Up Appium Testing Environment

Initialize Appium E2E testing infrastructure for a React Native or Expo project.

## Prerequisites Check

First, verify the following are installed:

```bash
# Check Node.js
node --version  # Should be 18+

# Check Java (for Android)
java --version  # Should be 11+

# Check Xcode (for iOS, macOS only)
xcodebuild -version

# Check Android SDK
echo $ANDROID_HOME
adb --version
```

## Step 1: Install Appium

```bash
# Install Appium globally
npm install -g appium

# Install drivers
appium driver install uiautomator2  # Android
appium driver install xcuitest      # iOS (macOS only)

# Verify installation
appium --version
appium driver list --installed
```

## Step 2: Install WebDriverIO

```bash
# In project root
npm install --save-dev \
  @wdio/cli \
  @wdio/local-runner \
  @wdio/mocha-framework \
  @wdio/spec-reporter \
  webdriverio \
  ts-node \
  typescript \
  @types/mocha
```

## Step 3: Create Configuration

Create `wdio.conf.ts`:

```typescript
import type { Options } from '@wdio/types';
import path from 'path';

// Determine platform from environment
const isIOS = process.env.PLATFORM === 'ios';
const isAndroid = process.env.PLATFORM === 'android' || !isIOS;

// Get app path from environment or use defaults
const getAppPath = (): string => {
  if (process.env.APP_PATH) return process.env.APP_PATH;

  if (isIOS) {
    // For Expo/EAS builds
    return path.resolve('./builds/app.app');
  }
  // For Android
  return path.resolve('./builds/app.apk');
};

const androidCapabilities = {
  platformName: 'Android',
  'appium:automationName': 'UiAutomator2',
  'appium:deviceName': process.env.DEVICE_NAME || 'Android Emulator',
  'appium:app': getAppPath(),
  'appium:autoGrantPermissions': true,
  'appium:newCommandTimeout': 240,
  'appium:noReset': false,
};

const iosCapabilities = {
  platformName: 'iOS',
  'appium:automationName': 'XCUITest',
  'appium:deviceName': process.env.DEVICE_NAME || 'iPhone 15',
  'appium:platformVersion': process.env.IOS_VERSION || '17.0',
  'appium:app': getAppPath(),
  'appium:autoAcceptAlerts': true,
  'appium:newCommandTimeout': 240,
  'appium:noReset': false,
};

export const config: Options.Testrunner = {
  runner: 'local',
  tsConfigPath: './tsconfig.json',

  specs: ['./tests/e2e/specs/**/*.spec.ts'],
  exclude: [],

  maxInstances: 1,

  capabilities: [isIOS ? iosCapabilities : androidCapabilities],

  logLevel: 'info',
  bail: 0,

  baseUrl: '',
  waitforTimeout: 10000,
  connectionRetryTimeout: 120000,
  connectionRetryCount: 3,

  port: 4723,

  framework: 'mocha',
  mochaOpts: {
    ui: 'bdd',
    timeout: 120000,
  },

  reporters: ['spec'],

  // Hooks
  beforeSession: async function () {
    // Start Appium server if not running
  },

  afterTest: async function (test, context, { error }) {
    if (error) {
      const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
      await browser.saveScreenshot(`./screenshots/failure-${timestamp}.png`);
    }
  },
};
```

## Step 4: Create Directory Structure

```bash
mkdir -p tests/e2e/{specs,screens,utils}
mkdir -p screenshots
mkdir -p builds
```

## Step 5: Create Base Screen Class

Create `tests/e2e/screens/Screen.ts`:

```typescript
export class Screen {
  protected driver: WebdriverIO.Browser;

  constructor(driver: WebdriverIO.Browser) {
    this.driver = driver;
  }

  async waitForDisplayed(timeout = 10000): Promise<void> {
    // Override in subclasses
  }

  async takeScreenshot(name: string): Promise<void> {
    await this.driver.saveScreenshot(`./screenshots/${name}.png`);
  }

  async dismissKeyboard(): Promise<void> {
    if (this.driver.isIOS) {
      await this.driver.execute('mobile: hideKeyboard', {});
    } else {
      try {
        await this.driver.hideKeyboard();
      } catch {
        // Keyboard might not be visible
      }
    }
  }

  async scrollDown(): Promise<void> {
    const { height, width } = await this.driver.getWindowSize();
    await this.driver.touchAction([
      { action: 'press', x: width / 2, y: height * 0.8 },
      { action: 'wait', ms: 100 },
      { action: 'moveTo', x: width / 2, y: height * 0.2 },
      { action: 'release' }
    ]);
  }

  async scrollUp(): Promise<void> {
    const { height, width } = await this.driver.getWindowSize();
    await this.driver.touchAction([
      { action: 'press', x: width / 2, y: height * 0.2 },
      { action: 'wait', ms: 100 },
      { action: 'moveTo', x: width / 2, y: height * 0.8 },
      { action: 'release' }
    ]);
  }
}
```

## Step 6: Add npm Scripts

Add to `package.json`:

```json
{
  "scripts": {
    "appium": "appium",
    "test:e2e:android": "PLATFORM=android wdio run wdio.conf.ts",
    "test:e2e:ios": "PLATFORM=ios wdio run wdio.conf.ts",
    "test:e2e": "wdio run wdio.conf.ts",
    "build:android:test": "eas build --platform android --profile development --local",
    "build:ios:test": "eas build --platform ios --profile development-simulator --local"
  }
}
```

## Step 7: Configure EAS Build (for Expo)

Create/update `eas.json`:

```json
{
  "cli": {
    "version": ">= 5.0.0"
  },
  "build": {
    "development": {
      "developmentClient": true,
      "distribution": "internal"
    },
    "development-simulator": {
      "developmentClient": true,
      "distribution": "internal",
      "ios": {
        "simulator": true
      }
    },
    "test": {
      "android": {
        "buildType": "apk"
      },
      "ios": {
        "simulator": true
      }
    }
  }
}
```

## Step 8: Verify Setup

```bash
# Terminal 1: Start Appium server
appium

# Terminal 2: Run a simple test
npm run test:e2e:android
# or
npm run test:e2e:ios
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Appium not found | Run `npm install -g appium` |
| Driver not installed | Run `appium driver install uiautomator2` |
| App not found | Check APP_PATH or build the app first |
| Session timeout | Increase `newCommandTimeout` capability |
| Element not found | Check testID exists and use `waitForDisplayed` |

## Next Steps

1. Run `/new-appium-test Login` to create your first test
2. Run `/find-testids` to audit testID coverage
3. Review the TDD workflow skill for best practices
