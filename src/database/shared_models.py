from pydantic import constr, Field


class Id(constr):
    __root__: str = Field(
        ...,
        regex=r"^[a-f0-9]{8}-[a-f0-9]{4}-[1-5][a-f0-9]{3}-[89ab][a-f0-9]{3}-[a-f0-9]{12}$",
    )


class Name(constr):
    __root__: str = Field(..., max_length=50)
