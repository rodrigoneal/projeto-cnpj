from dataclasses import dataclass


@dataclass
class Resposta:
    id: str
    cnpj: str

    def to_json(self):
        return {"id": self.id}
