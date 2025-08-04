{ pkgs }: {

    deps = [
        pkgs.python311Full
        pkgs.python311Packages.pip
        pkgs.chromium
        pkgs.chromedriver
        pkgs.geckodriver
        pkgs.xvfb-run
        pkgs.which
        pkgs.python311Packages.setuptools
        pkgs.python311Packages.wheel
        pkgs.gnumake
        pkgs.gcc
        pkgs.nodejs

    ];
    env = {
        PYTHONBIN = "${pkgs.python311Full}/bin/python3.11";
        CHROME_BIN = "${pkgs.chromium}/bin/chromium";
        CHROMEDRIVER_PATH = "${pkgs.chromedriver}/bin/chromedriver";
        PYTHONPATH = "${pkgs.python311Packages.setuptools}/${pkgs.python311.sitePackages}";
        PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH = "${pkgs.chromium}/bin/chromium";
    };
} 