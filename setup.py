import os
import setuptools

def long_description_read():
    with open("README.md") as readme_file:
        long_description = readme_file.read()
    return long_description

environment = os.environ
assert "BOM_VERSION" in environment, "BOM_VERSION environment variable is not set"
version = environment["BOM_VERSION"]

# Arguments to *setup*() are in alphabetical order:
setuptools.setup(
    author="Wayne Gramlich",
    author_email="Wayne@Gramlich.Net",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    description=("BOM Manager plugin for accessing electronic parts "
                 "pricing and availability from FindChips.Com ."),
    entry_points = {
        "bom_manager_panda_get": ["panda_get=bom_findchips_plugin.findchips:panda_get"],
    },
    #include_package_data=True,
    # install_requires = [
    #     "bs4",
    # ],
    license="MIT",
    long_description=long_description_read(),
    long_description_content_type="text/markdown",
    name="bom_findchips_plugin_waynegramlich",
    packages=[
        "bom_findchips_plugin",
    ],
    python_requires=">=3.6",
    url="https://github.com/waynegramlich/bom_findchips_plugin",
    version=version,
)
