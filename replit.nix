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
        pkgs.playwright-driver

    ];
    env = {Add commentMore actions
        PYTHONBIN = "${pkgs.python311Full}/bin/python3.11";
        CHROME_BIN = "${pkgs.chromium}/bin/chromium";
        CHROMEDRIVER_PATH = "${pkgs.chromedriver}/bin/chromedriver";
        PYTHONPATH = "${pkgs.python311Packages.setuptools}/${pkgs.python311.sitePackages}";
        PLAYWRIGHT_BROWSERS_PATH = "${pkgs.playwright-driver.browsers}";
    };
} 