TO DO:

- Run mypy/ruff again
- Add unit tests (pytest)
- Create API tests using jest/typescript
- Create automated template builder
- Auto generate project documentation (sphinx?)
- Set up CI/CD to run tests on each pr or commit.
- Create a changelog
- Create performance tests
- Build diagrams for the project, formal diagrams expressed in code with auto-generation from code

Bugs:

- Barclays:
  - Use statement date year is not working

Start up:

python -m venv venv
source venv/bin/activate
pip install -r requirements_dev.txt



Checks:

pre-commit run --all-files

mypy {path_to_file_or_directory} --explicit-package-bases


Generate types:

npm run generate-types