# Appium Capabilities Reference for React Native/Expo

## Overview

Capabilities configure the Appium session - what device to use, which app to test, and how to behave. This reference covers the most important capabilities for React Native testing.

## Core Capabilities

### Platform Identification

```typescript
const capabilities = {
  // Required: Target platform
  platformName: 'Android', // or 'iOS'

  // Required: Automation driver
  'appium:automationName': 'UiAutomator2', // Android
  // or
  'appium:automationName': 'XCUITest', // iOS
};
```

### Device Selection

```typescript
// Android Emulator
const androidCaps = {
  'appium:deviceName': 'Pixel_6_API_33', // AVD name
  'appium:platformVersion': '13',
  'appium:udid': 'emulator-5554', // Optional: specific emulator
};

// Android Physical Device
const androidPhysicalCaps = {
  'appium:deviceName': 'My Phone',
  'appium:udid': 'ABCD1234567890', // From `adb devices`
  'appium:platformVersion': '14',
};

// iOS Simulator
const iosSimCaps = {
  'appium:deviceName': 'iPhone 15 Pro',
  'appium:platformVersion': '17.0',
};

// iOS Physical Device
const iosPhysicalCaps = {
  'appium:deviceName': 'My iPhone',
  'appium:udid': '00008110-XXXX', // From Xcode/iTunes
  'appium:platformVersion': '17.0',
  'appium:xcodeOrgId': 'YOUR_TEAM_ID',
  'appium:xcodeSigningId': 'iPhone Developer',
};
```

### App Configuration

```typescript
// Local APK/IPA
const appCaps = {
  'appium:app': '/absolute/path/to/app.apk',
  // or
  'appium:app': '/absolute/path/to/app.app', // iOS Simulator
  // or
  'appium:app': '/absolute/path/to/app.ipa', // iOS Device
};

// Already installed app (Android)
const installedAppCaps = {
  'appium:appPackage': 'com.mycompany.myapp',
  'appium:appActivity': '.MainActivity',
  // Don't set 'appium:app' when using package/activity
};

// Already installed app (iOS)
const installedIosCaps = {
  'appium:bundleId': 'com.mycompany.myapp',
  // Don't set 'appium:app' when using bundleId
};

// Expo Go (for development)
const expoGoCaps = {
  'appium:app': 'host.exp.Exponent', // Expo Go bundle ID (iOS)
  // or
  'appium:appPackage': 'host.exp.exponent', // Expo Go (Android)
  'appium:appActivity': '.experience.HomeActivity',
};
```

## Session Behavior

### State Management

```typescript
const stateCaps = {
  // Don't reinstall app between sessions
  'appium:noReset': true,

  // Full reset: uninstall and reinstall app
  'appium:fullReset': false,

  // Keep app data but restart app
  'appium:noReset': false,
  'appium:fullReset': false, // Default behavior
};
```

### Timeouts

```typescript
const timeoutCaps = {
  // Command timeout (seconds) - default 60
  'appium:newCommandTimeout': 300,

  // Implicit wait (milliseconds)
  'appium:implicitWait': 0, // Prefer explicit waits

  // App launch timeout (milliseconds)
  'appium:appWaitDuration': 30000,

  // WebDriverIO-level timeouts
  // (set in wdio.conf.ts, not capabilities)
};
```

## Android-Specific Capabilities

```typescript
const androidCaps = {
  platformName: 'Android',
  'appium:automationName': 'UiAutomator2',

  // App settings
  'appium:app': '/path/to/app.apk',
  'appium:appPackage': 'com.mycompany.myapp',
  'appium:appActivity': '.MainActivity',
  'appium:appWaitActivity': '.SplashActivity', // Wait for specific activity

  // Permissions
  'appium:autoGrantPermissions': true, // Auto-grant runtime permissions

  // Performance
  'appium:skipDeviceInitialization': false,
  'appium:skipServerInstallation': false,
  'appium:skipUnlock': true,
  'appium:ignoreHiddenApiPolicyError': true,

  // Network ports (useful for parallel runs)
  'appium:systemPort': 8200, // UiAutomator2 server port
  'appium:mjpegServerPort': 7810,
  'appium:chromedriverPort': 9515,

  // Chrome/WebView (for hybrid apps)
  'appium:autoWebview': false,
  'appium:chromedriverExecutable': '/path/to/chromedriver',

  // Debugging
  'appium:printPageSourceOnFindFailure': true,
  'appium:enablePerformanceLogging': false,

  // Emulator-specific
  'appium:isHeadless': false,
  'appium:avd': 'Pixel_6_API_33', // Launch specific AVD
  'appium:avdLaunchTimeout': 120000,
  'appium:avdReadyTimeout': 120000,
};
```

