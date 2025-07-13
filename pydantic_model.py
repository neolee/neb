from pydantic import BaseModel
from pydantic_ai import Agent
import models as m

import instrument
instrument.init()


class MyModel(BaseModel):
    city: str
    country: str


city_agent = Agent(m.default, output_type=MyModel)

if __name__ == '__main__':
    # result = city_agent.run_sync('The windy city in the USA.')
    result = city_agent.run_sync('The capital city of PR of China.')
    print(result.output)
    print(result.usage())
