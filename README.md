TO DO:

- Clean up code
- Create FASTAPI endpoints (local)
- Add unit tests
- Create end to end tests (using fastapi endpoints)
- Create automated template builder
- Auto generate project documentation (sphinx?)
- Set up CI/CD to run tests on each pr or commit.
- Create a changelog
- Create performance tests
- Create a Docker container to test pulling and using of python package inside a container
- Build brew dependecies list
- Build diagrams for the project, formal diagrams expressed in code with auto-generation from code
- Set up project as a pacakage (use setup.cfg with poetry and complete README.md)


For template builder, run through OCR and Extraction and compare the words, see what % match. Use a threshold to classify as extraction or ocr method.

Only convert to jpg if the OCR method is used or if there is a max pixel value for lines.

Provide jpeg bytes in the pdf_data object for the OCR method.


Start up:

python -m venv venv
source venv/bin/activate
pip install -r requirements_dev.txt

Checks:

pre-commit run --all-files

mypy {path_to_file_or_directory} --explicit-package-bases
