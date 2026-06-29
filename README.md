# Agentic Orchestrator (Агентный Оркестратор для OpenCode)

Реализация универсальной мультиагентной системы оркестрации на базе исследовательских практик **Anthropic 2025/2026**. Оркестратор декомпозирует сложные высокоуровневые задачи на специализированные пайплайны и распределяет их между субагентами.

---

## Основные принципы архитектуры

Система построена на принципах экономии токенов, адаптивной сложности и точечной загрузки контекста:

1. **Lead Agent для простых задач** — вместо прогона тяжёлых мультиагентных цепочек для локальных правок (исправить баг в 1 файле, добавить 1 тест), оркестратор переходит в режим «Lead Agent» и делегирует задачу напрямую исполнителю (`implementer-builder` или `debug`), минуя фазы планирования и ревью.

2. **Weak-model-aware диспетчеризация** — оркестратор работает на pro-модели, а субагенты — на более слабой. Оркестратор пишет промпты с запасом: over-explain, numbered checklists, явные форматы выдачи, extract-only-relevant-context. Подробный dispatch-шаблон — в `skills/agentic-orchestrator/references/dispatch-template.md`.

3. **Делегированная верификация** — оркестратор **не читает файлы сам** (нет `read`/`grep` доступа). Вся проверка результатов делегируется `reviewer-critic` (для стандартных задач) или `reviewer-critic-pro` (для высокорисковых: auth, payments, security). Это соблюдает Single Responsibility и гарантирует, что проверку делает специализированный агент.

4. **Just-in-Time контекст через `AGENTS.md`** — субагенты не загружают весь проект сразу. При старте они ищут `AGENTS.md` (или считывают глобальный `~/.config/opencode/AGENTS.md`) для получения команд сборки, линтера, тестов и правил кодинга.

5. **Inline Pipeline Registry** — таблица пайплайнов встроена прямо в промпт оркестратора. Не нужен лишний `skill()` roundtrip для выбора пайплайна.

6. **Explicit artifact tracking** — каждый выходной файл сохраняется в `.opencode/context/<name>.md`. Финальный отчёт оркестратора содержит пути ко всем артефактам.

7. **No forced-finding quotas** — скиллы ревью/аудита не требуют «найти минимум N проблем». Если проблем нет — агент явно пишет «не выявлено».

---

## Установка на устройство

Есть два способа: **глобальная установка** (рекомендуется для регулярного
использования) и **локальная через `.opencode/`** (удобно для тестирования и
разработки самого оркестратора).

### Способ 1. Глобальная установка

