"""La empresa: agentes con rol propio que conversan en reuniones con acta compartida."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from . import llm
from .episode import catalog_text

ROOT = Path(__file__).parent
STATE = ROOT / "state"

ROLES = {
    "ceo": "CEO", "board": "Consejo", "ideas": "Ideas", "marketing": "Marketing", "product": "Producto",
    "studio": "Estudio", "compliance": "Compliance", "it": "IT", "operations": "Operaciones",
}


def load_config() -> dict:
    return yaml.safe_load((ROOT / "config.yaml").read_text(encoding="utf-8"))


def load_episodes() -> list[dict]:
    return json.loads((STATE / "episodes.json").read_text(encoding="utf-8"))


def save_episodes(eps: list[dict]):
    (STATE / "episodes.json").write_text(json.dumps(eps, ensure_ascii=False, indent=2), encoding="utf-8")


def company_context(cfg: dict) -> str:
    """Contexto común para todos los agentes (va primero en el prompt de sistema y se cachea)."""
    eps = load_episodes()[-12:]
    hist = "\n".join(f"- Ep. {e['number']} · {e['title']} · tema: {e['topic']} · idea: {e['core_idea']} · "
                     f"objetos: {', '.join(e.get('objects', []))} · estado: {e.get('status')}" for e in eps)
    kpis = json.loads((STATE / "kpis.json").read_text()).get("history", [])[-1:] or ["(todavía sin métricas)"]
    from . import owner
    dec = STATE / "ceo_decisions.md"
    decisions = "\n".join(dec.read_text(encoding="utf-8").strip().splitlines()[-25:]) if dec.exists() else "(ninguna)"
    return f"""Eres parte del equipo de agentes que dirige Finroots de forma autónoma para su dueño.
Todo lo que producís se publica de verdad: sed rigurosos, concretos y honestos. No inventéis métricas.

# MARCA
{yaml.safe_dump(cfg['brand'], allow_unicode=True)}
# BIBLIA DE LA SERIE
{(ROOT / 'bible.md').read_text(encoding='utf-8')}

# DIRECTIVAS VIGENTES DEL CONSEJO
{(STATE / 'directives.md').read_text(encoding='utf-8')}

# EPISODIOS RECIENTES
{hist}

# ÚLTIMAS MÉTRICAS
{json.dumps(kpis[-1], ensure_ascii=False)[:3000]}

# BACKLOG
{(STATE / 'backlog.md').read_text(encoding='utf-8')}

# GUÍA DE ESTILO DEL DUEÑO (OBLIGATORIA)
{(ROOT / 'company' / 'owner_style.md').read_text(encoding='utf-8')}

# GOBIERNO: QUÉ PODÉIS HACER SOLOS Y QUÉ NECESITA AL DUEÑO
{(ROOT / 'governance.md').read_text(encoding='utf-8')}

# CANAL CON EL DUEÑO
{owner.context_text()}

# DECISIONES RECIENTES DE DIRECCIÓN
{decisions}

# MOTOR DE VÍDEO
{catalog_text()}
"""


@dataclass
class Meeting:
    title: str
    cfg: dict
    log: list[tuple[str, str]] = field(default_factory=list)
    _ctx: str | None = None

    @property
    def ctx(self) -> str:
        if self._ctx is None:
            self._ctx = company_context(self.cfg)
        return self._ctx

    def transcript(self, limit_chars: int = 60000) -> str:
        t = "\n\n".join(f"**{ROLES.get(w, w)}:**\n{x}" for w, x in self.log)
        return t[-limit_chars:]

    def say(self, role: str, task: str, want_json: bool = False, record: bool = True, retries: int = 2):
        persona = (ROOT / "company" / f"{role}.md").read_text(encoding="utf-8")
        system = [
            {"type": "text", "text": self.ctx, "cache_control": {"type": "ephemeral"}},
            {"type": "text", "text": persona},
        ]
        user = (f"# Reunión: {self.title}\n\n## Lo dicho hasta ahora\n{self.transcript() or '(empiezas tú)'}\n\n"
                f"## Tu turno ({ROLES[role]})\n{task}")
        if want_json:
            user += "\n\nResponde con un único bloque ```json``` válido y nada más fuera de él."
        model = self.cfg["models"].get(role + "_model") or self.cfg["models"]["default"]
        effort = self.cfg["models"]["effort"].get(role, "medium")
        last_err = None
        for _ in range(retries + 1):
            text = llm.ask(system, user if last_err is None else user + f"\n\n(Tu respuesta anterior no era JSON válido: {last_err}. Repite solo el JSON.)",
                           model=model, effort=effort, role=role)
            if not want_json:
                if record:
                    self.log.append((role, text))
                print(f"  · {ROLES[role]} ha hablado ({len(text)} caracteres)")
                return text
            try:
                obj = llm.extract_json(text)
                if record:
                    self.log.append((role, "```json\n" + json.dumps(obj, ensure_ascii=False, indent=1)[:12000] + "\n```"))
                print(f"  · {ROLES[role]} ha hablado (JSON)")
                return obj
            except ValueError as e:
                last_err = str(e)
        raise RuntimeError(f"{ROLES[role]} no devolvió JSON válido: {last_err}")

    def note(self, who: str, text: str):
        self.log.append((who, text))

    def minutes(self) -> str:
        return f"# {self.title}\n\n" + "\n\n".join(f"### {ROLES.get(w, w)}\n{x}" for w, x in self.log) + "\n"
