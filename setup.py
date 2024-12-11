from setuptools import setup, find_packages

setup(
    name="pdf-parser",
    version="0.1.0",
    author="Oxford Data Processes",
    author_email="info@oxforddataprocesses.com",
    description="Package for parsing PDF documents",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Oxford-Data-Processes/pdf-parser",
    packages=find_packages(include=["pdf_parser", "pdf_parser.*"]),
    package_data={
        "pdf_parser": ["schema/*.json"],
    },
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.11",
    install_requires=[
        "pdf2image",
        "pdfplumber",
        "numpy",
        "pytesseract",
        "Pillow",
        "python-multipart",
        "pydantic",
        "jsonschema",
    ],
)
