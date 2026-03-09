# app/models/printer.py

from dataclasses import dataclass


@dataclass
class Printer:
    nome: str
    ip: str
    departamento: str

    def to_dict(self) -> dict:
        return {
            "nome": self.nome.strip(),
            "ip": self.ip.strip(),
            "departamento": self.departamento.strip(),
        }