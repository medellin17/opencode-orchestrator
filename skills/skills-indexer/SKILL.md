---
name: skills-indexer
description: Сканирует все доступные скиллы и генерирует `.orchestrator/skills-index.md` + `.orchestrator/skills-index.json`. Использовать когда skills-index старше 7 дней, отсутствует, или при добавлении/удалении скиллов.
---

# Skills Indexer

Сканирует три источника скиллов и генерирует индекс для оркестратора:

- `.opencode/skills/`, `.gemini/skills/` — локальные скиллы проекта
- `~/.config/opencode/skills/` — глобальные скиллы OpenCode
- `~/.agents/skills/` — глобальные мультиагентные скиллы

## Выходные файлы

| Файл | Назначение |
|------|-----------|
| `.orchestrator/skills-index.md` | Человекочитаемая таблица: скилл → описание → рекомендуемые агенты |
| `.orchestrator/skills-index.json` | Машиночитаемый индекс для conductor при runtime |

## Запуск

Выполнить Python-скрипт:

```bash
python3 ~/.config/opencode/skills/skills-indexer/scripts/generate_skills_index.py
```

Если скрипт отсутствует — сообщить пользователю и предложить создать его вручную
на основе шаблона из `skills-indexer.md` агента.

Не пытаться парсить скиллы вручную через shell-команды. Использовать скрипт.

## Формат результата

Вернуть в разговоре краткий отчёт:

```
# Skills Index Report

- Project-local skills: N
- Global OpenCode skills: N
- Global multi-agent skills: N
- Mapped to agents: N
- Unmapped: N

Индексы записаны в:
- .orchestrator/skills-index.md
- .orchestrator/skills-index.json
```

## Структура skills-index.json

```json
{
  "generated_at": "ISO-8601",
  "skills": [
    {
      "name": "skill-name",
      "description": "...",
      "location": "path/to/SKILL.md",
      "scope": "project|global",
      "suggested_agents": ["agent-name"],
      "tags": ["tag1", "tag2"]
    }
  ]
}
```
