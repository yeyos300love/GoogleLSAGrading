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
        # Add the missing libraries for Playwright/Chromium
        pkgs.nss
        pkgs.nspr
        pkgs.dbus
        pkgs.atk
        pkgs.at-spi2-atk
        pkgs.cups
        pkgs.expat
        pkgs.libxcb
        pkgs.libxkbcommon
        pkgs.at-spi2-core
        pkgs.libXcomposite
        pkgs.libXdamage
        pkgs.libXfixes
        pkgs.mesa # for libgbm
        pkgs.pango
        pkgs.cairo
        pkgs.systemd # for libudev
        pkgs.alsa-lib
        pkgs.gtk3
        pkgs.glib
        pkgs.fontconfig
        pkgs.freetype
    ];
    env = {
        PYTHONBIN = "${pkgs.python311Full}/bin/python3.11";
        CHROME_BIN = "${pkgs.chromium}/bin/chromium";
        CHROMEDRIVER_PATH = "${pkgs.chromedriver}/bin/chromedriver";
        PYTHONPATH = "${pkgs.python311Packages.setuptools}/${pkgs.python311.sitePackages}";
        LD_LIBRARY_PATH = "${pkgs.lib.makeLibraryPath [
            pkgs.nss
            pkgs.nspr
            pkgs.dbus
            pkgs.atk
            pkgs.at-spi2-atk
            pkgs.cups
            pkgs.expat
            pkgs.libxcb
            pkgs.libxkbcommon
            pkgs.at-spi2-core
            pkgs.libXcomposite
            pkgs.libXdamage
            pkgs.libXfixes
            pkgs.mesa
            pkgs.pango
            pkgs.cairo
            pkgs.systemd
            pkgs.alsa-lib
            pkgs.gtk3
            pkgs.glib
            pkgs.fontconfig
            pkgs.freetype
        ]}";
    };
} 