{ pkgs }: {
    deps = [
        pkgs.python311Full
        pkgs.python311Packages.pip
        pkgs.chromium
        pkgs.chromedriver
        pkgs.geckodriver
        pkgs.xvfb-run
        pkgs.which
        pkgs.python311Packages.selenium
        pkgs.python311Packages.numpy
        pkgs.python311Packages.setuptools
        pkgs.python311Packages.wheel
        pkgs.gnumake
        pkgs.gcc
        pkgs.nodejs

        # Missing libraries for Playwright
        pkgs.nss
        pkgs.nspr
        pkgs.dbus
        pkgs.atk
        pkgs.at-spi2-atk
        pkgs.cups
        pkgs.libxcb
        pkgs.libxkbcommon
        pkgs.at-spi2-core
        pkgs.xorg.libXcomposite
        pkgs.xorg.libXdamage
        pkgs.xorg.libXfixes
        pkgs.mesa
        pkgs.pango
        pkgs.cairo
        pkgs.alsa-lib

    ];
    env = {
        PYTHONBIN = "${pkgs.python311Full}/bin/python3.11";
        CHROME_BIN = "${pkgs.chromium}/bin/chromium";
        CHROMEDRIVER_PATH = "${pkgs.chromedriver}/bin/chromedriver";
        PYTHONPATH = "${pkgs.python311Packages.setuptools}/${pkgs.python311.sitePackages}";
        PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH = "${pkgs.chromium}/bin/chromium";
    };
} 