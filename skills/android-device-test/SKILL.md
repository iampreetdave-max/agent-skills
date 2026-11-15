---
name: android-device-test
description: Test an Android app on a real phone or emulator over adb. Builds and installs it, drives the UI by tapping real on-screen elements, covers the flows that break on devices (network loss, backgrounding, process death, rotation) and reports pass or fail with screenshots and logcat. Use when the user says "test it on my phone", "run it on the device", connects an Android phone, or wants on-device proof that a change works.
---

# Android device test

With a phone connected over USB (or an emulator running) you can drive it yourself: install the build, tap through the app, and capture evidence. Proof on a device beats static code evidence.

## 0. Preflight

```
adb devices
```

- Exactly one device in state `device`: go on. More than one: pass `-s <serial>` on every command and say which device you used.
- `unauthorized`: ask the user to accept the "Allow USB debugging" prompt on the phone.
- Nothing listed: ask the user to check the cable (charge-only cables carry no data) and to turn on USB debugging (Settings > About phone > tap Build number 7 times, then Developer options > USB debugging).
- `adb` not found: look in the SDK, `%LOCALAPPDATA%\Android\Sdk\platform-tools` (Windows), `~/Library/Android/sdk/platform-tools` (macOS), `~/Android/Sdk/platform-tools` (Linux). If it is not there, ask. Never guess a path.

Note the screen size once: `adb shell wm size`.

## 1. Build and install

Use whatever the project already uses:

| Project | Build | APK |
|---|---|---|
| Flutter | `flutter build apk --debug` | `build/app/outputs/flutter-apk/app-debug.apk` |
| Native, or React Native (run in `android/`) | `./gradlew assembleDebug` | `app/build/outputs/apk/debug/app-debug.apk` |
| Expo | `npx expo run:android` builds and installs | |

```
adb install -r <apk>     # -r keeps app data, so the test account stays logged in
```

Find the package name with `adb shell pm list packages | grep -i <app name>` (`findstr /i` on Windows).

## 2. Logs

```
adb logcat -c                                                          # clear before the test
# ... run the flow ...
adb logcat -d -v time --pid=$(adb shell pidof -s <package>) > app.log  # this app only
adb logcat -d -b crash > crash.log                                     # crashes, even after the process died
```

Search them for `FATAL EXCEPTION`, `AndroidRuntime` and `ANR`. If the app talks to a server you can reach, tail its logs during the test and line the timestamps up.

## 3. Drive the UI by elements, not guessed pixels

```
adb shell monkey -p <package> -c android.intent.category.LAUNCHER 1     # launch
adb shell uiautomator dump /sdcard/ui.xml && adb pull /sdcard/ui.xml     # every element on screen
```

Find the element by its `text`, `content-desc` or `resource-id` in `ui.xml`, take the centre of its `bounds="[x1,y1][x2,y2]"`, and tap there:

```
adb shell input tap <x> <y>
adb shell input text "hello%sworld"       # types into the focused field; %s is a space
adb shell input swipe 540 1600 540 600 300
adb shell input keyevent 4                # back. 3 = home, 66 = enter, 67 = backspace
```

If the dump has nothing useful (games, canvases, Flutter screens without semantics labels), take a screenshot, look at it, and work out coordinates from the image. Dump or screenshot again after each tap to confirm it landed.

## 4. Screenshots at every step

```
adb shell screencap -p /sdcard/s.png && adb pull /sdcard/s.png step01-login.png
```

Do not use `adb exec-out screencap -p > file.png` in Windows PowerShell 5: the redirect re-encodes the bytes and corrupts the PNG. Look at every screenshot you take. A screenshot you did not look at is not evidence.

## 5. Flows that break on real devices

Run the flows the change touches, plus each of these that applies:

- **Cold start**: `adb shell am force-stop <package>`, launch, and time it to the first usable screen.
- **Network loss**: `adb shell svc wifi disable` and `adb shell svc data disable`, wait 10 seconds, use the app, then re-enable both. The app should show an offline state and recover, never a blank screen or a hang.
- **Background and return**: `adb shell input keyevent 3`, wait, relaunch. The user should land where they left off.
- **Process death**: background the app, `adb shell am kill <package>`, reopen it from recents. Saved state should restore. This one finds the most bugs.
- **Rotation**, if the app allows it: `adb shell settings put system accelerometer_rotation 0`, then `adb shell settings put system user_rotation 1`, and back to `0`.

## 6. Report

| Flow | Result | Evidence |
|---|---|---|
| Login | PASS | step01-login.png, step02-home.png |
| Network loss | FAIL: blank screen after reconnect | step05.png, app.log lines 210 to 240 |

A FAIL is reported as a FAIL with its screenshots and log excerpt, never softened. Keep the files and give their paths.

## Safety

- Test accounts only. Never act on a real user's account, and never send real messages, payments or purchases.
- Before finishing, even after a failure: re-enable wifi and data, and restore auto-rotate (`adb shell settings put system accelerometer_rotation 1`).
- Do not `adb uninstall` or `adb shell pm clear` (both wipe app data) unless the user asks for a clean install.
- Touch only the app under test.
