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

        # Missing libraries for Playwright - mapped to Nix packages
        pkgs.nss              # provides libnss3.so, libnssutil3.so, libsmime3.so
        pkgs.nspr             # provides libnspr4.so
        pkgs.dbus             # provides libdbus-1.so.3
        pkgs.atk              # provides libatk-1.0.so.0
        pkgs.at-spi2-atk      # provides libatk-bridge-2.0.so.0
        pkgs.cups             # provides libcups.so.2
        pkgs.expat            # provides libexpat.so.1
        pkgs.libxcb           # provides libxcb.so.1
        pkgs.libxkbcommon     # provides libxkbcommon.so.0
        pkgs.at-spi2-core     # provides libatspi.so.0
        pkgs.xorg.libXcomposite  # provides libXcomposite.so.1
        pkgs.xorg.libXdamage     # provides libXdamage.so.1
        pkgs.xorg.libXfixes      # provides libXfixes.so.3
        pkgs.mesa             # provides libgbm.so.1
        pkgs.pango            # provides libpango-1.0.so.0
        pkgs.cairo            # provides libcairo.so.2
        pkgs.systemd          # provides libudev.so.1
        pkgs.alsa-lib         # provides libasound.so.2
    ];
    env = {
        PYTHONBIN = "${pkgs.python311Full}/bin/python3.11";
        CHROME_BIN = "${pkgs.chromium}/bin/chromium";
        CHROMEDRIVER_PATH = "${pkgs.chromedriver}/bin/chromedriver";
        PYTHONPATH = "${pkgs.python311Packages.setuptools}/${pkgs.python311.sitePackages}";
    };
} 