#### 1.1. Скопируйте агентов
Поместите все файлы из папки `agents/` в глобальную директорию конфигурации OpenCode:
- **Windows**: `C:\Users\<Пользователь>\.config\opencode\agents\`
- **macOS / Linux**: `~/.config/opencode/agents/`

#### 1.2. Скопируйте скиллы
Поместите все папки из `skills/` в глобальную директорию скиллов OpenCode:
- **Windows**: `C:\Users\<Пользователь>\.config\opencode\skills\`
- **macOS / Linux**: `~/.config/opencode/skills/`

Перенесите папки:
- `agentic-orchestrator` — основной скилл оркестратора + `references/dispatch-template.md`
- `plan-creator`, `plan-refiner`, `plan-reviewer`, `plan-intent-validator` — инструменты планирования
- `peer-reviewer`, `commit-reviewer`, `deep-auditor`, `multi-agent-scanner` — рецензирование и аудит
- `code-verifier` — валидатор безопасности и соответствия плану
- `doc-audit`, `doc-pruner`, `doc-scaffold`, `doc-transfer`, `doc-update` — документация
- `skills-indexer` — индексатор скиллов
- `architecture-update` — обновление архитектурных C4/Mermaid схем
- `project-code-auditor` — 5-проходной аудит кодовой базы
- `module-security-scanner` — изолированный аудит безопасности модуля
- `security-prompt-crafter` — генератор policy-safe промптов для white-box review
- `white-box-review-runner` — white-box code review через policy-safe framing

#### 1.3. Настройте `opencode.json`

Добавьте в глобальный `~/.config/opencode/opencode.json`:

```json
{
  "model": "opencode-go/mimo-v2.5",
  "agent": {
    "orchestrator-conductor": {
      "model": "opencode-go/mimo-v2.5-pro",
      "thinking": { "type": "enabled", "reasoningEffort": "high" }
    },
    "architect-planner-pro": {
      "model": "opencode-go/mimo-v2.5-pro",
      "thinking": { "type": "enabled", "reasoningEffort": "high" }
    },
    "reviewer-critic-pro": {
      "model": "opencode-go/mimo-v2.5-pro",
      "thinking": { "type": "enabled", "reasoningEffort": "high" }
    }
  }
}
```

`orchestrator-conductor`, `architect-planner-pro` и `reviewer-critic-pro` работают на pro-модели. Остальные
агенты наследуют глобальную `mimo-v2.5`.

### Способ 2. Локальная установка через `.opencode/`

В репозитории уже есть папка `.opencode/` с полной копией агентов, скиллов и
локальным `opencode.json`. Если открыть этот репозиторий как рабочую директорию
в OpenCode, оркестратор подхватится без глобальной установки.

Структура:

```
.opencode/
├── agents/        # копия agents/
├── skills/        # копия skills/
└── opencode.json  # локальные настройки моделей
```

Файл `.opencode/opencode.json` уже настроен:
- `orchestrator-conductor` → `mimo-v2.5-pro`
- `architect-planner-pro` → `mimo-v2.5-pro`
- `reviewer-critic-pro` → `mimo-v2.5-pro`
- остальные агенты → глобальная `mimo-v2.5`

#### 2.1. Создайте `AGENTS.md` в корне проекта

Субагенты автоматически найдут этот файл и применят настройки. Формат — на ваше усмотрение (команды сборки, правила кодинга, workflow).

---

## Роли субагентов

| Агент | Роль | Доступ |
|-------|------|--------|
| `orchestrator-conductor` | Ведущий оркестратор. Планирует, делегирует, синтезирует отчёт (не проверяет сам — делегирует reviewer'ам). | `task` (селективный), `skill` (селективный) — без `read`/`grep` |
| `researcher-explorer` | Исследователь. Анализирует код, структуру, ищет взаимосвязи. | Read, Grep, Glob, Skill, LSP, Webfetch |
| `architect-planner` | Проектировщик. Создаёт технические спецификации и планы для простых задач. | Read, Write, Grep, Skill, LSP |
| `architect-planner-pro` | Старший проектировщик. Сложные, кросс-доменные или high-stakes планы (auth, payments, новые модули). | Read, Write, Grep, Skill, LSP |
| `implementer-builder` | Разработчик. Пишет код, тесты, документацию по спецификации. | Read, Write, Edit, Grep, Skill, Bash, Webfetch |
| `reviewer-critic` | Рецензент. Quality gate — проверяет планы и код (стандартные задачи). | Read, Grep, Skill, LSP |
| `reviewer-critic-pro` | Старший рецензент. Глубокое ревью для high-stakes (auth, payments, security). | Read, Grep, Skill, LSP |
| `integrator-qa` | Тестировщик. Запускает тесты, проверяет соответствие ТЗ. | Read, Grep, Skill, Bash |
| `debug` | Отладчик. Поиск и устранение корневых причин багов. | Read, Write, Edit, Bash, Webfetch |
| `doc-maintainer` | Документатор. Держит проектную базу знаний в актуальном состоянии. | Read, Write, Edit, Glob, Grep, Bash |
| `content-writer` | Копирайтер. Пишет статьи, документацию, маркетинговые тексты. | Read, Write, Edit, Grep, Skill, Bash (ask), Webfetch |
| `data-analyst` | Аналитик. Обрабатывает данные, строит отчёты, визуализирует. | Read, Write, Edit, Grep, Skill, Bash (селективный), Webfetch |
| `ux-designer` | UX-дизайнер. Пользовательские сценарии, wireframes, интерфейсы. | Read, Write, Edit, Grep, Skill, Webfetch |
| `code-reviewer` | Код-ревьюер. Структурированный 5-мерный анализ кода. | `*` (все разрешения) |
| `test-engineer` | Тест-инженер. Генерация тестов, coverage-анализ. | `*` (все разрешения) |
| `security-auditor` | Аудитор безопасности. Поиск уязвимостей, OWASP-методология. | `*` (все разрешения) |
| `skills-indexer` | Индексатор скиллов. Сканирует и мапит скиллы на агентов. | Read, Write, Edit, Glob, Grep, Bash |

---

## Пайплайны работы

Выбор пайплайна — автоматический, на основе сложности задачи. `architect-planner*`
означает: для простых задач используется `architect-planner`, для сложных или
high-stakes — `architect-planner-pro`.

| Сложность | Пайплайн | Цепочка агентов |
|-----------|----------|-----------------|
| Тривиально (1 файл) | **direct** | `implementer-builder` или `debug` |
| Просто (2-3 файла) | **build** | researcher → architect-planner* → implementer → integrator-qa |
| Стандартно (фича) | **build-review** | researcher → architect-planner* → reviewer-critic* → implementer → reviewer-critic* → integrator-qa |
| Критично (auth, payments) | **full-cycle** | researcher → architect-planner-pro → reviewer-critic-pro → implementer → reviewer-critic-pro → integrator-qa → doc-maintainer |
| Баг (неизвестная причина) | **debug-fix** | researcher → architect-planner* → debug → implementer → integrator-qa |
| Аудит | **parallel-audit** | reviewer ∥ security-auditor → synthesize |
| Глубокое исследование | **parallel-research** | researcher₁ ∥ researcher₂ ∥ ... → synthesize |
| Многомерное ревью | **parallel-review** | reviewer ∥ security-auditor ∥ code-reviewer → synthesize |
| Независимые модули | **parallel-build** | researcher → architect-planner* → implementer₁ ∥ implementer₂ → integrator-qa |
| Исследование | **research** | researcher-explorer |
| Планирование | **plan** | researcher → architect-planner* |
| Контент | **content** | researcher → content-writer → reviewer-critic* |
| Данные | **data** | researcher → data-analyst → reviewer-critic* → integrator-qa |
| Дизайн | **design** | researcher → ux-designer → reviewer-critic* → implementer |

Для любого пайплайна можно добавить `→ doc-maintainer` в конце для автообновления проектной документации.

---

## Структура директории

```
agentic-orchestrator-v1-better/
├── README.md                          # этот файл
├── agents/                            # определения агентов (.md)
│   ├── orchestrator-conductor.md      # оркестратор (primary)
│   ├── researcher-explorer.md         # исследователь
│   ├── architect-planner.md           # проектировщик (простые задачи)
│   ├── architect-planner-pro.md       # старший проектировщик (сложные/high-stakes задачи)
│   ├── implementer-builder.md         # разработчик
│   ├── reviewer-critic.md             # рецензент (стандартные задачи)
│   ├── reviewer-critic-pro.md         # старший рецензент (high-stakes, deepseek-pro)
│   ├── integrator-qa.md               # тестировщик
│   ├── debug.md                       # отладчик (переписан — без дублей)
│   ├── doc-maintainer.md              # документатор
│   ├── content-writer.md              # копирайтер
│   ├── data-analyst.md                # аналитик
│   ├── ux-designer.md                 # UX-дизайнер
│   ├── code-reviewer.md               # код-ревьюер
│   ├── test-engineer.md               # тест-инженер
│   ├── security-auditor.md            # аудитор безопасности
│   └── skills-indexer.md              # индексатор скиллов
└── skills/                            # определения скиллов
    ├── agentic-orchestrator/          # основной скилл оркестратора
    │   ├── SKILL.md
    │   └── references/
    │       ├── dispatch-template.md   # индекс шаблонов
    │       ├── dispatch-simple.md     # шаблон обычного task() вызова
    │       ├── dispatch-pro-planner.md # шаблон для architect-planner-pro
    │       └── dispatch-parallel.md   # шаблон параллельных вызовов
    ├── plan-creator/                  # создание плана
    ├── plan-refiner/                  # доработка плана (переписан)
    ├── plan-reviewer/                 # ревью плана (5 проходов)
    ├── plan-intent-validator/         # валидация соответствия задаче
    ├── peer-reviewer/                 # контрастный анализ
    ├── commit-reviewer/               # ревью git diff / коммита
    ├── deep-auditor/                  # глубинный аудит архитектуры
    ├── multi-agent-scanner/           # мультиагентный аудит
    ├── code-verifier/                 # сверка кода с планом
    ├── doc-audit/                     # аудит документации
    ├── doc-pruner/                    # поиск избыточной документации
    ├── doc-scaffold/                  # создание каркаса документации
    ├── doc-transfer/                  # перенос документационного фреймворка
    ├── doc-update/                    # обновление документации
    ├── skills-indexer/                # индексатор скиллов (создан SKILL.md)
    ├── architecture-update/           # обновление architecture.md
    ├── architecture-security-reviewer/ # Threat Modeling + STRIDE
    ├── project-code-auditor/          # 5-проходной аудит кода
    ├── module-security-scanner/       # аудит безопасности модуля
    ├── security-prompt-crafter/       # генератор policy-safe промптов
    └── white-box-review-runner/       # white-box code review
