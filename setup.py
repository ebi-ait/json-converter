import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="json-converter",
    version="0.1.0",
    description="json-converter is a tool for translating/converting a JSON document into another JSON document with a different structure.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ebi-ait/json-converter",
    packages=setuptools.find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent"
    ],
    python_requires='>=3.8',
)
