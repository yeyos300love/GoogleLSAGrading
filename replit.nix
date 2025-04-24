{ pkgs }: {
    deps = [
        pkgs.python38
        pkgs.python38Packages.pip
        pkgs.chromium
        pkgs.chromedriver
        pkgs.geckodriver
        pkgs.xvfb-run
        pkgs.which
        pkgs.python38Packages.selenium
        pkgs.python38Packages.numpy
        pkgs.python38Packages.setuptools
        pkgs.python38Packages.wheel
        pkgs.gnumake
        pkgs.gcc
        pkgs.nodejs
    ];
    env = {
        PYTHONBIN = "${pkgs.python38}/bin/python3.8";
        CHROME_BIN = "${pkgs.chromium}/bin/chromium";
        CHROMEDRIVER_PATH = "${pkgs.chromedriver}/bin/chromedriver";
    };
} 