from setuptools import setup, find_packages

def read_requirements(file):
    with open(file, "r") as f:
        return [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name="WasteAndMaterialFootprint",
    version="0.1.0",
    description="A tool for analyzing waste and material footprints.",
    author="Stewart Charles McDowall | Stew-McD",
    author_email="s.c.mcdowall@cml.leidenuniv.nl",
    url="https://github.com/Stew-McD/WasteAndMaterialFootprint",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=read_requirements("requirements.txt"),
    extras_require={
        "dev": read_requirements("requirements-dev.txt"),
        "docs": read_requirements("requirements-docs.txt"),
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: The Unlicense (Unlicense)",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Information Analysis",
    ],
    python_requires=">=3.6",
)
