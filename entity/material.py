from dataclasses import dataclass


@dataclass
class Material:
    material_id: str
    material_name: str
    material_type: str
    subject: str
    start_time: str
    end_time: str
