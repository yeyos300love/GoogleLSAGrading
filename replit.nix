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
    ];
} 