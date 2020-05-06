# Test OPI Creator
Control Systems Studio (CS-Studio) GUI to run an embedded Python program to replace all PVs in the screen with local PVs for testing

End result of program are two screens: a test screen and a control screen. The test screen is a copy of the input screen with all PVs changed to local PVs. The control screen is a copy of the test screen with all indicators changed to controls (and visa versa) and Boolean controls added for all PVs used in screen to trigger rules.

---

**Repository Contents:**

*  *make-test-screens.opi*
    *  CS-Studio screen with embedded program.
    *  Put this OPI in your CS-Studio workspace and run it to open GUI for program.

*  *make-test-screens_with-PV-check.opi*
    *  CSS-Studio screen with embedded program that includes the ability to check PVs on the screen.

*  *make-test-version.py*
    *  Python program embedded into OPI files.
    *  Program is not executable from Python environment since it relies on Jython functions in CS-Studio.
