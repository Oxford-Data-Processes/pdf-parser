TO DO:

- Add unit tests (pytest)
- Create API tests using jest/typescript
- Create automated template builder
- Auto generate project documentation (sphinx?)
- Set up CI/CD to run tests on each pr or commit.
- Create a changelog
- Create performance tests
- Build diagrams for the project, formal diagrams expressed in code with auto-generation from code


Start up:

python -m venv venv
source venv/bin/activate
pip install -r requirements_dev.txt

API:

docker build -t pdf-parser-api ./api
docker run -p 8000:8000 -v $(pwd)/src:/app/src pdf-parser-api

Local:

uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload

Checks:

pre-commit run --all-files

mypy {path_to_file_or_directory} --explicit-package-bases