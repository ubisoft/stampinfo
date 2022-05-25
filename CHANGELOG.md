## 1.2.1 (2022-05-24)

- Added a property to specify the time context to use for the output images indices
- Added a property to set the start frame on video (videoFirstFrameIndex)
- Added a property to control the number of digits in the frame numbers (frameDigitsPadding)
- Added an add-on preferences property to toggle the visibility of the main UI panel in the 3D View

#### Code
- Add-on Preference property named mediaFirstFrameIsZero has been removed, it is now
  advantageously replaced by videoFirstFrameIndex

## 1.1.2 (2022-05-11)

- Fix on the get latest release version path


## 1.1.1 (2022-05-11)
- Support for Blender 3.1+ and Python 3.10

#### Code

- Code cleaning and updated to match the implementation of Ubisoft Shot Manager add-on
- Added custom class of Logger
- (partly) changed the global debug variable gbWkDebug to a variable devDebug stored in config.py

## 1.0.17 (2022-01-15)

- Added function evaluateRenderResolutionForStampInfo


## 1.0.15 (2021-11-02)

#### Features

- Improved tooltips and explanations about animation ranges
- Added a text field for Sequence
- Set date and time on by default


## 1.0.14 (2021-10-29)

#### Bug fix

- Logos built-in path was broken


## 1.0.13 (2021-09-28)

#### Installation

- Improved again error catching for better user feedback when not in admin mode


## 1.0.12 (2021-09-23)

#### Installation

- Improved error catching with pip download timeout


## 1.0.11 (2021-09-23)

#### Documentation

- Online documentation now available here: [Ubisoft Stamp Info](https://ubisoft-stampinfo.readthedocs.io/)

#### UI and Installation

- Provided better user feedback at install time in case of errors


## 1.0.9 (2021-08-20)

#### UI

- Refactored messagebox function
- Added a query messagebox operator
- Added a Reset All Properties function
- Improved the rendering usability by reducing the blocking rendering cases
- Fix: Frame ranges are now disabled again when unchecked in the UI


## 1.0.8 (05/07/2021)

- Rewamped UI
- Improved documentation


## 1.0.1 (2021-06-12)

- Removed handlers and use of the compositing editor that were used to generate the final images
because code was unstable and complicated
- Added 2 Render buttons and a batch based on the VSE to create the final images


--------

## 0.9.x - Production versions