```

---

## Отличия от базовой версии

| Аспект | Было | Стало |
|--------|------|-------|
| Pipeline selection | `skill()` roundtrip | inline-таблица в промпте |
| Skills Discovery | ~30% промпта | 3 строки |
| Правила оркестратора | 12 (с дублями) | 10 (чисто) |
| Dispatch template | вшит в промпт | `references/dispatch-template.md` |
| Weak model mindset | отсутствовал | отдельный раздел + гайд |
| QA stop criteria | «max 3 iterations» | пороги: cosmetic → stop, functional → 3, critical → 4+ alert |
| Task granularity | не было | когда 1 агент vs несколько |
| Fine-grained decomposition | дефолт — fewer dispatches | дефолт — split more, merge only for trivial tasks |
| Artifact tracking | не было | обязательные пути в финальном отчёте |
| Save locations | отсутствовали у ~18 файлов | добавлены везде |
| Forced-finding quotas | «найти минимум N» в 7 скиллах | заменены на «если есть — перечисли, если нет — напиши» |
| Hardcoded paths | 3 Windows-пути | исправлены на portable |
| `plan-refiner` | 19 строк, без структуры | ~60 строк, с 4-секционной схемой и примером |
| `debug` | 301 строка, дубли секций | ~130 строк, линейный workflow |
| `skills-indexer` | отсутствовал SKILL.md | создан |
| Верификация | оркестратор spot-check'ил сам через `read`/`grep` | оркестратор не имеет `read`/`grep` — вся проверка делегируется `reviewer-critic`/`reviewer-critic-pro` |

| reviewer-critic-pro | отсутствовал | новый pro-агент для high-stakes ревью (deepseek-pro) |
| `tools:` format | deprecated `tools:` секция (true/false) | миграция на `permission:` (allow/deny) во всех 16 агентах |
| LSP | ни один агент не имел LSP | `lsp: allow` добавлен researcher, architect, reviewer |

---

## Модели

- **Оркестратор**: `opencode-go/mimo-v2.5-pro` — pro-модель для сложной координации
- **architect-planner-pro**, **reviewer-critic-pro**: `opencode-go/mimo-v2.5-pro` — pro-модель для сложных/high-stakes задач
- **Все остальные агенты**: `opencode-go/mimo-v2.5` — базовая модель

Оркестратор осведомлён о разнице в моделях и пишет промпты для субагентов с учётом этого.
