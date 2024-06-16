Required libraries:
    websocket-client
    PyATEMMax

Simple Description:
    Detects when ATEM switcher switches program source and sends that information to obs to apply a filter for color grading.

NOTE: Until further configuration is added you will need to have the OBS filter be the same name as the source. e.g. have a filter called input1 (no spaces) which will then be dedicated to input1 of the ATEM switcher.
