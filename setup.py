from setuptools import setup, find_packages

setup(
    name="koipond",
    version="1.0.0",
    description="KoiPond - Relax and take care of some koi!",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "pygame",
        "pygame_gui",
    ],
    entry_points={
        "console_scripts": [
            "koipond=koipond.main:main",
        ],
    },
    python_requires=">=3.7",
)