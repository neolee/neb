from pydantic import BaseModel
from pydantic_ai import Agent

import models as m


class CityLocation(BaseModel):
    city: str
    country: str


agent = Agent(model=m.default, output_type=CityLocation)
result = agent.run_sync('Where were the olympics held in 2012?')
print(result)
print(type(result.output))
print(result.output)
print(result.usage())
