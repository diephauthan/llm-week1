from pydantic import BaseModel, Field, ValidationError

class Report(BaseModel):
    machine_id: str
    wear_um: float = Field(ge=0)
    note: str = ""

r = Report(machine_id="cnc03", wear_um=180)
print(r)
print(r.wear_um +20)

r2 = Report.model_validate_json('{"machine_id": "cnc05", "wear_um": "95.5"}')
print(r2.wear_um, type(r2.wear_um))

try:
    Report(machine_id="cnc03", wear_um=-50)
except ValidationError as e:
    print(e)