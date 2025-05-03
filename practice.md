# Head Alignment Tool for Photo "Multiverse" Effect

## Project Summary
This project involves developing a tool that aligns faces across different photos to create a "multiverse" effect by maintaining consistent head positions. The tool uses computer vision to detect facial features and align them according to a reference image.

## Development Journey

### Initial Development
- Built Python application using OpenCV, Mediapipe for face detection, and Tkinter for UI
- Implemented face alignment algorithm using eye positions as reference points
- Created options for reference image selection and background handling

### User Identified Issues
- UI buttons were unresponsive, requiring multiple clicks
- Interface elements blocked image viewing
- Confusion about parameters like "eye distance"
- Alignment results weren't satisfactory - heads weren't properly positioned

### Major Improvements
- Multi-threading to prevent UI freezing during processing
- Progress bars and visual feedback
- Redesigned UI with side panel controls
- Dark theme with color-coded buttons
- Better error handling and parameter explanations

### Final Enhancements
- Added head tilt detection feature to filter out photos where subject's head is tilted
- Implemented both horizontal (eye-line) and vertical (forehead-to-chin) tilt detection
- Added adjustable threshold control and UI to view skipped/filtered images
- Enhanced explanation of "eye distance" parameter (controls face size in output)

## Summary
The head alignment tool evolved from a basic implementation to a robust application with improved user experience, more precise alignment capabilities, and automatic filtering of unsuitable images. It effectively helps users create "multiverse" style photo compilations by maintaining consistent face positioning across different images. 