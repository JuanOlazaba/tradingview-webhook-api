"""Uso:
  python -m finroots.cli daily [--no-publish] [--no-render]   # comité diario: 1 reel
  python -m finroots.cli board                                # consejo semanal
  python -m finroots.cli improve [tema]                       # reunión de mejora (contenido, crecimiento,
                                                              #   monetizacion, tecnologia, finanzas, riesgos)
  python -m finroots.cli sync                                 # lee las respuestas del dueño
  python -m finroots.cli panel                                # regenera PANEL.md
  python -m finroots.cli render N                             # renderiza el episodio N ya escrito
  python -m finroots.cli validate N                           # valida el JSON del episodio N
  python -m finroots.cli auth-url REDIRECT_URI                # URL para conectar la cuenta de TikTok
  python -m finroots.cli mark-published N                     # marcar como subido a mano
"""
import json
import sys

from . import pipeline, tiktok
from .company import load_config, load_episodes, save_episodes
from .episode import validate


def main(argv):
    if not argv:
        print(__doc__)
        return 1
    cmd, rest = argv[0], argv[1:]
    if cmd == "daily":
        r = pipeline.daily(publish="--no-publish" not in rest, render="--no-render" not in rest)
    elif cmd == "board":
        r = pipeline.board()
    elif cmd == "improve":
        r = pipeline.improve(rest[0] if rest else None)
    elif cmd == "sync":
        pipeline.handle_owner_decisions()
        from .ledger import write_panel
        write_panel()
        r = {"ok": True}
    elif cmd == "panel":
        from .ledger import write_panel
        write_panel()
        r = {"ok": True}
    elif cmd in ("render", "validate"):
        n = int(rest[0])
        ep = json.loads((pipeline._ep_dir(n) / "episode.json").read_text(encoding="utf-8"))
        if cmd == "validate":
            r = {"errors": validate(ep)}
        else:
            from .render import render_episode
            r = render_episode(ep, pipeline._ep_dir(n), load_config())
    elif cmd == "auth-url":
        r = {"url": tiktok.auth_url(rest[0])}
    elif cmd == "mark-published":
        eps = load_episodes()
        for e in eps:
            if e["number"] == int(rest[0]):
                e["status"] = "published_manually"
        save_episodes(eps)
        r = {"ok": True}
    else:
        print(__doc__)
        return 1
    print(json.dumps(r, ensure_ascii=False, indent=1, default=str))
    return 0 if r.get("ok", True) and not r.get("errors") else 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
