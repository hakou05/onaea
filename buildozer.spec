[app]

# (str) Title of your application
title = برنامج إدخال معلومات المتمدرسين

# (str) Package name
package.name = onaea_app

# (str) Package domain (needed for android/ios packaging)
package.domain = org.onaea

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,gif,db

# (list) List of inclusions using pattern matching
source.include_patterns = assets/*

# (str) Application versioning (method 1)
version = 1.0

# (list) Application requirements
requirements = python3,flet==0.10.0,pandas==2.0.0,openpyxl==3.0.0,kivy,pillow

# (str) Presplash of the application
presplash.filename = logo.gif

# (str) Icon of the application
icon.filename = logo.gif

# (str) Supported orientation (one of landscape, sensorLandscape, portrait or all)
orientation = portrait

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (list) Permissions
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

# (int) Target Android API, should be as high as possible.
android.api = 33

# (int) Minimum API your APK will support.
android.minapi = 21

# (str) Android NDK version to use
android.ndk = 23b

# (bool) If True, then skip trying to update the Android sdk
# This can be useful to avoid excess Internet downloads or save time
# when an update is due and you just want to test/build your package
android.skip_update = False

# (bool) If True, then automatically accept SDK license
# agreements. This is intended for automation only. If set to False,
# the default, you will be shown the license when first running
# buildozer.
android.accept_sdk_license = True

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2