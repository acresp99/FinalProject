from sqlmodel import SQLModel, Field, Session, create_engine, delete
import pandas as pd


class StatePopulation(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    state: str
    population: str
    annual_change: str


DB_NAME = "state_pop.db"
engine = create_engine(f"sqlite:///{DB_NAME}")


def create_database() -> None:
    SQLModel.metadata.create_all(engine)

    df = pd.read_csv("state_pop.csv")
    df = df.rename(
        columns={"State": "state", "Population": "population", "Annual Change": "annual_change"}
    )
    records = [StatePopulation(**row) for row in df.to_dict(orient="records")]

    with Session(engine) as session:
        session.exec(delete(StatePopulation))
        session.add_all(records)
        session.commit()


if __name__ == "__main__":
    create_database()