## iOS-Specific Capabilities

```typescript
const iosCaps = {
  platformName: 'iOS',
  'appium:automationName': 'XCUITest',

  // Device
  'appium:deviceName': 'iPhone 15',
  'appium:platformVersion': '17.0',

  // App
  'appium:app': '/path/to/MyApp.app',
  'appium:bundleId': 'com.mycompany.myapp',

  // Simulator specific
  'appium:simulatorStartupTimeout': 120000,
  'appium:connectHardwareKeyboard': false,

  // Real device specific
  'appium:udid': 'device-udid',
  'appium:xcodeOrgId': 'YOUR_TEAM_ID',
  'appium:xcodeSigningId': 'iPhone Developer',
  'appium:updatedWDABundleId': 'com.mycompany.WebDriverAgentRunner',

  // Permissions and alerts
  'appium:autoAcceptAlerts': true,
  'appium:autoDismissAlerts': false,

  // Performance
  'appium:useNewWDA': false,
  'appium:usePrebuiltWDA': true,
  'appium:wdaStartupRetries': 4,
  'appium:wdaStartupRetryInterval': 20000,

  // WebView (hybrid apps)
  'appium:webviewConnectRetries': 8,
  'appium:safariAllowPopups': true,

  // Debugging
  'appium:showXcodeLog': true,
  'appium:showIOSLog': false,
};
```

## Expo-Specific Configuration

### Development Build

```typescript
const expoDevCaps = {
  platformName: 'Android',
  'appium:automationName': 'UiAutomator2',
  'appium:app': './builds/my-app-dev.apk', // EAS development build
  'appium:autoGrantPermissions': true,
  'appium:noReset': false,
};
```

### EAS Build Integration

```bash
# Build for testing
eas build --profile test --platform android --local

# The output APK/IPA path can be passed to capabilities
```

### Development Client vs Production

```typescript
// Development client (for dev builds)
const devClientCaps = {
  'appium:app': './builds/dev-client.apk',
  // May need to handle Expo dev menu
};

// Production build (for release testing)
const productionCaps = {
  'appium:app': './builds/production.apk',
  // Simpler setup, no dev menu
};
```

## Complete Configuration Examples

### Android Emulator + Local APK

```typescript
export const androidConfig = {
  platformName: 'Android',
  'appium:automationName': 'UiAutomator2',
  'appium:deviceName': 'Pixel_6_API_33',
  'appium:app': path.resolve('./builds/app-debug.apk'),
  'appium:autoGrantPermissions': true,
  'appium:newCommandTimeout': 240,
  'appium:noReset': false,
  'appium:printPageSourceOnFindFailure': true,
};
```

### iOS Simulator + Local Build

```typescript
export const iosConfig = {
  platformName: 'iOS',
  'appium:automationName': 'XCUITest',
  'appium:deviceName': 'iPhone 15',
  'appium:platformVersion': '17.0',
  'appium:app': path.resolve('./builds/MyApp.app'),
  'appium:autoAcceptAlerts': true,
  'appium:newCommandTimeout': 240,
  'appium:noReset': false,
};
```

### CI/CD Environment Variables

```typescript
const ciConfig = {
  platformName: process.env.PLATFORM || 'Android',
  'appium:automationName': process.env.PLATFORM === 'iOS' ? 'XCUITest' : 'UiAutomator2',
  'appium:deviceName': process.env.DEVICE_NAME || 'emulator-5554',
  'appium:app': process.env.APP_PATH || './builds/app.apk',
  'appium:platformVersion': process.env.PLATFORM_VERSION,
};
```

## Troubleshooting Capabilities

| Issue | Capability Fix |
|-------|----------------|
| Session timeout | Increase `newCommandTimeout` |
| Permissions denied | Set `autoGrantPermissions: true` |
| App not starting | Check `appPackage`/`appActivity` |
| WebView not found | Set `autoWebview: true` |
| Slow startup | Use `skipDeviceInitialization` |
| Port conflicts | Change `systemPort`, `mjpegServerPort` |
| iOS signing fails | Check `xcodeOrgId`, `xcodeSigningId` |
