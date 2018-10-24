This repo contains code and development for the Land Cover use case, providing spatial coverage of surveyed area, reasonable estimates on atmospheric contributions, and comparisons to a spectral library of known geologic materials.

Directory structure:
    src
        utils (containing setup instructions, xml reader etc.)
        lib (earth-sun distance lookup table, etc)
        cal (atmospheric correction and other calibration code)
        classification (land cover classification code)
        entk_scripts (Ensemble pipeline scripts)

    validation_suite (code to check installation and testing results)

