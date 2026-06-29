# Масштабируемый оркестратор на OpenCode: полный анализ и план

> Полный технический анализ и蓝图 для построения масштабируемого мультисессионного оркестратора на существующей инфраструктуре OpenCode. OpenHands для этого кейса не нужен.

---

## Содержание

1. [Почему OpenCode, а не OpenHands](#1-почему-opencode-а-не-openhands)
2. [Когда OpenHands всё-таки лучше](#2-когда-openhands-всё-таки-лучше)
3. [Архитектура оркестратора на OpenCode](#3-архитектура-оркестратора-на-opencode)
4. [Шаг 1: Конфигурация агентов](#4-шаг-1-конфигурация-агентов)
5. [Шаг 2: Определения агентов (.md файлы)](#5-шаг-2-определения-агентов-md-файлы)
6. [Шаг 3: Plugin — orchestrator-monitor](#6-шаг-3-plugin--orchestrator-monitor)
7. [Шаг 4: Orchestrator Script (Node.js + SDK)](#7-шаг-4-orchestrator-script-nodejs--sdk)
8. [Шаг 5: Skills](#8-шаг-5-skills)
9. [Шаг 6: Запуск](#9-шаг-6-запуск)
10. [Путь миграции от v1](#10-путь-миграции-от-v1)
11. [Финальная сводка](#11-финальная-сводка)

---

## 1. Почему OpenCode, а не OpenHands

OpenCode уже обладает всей необходимой инфраструктурой для построения масштабируемого оркестратора. Интегрированная система агентов, мультисессионность, плагины, SKILL.md, MCP-серверы, ACP-поддержка — всё это работает из коробки. OpenHands — мощная платформа, но для нашего кейса (кастомный оркестратор с тонкой настройкой поведения агентов) она избыточна.

### Сравнение возможностей

| Возможность | OpenCode | OpenHands |
|---|---|---|
| HTTP API для управления сессиями | ✅ Полная поддержка | ✅ Полная поддержка |
| JS/TS SDK | ✅ @opencode-ai/sdk | ❌ Python only |
| Мультисессионность | ✅ Несколько сессий параллельно | ✅ Несколько сессий параллельно |
| Система агентов (primary/subagent/task permissions) | ✅ Полная конфигурация | ⚠️ Базовые агенты, без task-level permissions |
| ACP поддержка | ✅ Claude Code, Codex, Gemini | ⚠️ Ограниченная |
| Кастомные инструменты | ✅ MCP + кастомные плагины | ⚠️ Только MCP |
| Плагины / event hooks | ✅ Полный lifecycle events | ⚠️ Ограниченные hooks |
| Skills (SKILL.md) | ✅ Полная поддержка | ❌ Нет |
| MCP серверы | ✅ Полная интеграция | ✅ Полная интеграция |
| LSP интеграция | ✅ Из коробки | ❌ Нет |
| Docker sandbox | ⚠️ Через MCP/плагины | ✅ Нативная изоляция |
| Web UI (Agent Canvas) | ⚠️ TUI + API | ✅ Полноценный UI |
| Automation (cron, webhooks) | ⚠️ Через SDK (нужен свой скрипт) | ✅ Встроенные scheduled tasks |
| Совместимость с существующим оркестратором v1 | ✅ Полная | ❌ Полная переработка |

**Вывод:** OpenCode покрывает 13 из 14 пунктов. Там, где OpenHands лучше (Docker sandbox, Web UI, automation), — это enterprise/team-фичи, которые не критичны для кастомного оркестратора на базе SDK.

---

## 2. Когда OpenHands всё-таки лучше

OpenHands — это не конкурент OpenCode, а комплементарная платформа для других сценариев.

### Командная работа: Agent Canvas как shared UI

Agent Canvas в OpenHands — это полноценный веб-интерфейс, где вся команда может видеть сессии агентов в реальном времени. Каждый разработчик видит прогресс, может подключиться к сессии, оставить комментарий, скорректировать направление. В OpenCode такого shared UI нет — только TUI на каждой машине.

### Docker sandbox: изоляция агентов

Критично для:
- **CI/CD пайплайнов** — агенты запускают код в изолированных контейнерах, не влияя на хост-систему
- **Untrusted code** — когда агент тестирует код из внешних PR или сторонних репозиториев
- **Мульти-теннантных сценариев** — несколько клиентов/проектов работают на одном сервере

### Automation Server: cron, webhooks

OpenHands позволяет запускать агентов по расписанию или на события:
- GitHub webhook → агент автоматически ревьюит PR
- Slack message → агент создаёт задачу и начинает работу
- Cron → ежедневный аудит кодовой базы
- Linear/GitHub Issues → агент парсит и начинает реализацию

### Always-on сервер

Агенты работают 24/7 на сервере в облаке. Даже когда ноутбук выключен — пайплайны продолжают выполняться, алерты обрабатываются, код ревьюится.

### Enterprise

- **SSO** — интеграция с корпоративной системой аутентификации
- **Audit logs** — кто, когда и что делал через агентов
- **Multi-user management** — роли, права, лимиты
- **Compliance** — SOC2, GDPR — требования, которые критичны для enterprise

### Готовый marketplace экосистемы

Готовые automation templates, интеграции с Slack/GitHub/Linear из коробки. Не нужно писать кастомные плагины — берёшь шаблон и настраиваешь.

### Если не нужен кастомный оркестратор

OpenHands + ACP агенты (Claude Code, Codex, Gemini) работают из коробки без написания кода. Просто подключаешь агентов и используешь встроенные пайплайны.

### Итог

| Сценарий | Лучший выбор |
|---|---|
| Enterprise / команда / always-on | **OpenHands** |
| Кастомный оркестратор / power-user / тонкая настройка | **OpenCode** |

---

## 3. Архитектура оркестратора на OpenCode

### Общая схема

```
┌─────────────────────────────────────────────────────┐
│  Orchestrator Script (Node.js)                      │
│  @opencode-ai/sdk                                   │
│                                                     │
│  • Создание сессий по задачам                       │
│  • Распределение между сессиями                     │
│  • Мониторинг через SSE                             │
│  • Форк сессий для параллельных подзадач            │
│  • Агрегация результатов                            │
└──────────────────────┬──────────────────────────────┘
                       │ HTTP (localhost:4096)
                       │ SSE events stream
┌──────────────────────▼──────────────────────────────┐
│  opencode serve --port 4096                         │
│                                                     │
│  ┌───────────┐  ┌───────────┐  ┌───────────┐       │
│  │ Session 1 │  │ Session 2 │  │ Session 3 │       │
│  │ (build)   │  │ (plan)    │  │ (review)  │       │
│  └───────────┘  └───────────┘  └───────────┘       │
│                                                     │
│  Агенты: orchestrator → subagents                   │
│  Skills: agentic-orchestrator, plan-creator...      │
│  Plugin: orchestrator-monitor                       │
│  MCP: filesystem, search, tools                     │
└─────────────────────────────────────────────────────┘
```

### Слой 1: Orchestrator Script (Node.js)

Внешний скрипт, работающий через `@opencode-ai/sdk`. Управляет жизненным циклом сессий: создаёт, отправляет промпты, слушает события, агрегирует результаты. Не зависит от TUI — работает headless.

### Слой 2: OpenCode Server

`opencode serve` — HTTP-сервер с SSE для событий. Принимает команды от SDK, управляет сессиями, маршрутизирует запросы к агентам.

### Слой 3: Сессии и агенты

Каждая сессия — изолированный контекст с конкретным агентом. Агенты определены в `.md` файлах с YAML-фронтматтером. Subagents получают только те инструменты, которые разрешены через `permission.task`.

### Слой 4: Инструменты

- **MCP серверы** — внешние сервисы (filesystem, search, APIs)
- **Skills** — поведенческие инструкции для агентов
- **Плагины** — lifecycle hooks для мониторинга и логирования
- **Кастомные инструменты** — специфичные для проекта

### Поток данных

```
Пользователь → Orchestrator Script → SDK call → OpenCode Server
                                                       │
                                                       ▼
                                              Session + Agent execution
                                                       │
                                                       ▼
                                              SSE events → Script
                                                       │
                                                       ▼
                                              Результат → Следующий шаг
```

---

## 4. Шаг 1: Конфигурация агентов

Полная конфигурация `opencode.json` с оркестратором и subagent'ами.

```json
{
  "$schema": "https://opencode.ai/schema.json",
  "agent": {
    "orchestrator-conductor": {
      "description": "Primary orchestrator agent that decomposes tasks, selects pipelines, manages subagents, and ensures quality through spot-checks",
      "mode": "primary",
      "model": "opencode-go/deepseek-v4-pro",
      "temperature": 0.3,
      "reasoningEffort": "max",
      "tools": {
        "bash": "deny",
        "write": "deny",
        "edit": "deny",
        "read": "allow",
        "glob": "allow",
        "grep": "allow",
        "webfetch": "allow",
        "skill": "allow",
        "question": "allow"
      },
      "permission": {
        "task": {
          "*": "deny",
          "research": "allow",
          "plan": "allow",
          "review": "allow",
          "audit": "allow",
          "refactor": "allow",
          "test": "allow",
          "doc": "allow",
          "deploy": "allow"
        }
      }
    },
    "researcher-explorer": {
      "description": "Read-only research agent. Explores codebase, reads files, searches patterns. Never writes or edits.",
      "mode": "subagent",
      "model": "opencode-go/deepseek-v4-flash",
      "temperature": 0.1,
      "reasoningEffort": "max",
      "tools": {
        "bash": "deny",
        "write": "deny",
        "edit": "deny",
        "read": "allow",
        "glob": "allow",
        "grep": "allow",
        "webfetch": "allow",
        "skill": "deny",
        "question": "deny"
      },
      "permission": {
        "task": {
          "*": "deny",
          "research": "allow"
        }
      }
    },
    "architect-planner": {
      "description": "Planning agent. Reads codebase, creates implementation plans, defines architecture decisions.",
      "mode": "subagent",
      "model": "opencode-go/deepseek-v4-flash",
      "temperature": 0.2,
      "reasoningEffort": "max",
      "tools": {
        "bash": "deny",
        "write": "deny",
        "edit": "deny",
        "read": "allow",
        "glob": "allow",
        "grep": "allow",
        "webfetch": "allow",
        "skill": "allow",
        "question": "deny"
      },
      "permission": {
        "task": {
          "*": "deny",
          "plan": "allow",
          "research": "allow"
        }
      }
    },
    "implementer-builder": {
      "description": "Implementation agent. Writes code, creates files, runs commands. Full write access.",
      "mode": "subagent",
      "model": "opencode-go/deepseek-v4-flash",
      "temperature": 0.1,
      "reasoningEffort": "max",
      "tools": {
        "bash": "allow",
        "write": "allow",
        "edit": "allow",
        "read": "allow",
        "glob": "allow",
        "grep": "allow",
        "webfetch": "allow",
        "skill": "deny",
        "question": "deny"
      },
      "permission": {
        "task": {
          "*": "deny",
          "build": "allow",
          "implement": "allow",
          "refactor": "allow"
        }
      }
    },
    "reviewer-critic": {
      "description": "Review agent. Reads code, finds bugs, suggests improvements. Read-only with detailed feedback.",
      "mode": "subagent",
      "model": "opencode-go/deepseek-v4-flash",
      "temperature": 0.2,
      "reasoningEffort": "max",
      "tools": {
        "bash": "deny",
        "write": "deny",
        "edit": "deny",
        "read": "allow",
        "glob": "allow",
        "grep": "allow",
        "webfetch": "deny",
        "skill": "deny",
        "question": "deny"
      },
      "permission": {
        "task": {
          "*": "deny",
          "review": "allow"
        }
      }
    },
    "integrator-qa": {
      "description": "QA agent. Runs tests, validates builds, checks integration points.",
      "mode": "subagent",
      "model": "opencode-go/deepseek-v4-flash",
      "temperature": 0.1,
      "reasoningEffort": "max",
      "tools": {
        "bash": "allow",
        "write": "deny",
        "edit": "deny",
        "read": "allow",
        "glob": "allow",
        "grep": "allow",
        "webfetch": "deny",
        "skill": "deny",
        "question": "deny"
      },
      "permission": {
        "task": {
          "*": "deny",
          "test": "allow",
          "audit": "allow"
        }
      }
    },
    "debug-troubleshooter": {
      "description": "Debug agent. Investigates errors, reads logs, traces issues through the codebase.",
      "mode": "subagent",
      "model": "opencode-go/deepseek-v4-flash",
      "temperature": 0.2,
      "reasoningEffort": "max",
      "tools": {
        "bash": "allow",
        "write": "deny",
        "edit": "deny",
        "read": "allow",
        "glob": "allow",
        "grep": "allow",
        "webfetch": "deny",
        "skill": "deny",
        "question": "deny"
      },
      "permission": {
        "task": {
          "*": "deny",
          "debug": "allow",
          "research": "allow"
        }
      }
    },
    "doc-maintainer": {
      "description": "Documentation agent. Reads code, generates and updates documentation files.",
      "mode": "subagent",
      "model": "opencode-go/deepseek-v4-flash",
      "temperature": 0.3,
      "reasoningEffort": "max",
      "tools": {
        "bash": "deny",
        "write": "allow",
        "edit": "allow",
        "read": "allow",
        "glob": "allow",
        "grep": "allow",
        "webfetch": "deny",
        "skill": "allow",
        "question": "deny"
      },
      "permission": {
        "task": {
          "*": "deny",
          "doc": "allow",
          "research": "allow"
        }
      }
    }
  },
  "mcp": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "."]
    },
    "search": {
      "command": "npx",
      "args": ["-y", "@anthropic-ai/mcp-search"]
    }
  },
  "plugin": {
    "orchestrator-monitor": {
      "path": ".opencode/plugins/orchestrator-monitor.ts"
    }
  }
}
```

### Ключевые решения конфигурации

**Модели:** Orchestrator использует `opencode-go/deepseek-v4-pro` для принятия стратегических решений. Subagents используют `opencode-go/deepseek-v4-flash`. У обоих `reasoningEffort: "max"` для максимального качества рассуждений.

**Task permissions:** Механизм `permission.task` позволяет точно контролировать, какие типы задач может выполнять каждый агент. Паттерн `"*": "deny"` блокирует всё по умолчанию, затем конкретные allow-паттерны разрешают нужное.

**Инструменты:** Каждый агент получает только необходимые инструменты. Researcher — только read/glob/grep. Implementer — bash/write/edit/read. Reviewer — только read/glob/grep.

---

## 5. Шаг 2: Определения агентов (.md файлы)

### agents/orchestrator-conductor.md

```markdown
---
description: Primary orchestrator agent that decomposes tasks, selects pipelines, manages subagents, and ensures quality through spot-checks
mode: primary
model: opencode-go/deepseek-v4-pro
reasoningEffort: max
temperature: 0.3
tools:
  - read
  - glob
  - grep
  - webfetch
  - skill
  - question
permission:
  task:
    - research
    - plan
    - review
    - audit
    - refactor
    - test
    - doc
    - deploy
---

# Orchestrator-Conductor

Ты — primary оркестратор. Твоя задача — декомпозировать входную задачу, выбрать пайплайн, распределить работу между subagent'ами и проверить качество результата.

## Принципы работы

1. **Анализ перед действием.** Прочитай структуру проекта, пойми контекст, прежде чем что-то делать.
2. **Минимальные промпты.** Каждый subagent должен получить чёткую, конкретную инструкцию. Без воды.
3. **Spot-check.** После каждого шага проверяй результат: читай ключевые файлы, запускай тесты, валидируй вывод.
4. **Не импровизируй.** Следуй пайплайну. Если пайплайн не подходит — скажи об этом, не меняй его сам.

## Пайплайны

### sequential: build
research → plan → implement → review → test

### parallel: audit
Запусти 3 reviewer'а параллельно на разных доменах. Агрегируй результаты.

### sequential: refactor
research → plan → implement → review

### direct: simple
Одна сессия, один агент, одна задача.

## Spot-check протокол

После каждого шага:
1. Прочитай 2-3 ключевых файла, которые были изменены
2. Запусти `npm test` или эквивалент
3. Сравни результат с ожиданием
4. Если отклонение — зафиксируй и скорректируй следующий шаг

## Формат результата

```
## Результат оркестрации
- Статус: ✅/⚠️/❌
- Пайплайн: [название]
- Шаги: [список с результатами]
- Spot-check: [найденные проблемы]
- Итог: [краткое резюме]
```
```

### agents/researcher-explorer.md

```markdown
---
description: Read-only research agent. Explores codebase, reads files, searches patterns. Never writes or edits.
mode: subagent
model: opencode-go/deepseek-v4-flash
reasoningEffort: max
temperature: 0.1
tools:
  - read
  - glob
  - grep
  - webfetch
permission:
  task:
    - research
---

# Researcher-Explorer

Ты — read-only research-агент. Твоя задача — изучить кодовую базу, найти релевантные файлы, проанализировать паттерны и вернуть структурированный отчёт.

## Правила

1. **Только чтение.** Никаких записей, редактирований, запуска команд.
2. **Структурированный вывод.** Всегда возвращай результат в формате:
   ```
   ## Исследование: [тема]
   ### Найденные файлы
   - path/to/file.ts — описание
   ### Паттерны
   - [паттерн] — где используется
   ### Выводы
   - [вывод 1]
   - [вывод 2]
   ### Рекомендации
   - [рекомендация]
   ```
3. **Глубина.** Не ограничивайся surface-level. Читай содержимое файлов, а не только имена.
4. **Источники.** Указывай конкретные пути файлов и номера строк.
```

### agents/implementer-builder.md

```markdown
---
description: Implementation agent. Writes code, creates files, runs commands. Full write access.
mode: subagent
model: opencode-go/deepseek-v4-flash
reasoningEffort: max
temperature: 0.1
tools:
  - bash
  - write
  - edit
  - read
  - glob
  - grep
permission:
  task:
    - build
    - implement
    - refactor
---

# Implementer-Builder

Ты — implementation-агент. Твоя задача — реализовать код согласно плану, написанный тебе оркестратором.

## Правила

1. **Следуй плану точно.** Не отклоняйся от спецификации. Если план некорректен — верни ошибку, не исправляй сам.
2. **Минимальный дифф.** Меняй только то, что требуется по задаче. Не рефактори unrelated код.
3. **Тестируй после.** Запускай `npm test` (или эквивалент) после каждого изменения.
4. **Чистый код.** Без комментариев к коду (комментарии — только для why). Без over-engineering.
5. **Откат.** Если что-то пошло не так — откати изменения через `git checkout` и сообщи о проблеме.

## Формат результата

```
## Результат реализации
- Файлы созданы/изменены:
  - path/to/file.ts — описание изменений
- Тесты: ✅/❌ [результат]
- Проблемы: [список или "нет"]
```
```

---

## 6. Шаг 3: Plugin — orchestrator-monitor

Полный плагин для мониторинга активности оркестратора.

```typescript
// .opencode/plugins/orchestrator-monitor.ts

import type { Plugin } from "@opencode-ai/plugin";

interface SessionMetrics {
  totalCreated: number;
  totalCompleted: number;
  totalFailed: number;
  totalErrored: number;
  activeSessions: number;
  avgDurationMs: number;
  sessions: Map<string, SessionRecord>;
}

interface SessionRecord {
  id: string;
  agent: string;
  task: string;
  createdAt: number;
  completedAt?: number;
  failedAt?: number;
  erroredAt?: number;
  error?: string;
  durationMs?: number;
}

function formatTimestamp(date: Date): string {
  return date.toISOString().replace("T", " ").replace(/\.\d{3}Z$/, "");
}

function formatDuration(ms: number): string {
  if (ms < 1000) return `${ms}ms`;
  if (ms < 60000) return `${(ms / 1000).toFixed(1)}s`;
  const minutes = Math.floor(ms / 60000);
  const seconds = Math.floor((ms % 60000) / 1000);
  return `${minutes}m ${seconds}s`;
}

const metrics: SessionMetrics = {
  totalCreated: 0,
  totalCompleted: 0,
  totalFailed: 0,
  totalErrored: 0,
  activeSessions: 0,
  avgDurationMs: 0,
  sessions: new Map(),
};

function log(level: "INFO" | "WARN" | "ERROR" | "DEBUG", message: string): void {
  const timestamp = formatTimestamp(new Date());
  const prefix = `[orchestrator-monitor][${timestamp}][${level}]`;
  console.log(`${prefix} ${message}`);
}

function updateAvgDuration(): void {
  const completed = Array.from(metrics.sessions.values()).filter(
    (s) => s.durationMs !== undefined
  );
  if (completed.length === 0) {
    metrics.avgDurationMs = 0;
    return;
  }
  const total = completed.reduce((sum, s) => sum + (s.durationMs ?? 0), 0);
  metrics.avgDurationMs = Math.round(total / completed.length);
}

function getMetricsSummary(): string {
  return JSON.stringify(
    {
      totalCreated: metrics.totalCreated,
      totalCompleted: metrics.totalCompleted,
      totalFailed: metrics.totalFailed,
      totalErrored: metrics.totalErrored,
      activeSessions: metrics.activeSessions,
      avgDurationMs: metrics.avgDurationMs,
      avgDurationFormatted: formatDuration(metrics.avgDurationMs),
    },
    null,
    2
  );
}

const orchestratorMonitorPlugin: Plugin = {
  name: "orchestrator-monitor",
  version: "1.0.0",

  onMount(api) {
    log("INFO", "Orchestrator Monitor plugin initialized");
    log("INFO", `Metrics: ${getMetricsSummary()}`);
  },

  onUnmount() {
    log("INFO", "Orchestrator Monitor plugin unmounted");
    log("INFO", `Final metrics: ${getMetricsSummary()}`);
  },

  event: {
    "session.created"(event) {
      const sessionId = event.properties?.sessionId ?? "unknown";
      const agent = event.properties?.agent ?? "unknown";
      const task = event.properties?.task ?? "no task specified";

      metrics.totalCreated++;
      metrics.activeSessions++;

      const record: SessionRecord = {
        id: sessionId,
        agent,
        task,
        createdAt: Date.now(),
      };
      metrics.sessions.set(sessionId, record);

      log(
        "INFO",
        `Session created: ${sessionId} | agent: ${agent} | active: ${metrics.activeSessions}`
      );
      log("DEBUG", `Task: ${task}`);
    },

    "session.idle"(event) {
      const sessionId = event.properties?.sessionId ?? "unknown";
      const record = metrics.sessions.get(sessionId);

      if (record) {
        record.completedAt = Date.now();
        record.durationMs = record.completedAt - record.createdAt;
        metrics.totalCompleted++;
        metrics.activeSessions = Math.max(0, metrics.activeSessions - 1);
        updateAvgDuration();

        log(
          "INFO",
          `Session completed: ${sessionId} | duration: ${formatDuration(record.durationMs)} | agent: ${record.agent}`
        );
        log(
          "DEBUG",
          `Avg duration: ${formatDuration(metrics.avgDurationMs)} | active: ${metrics.activeSessions}`
        );
      } else {
        log(
          "WARN",
          `Session idle event for unknown session: ${sessionId}`
        );
      }
    },

    "session.error"(event) {
      const sessionId = event.properties?.sessionId ?? "unknown";
      const error = event.properties?.error ?? "unknown error";
      const record = metrics.sessions.get(sessionId);

      if (record) {
        record.erroredAt = Date.now();
        record.error = typeof error === "string" ? error : JSON.stringify(error);
        record.durationMs = record.erroredAt - record.createdAt;
        metrics.totalErrored++;
        metrics.activeSessions = Math.max(0, metrics.activeSessions - 1);
        updateAvgDuration();

        log(
          "ERROR",
          `Session error: ${sessionId} | agent: ${record.agent} | duration: ${formatDuration(record.durationMs)}`
        );
        log("ERROR", `Error details: ${record.error}`);
      } else {
        log("ERROR", `Session error for unknown session: ${sessionId} | error: ${error}`);
      }
    },

    "session.status"(event) {
      const sessionId = event.properties?.sessionId ?? "unknown";
      const status = event.properties?.status ?? "unknown";

      log("DEBUG", `Session status: ${sessionId} → ${status}`);

      if (status === "failed") {
        const record = metrics.sessions.get(sessionId);
        if (record && !record.failedAt) {
          record.failedAt = Date.now();
          record.durationMs = record.failedAt - record.createdAt;
          metrics.totalFailed++;
          metrics.activeSessions = Math.max(0, metrics.activeSessions - 1);
          updateAvgDuration();

          log(
            "WARN",
            `Session failed: ${sessionId} | agent: ${record.agent} | duration: ${formatDuration(record.durationMs)}`
          );
        }
      }
    },
  },
};

export default orchestratorMonitorPlugin;
```

### Что делает плагин

- **session.created** — логирует создание сессии, инкрементирует счётчики
- **session.idle** — логирует завершение, считает длительность, обновляет среднее
- **session.error** — логирует ошибку с деталями, считает как failed
- **session.status** — отслеживает все смены статуса для отладки
- **getMetricsSummary()** — публичная функция для получения текущих метрик

---

## 7. Шаг 4: Orchestrator Script (Node.js + SDK)

Полный скрипт оркестратора на TypeScript + @opencode-ai/sdk.

```typescript
// orchestrator.ts

import { OpencodeClient, type Session, type Message } from "@opencode-ai/sdk";

// ─── Конфигурация ────────────────────────────────────────────────────────────

const OPENCODE_URL = process.env.OPENCODE_URL ?? "http://localhost:4096";
const DEFAULT_TIMEOUT_MS = 5 * 60 * 1000; // 5 минут
const POLL_INTERVAL_MS = 1000; // 1 секунда

const client = new OpencodeClient({ baseUrl: OPENCODE_URL });

// ─── Типы ────────────────────────────────────────────────────────────────────

interface TaskStep {
  task: string;
  agent: string;
  taskType?: string;
}

interface PipelineResult {
  success: boolean;
  steps: StepResult[];
  finalOutput: string;
  totalDurationMs: number;
}

interface StepResult {
  stepIndex: number;
  agent: string;
  task: string;
  sessionId: string;
  output: string;
  durationMs: number;
  success: boolean;
  error?: string;
}

interface ParallelResult {
  success: boolean;
  results: StepResult[];
  totalDurationMs: number;
}

// ─── Утилиты ─────────────────────────────────────────────────────────────────

function log(level: "INFO" | "WARN" | "ERROR", message: string): void {
  const timestamp = new Date().toISOString().replace("T", " ").replace(/\.\d{3}Z$/, "");
  console.log(`[${timestamp}][${level}] ${message}`);
}

function formatDuration(ms: number): string {
  if (ms < 1000) return `${ms}ms`;
  if (ms < 60000) return `${(ms / 1000).toFixed(1)}s`;
  const minutes = Math.floor(ms / 60000);
  const seconds = Math.floor((ms % 60000) / 1000);
  return `${minutes}m ${seconds}s`;
}

async function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

// ─── Основные функции ────────────────────────────────────────────────────────

/**
 * Запуск одной сессии с ожиданием завершения.
 */
async function runSession(
  task: string,
  agent: string,
  timeoutMs: number = DEFAULT_TIMEOUT_MS
): Promise<{ sessionId: string; output: string; durationMs: number }> {
  const startTime = Date.now();

  log("INFO", `Creating session | agent: ${agent}`);
  log("INFO", `Task: ${task.substring(0, 100)}${task.length > 100 ? "..." : ""}`);

  // Создаём сессию
  const session = await client.session.create({
    agent,
  });

  const sessionId = session.id;
  log("INFO", `Session created: ${sessionId}`);

  // Отправляем промпт
  await client.session.prompt({
    sessionId,
    message: task,
  });

  log("INFO", `Prompt sent to session ${sessionId}, waiting for completion...`);

  // Ждём завершения (polling статуса)
  const deadline = Date.now() + timeoutMs;
  let lastStatus = "";

  while (Date.now() < deadline) {
    await sleep(POLL_INTERVAL_MS);

    try {
      const status = await client.session.status({ sessionId });
      const currentStatus = status.status ?? "unknown";

      if (currentStatus !== lastStatus) {
        log("INFO", `Session ${sessionId} status: ${currentStatus}`);
        lastStatus = currentStatus;
      }

      if (currentStatus === "idle" || currentStatus === "completed") {
        // Получаем финальный вывод
        const messages = await client.session.messages({ sessionId });
        const lastMessage = messages[messages.length - 1];
        const output = lastMessage?.content ?? "(no output)";
        const durationMs = Date.now() - startTime;

        log(
          "INFO",
          `Session ${sessionId} completed in ${formatDuration(durationMs)}`
        );

        return { sessionId, output, durationMs };
      }

      if (currentStatus === "failed" || currentStatus === "error") {
        const durationMs = Date.now() - startTime;
        const errorMsg = `Session failed with status: ${currentStatus}`;
        log("ERROR", errorMsg);
        return { sessionId, output: errorMsg, durationMs };
      }
    } catch (err) {
      log("WARN", `Error polling session ${sessionId}: ${err}`);
    }
  }

  // Timeout
  const durationMs = Date.now() - startTime;
  log("ERROR", `Session ${sessionId} timed out after ${formatDuration(durationMs)}`);
  return {
    sessionId,
    output: `Timeout after ${formatDuration(durationMs)}`,
    durationMs,
  };
}

/**
 * Запуск пайплайна: последовательное выполнение шагов с передачей контекста.
 */
async function runSequential(
  steps: TaskStep[],
  timeoutMs: number = DEFAULT_TIMEOUT_MS
): Promise<PipelineResult> {
  const startTime = Date.now();
  const results: StepResult[] = [];
  let contextAccumulator = "";

  log("INFO", `=== Starting sequential pipeline (${steps.length} steps) ===`);

  for (let i = 0; i < steps.length; i++) {
    const step = steps[i];
    const enrichedTask = contextAccumulator
      ? `${step.task}\n\n--- Контекст из предыдущих шагов ---\n${contextAccumulator}`
      : step.task;

    log("INFO", `--- Step ${i + 1}/${steps.length}: ${step.agent} ---`);

    const result = await runSession(enrichedTask, step.agent, timeoutMs);

    const stepResult: StepResult = {
      stepIndex: i,
      agent: step.agent,
      task: step.task,
      sessionId: result.sessionId,
      output: result.output,
      durationMs: result.durationMs,
      success: !result.output.startsWith("Timeout") && !result.output.startsWith("Session failed"),
    };

    results.push(stepResult);

    if (!stepResult.success) {
      log("ERROR", `Step ${i + 1} failed: ${stepResult.error ?? stepResult.output}`);
      return {
        success: false,
        steps: results,
        finalOutput: stepResult.output,
        totalDurationMs: Date.now() - startTime,
      };
    }

    // Накапливаем контекст для следующего шага
    contextAccumulator += `\n\n### Шаг ${i + 1}: ${step.agent}\n${result.output}`;
  }

  const totalDurationMs = Date.now() - startTime;
  log(
    "INFO",
    `=== Pipeline completed in ${formatDuration(totalDurationMs)} (${results.length} steps) ===`
  );

  return {
    success: true,
    steps: results,
    finalOutput: results[results.length - 1].output,
    totalDurationMs,
  };
}

/**
 * Параллельное выполнение нескольких задач.
 */
async function runParallel(
  tasks: TaskStep[],
  timeoutMs: number = DEFAULT_TIMEOUT_MS
): Promise<ParallelResult> {
  const startTime = Date.now();

  log(
    "INFO",
    `=== Starting parallel execution (${tasks.length} tasks) ===`
  );

  const promises = tasks.map(async (task, index) => {
    log("INFO", `--- Parallel task ${index + 1}: ${task.agent} ---`);
    const result = await runSession(task.task, task.agent, timeoutMs);

    return {
      stepIndex: index,
      agent: task.agent,
      task: task.task,
      sessionId: result.sessionId,
      output: result.output,
      durationMs: result.durationMs,
      success: !result.output.startsWith("Timeout") && !result.output.startsWith("Session failed"),
    };
  });

  const results = await Promise.all(promises);
  const totalDurationMs = Date.now() - startTime;
  const allSuccess = results.every((r) => r.success);

  log(
    "INFO",
    `=== Parallel execution completed in ${formatDuration(totalDurationMs)} | success: ${allSuccess} ===`
  );

  return {
    success: allSuccess,
    results,
    totalDurationMs,
  };
}

/**
 * Запуск простой задачи (одна сессия, один агент).
 */
async function runDirect(
  task: string,
  agent: string = "orchestrator-conductor"
): Promise<StepResult> {
  log("INFO", `=== Running direct task ===`);

  const result = await runSession(task, agent);

  return {
    stepIndex: 0,
    agent,
    task,
    sessionId: result.sessionId,
    output: result.output,
    durationMs: result.durationMs,
    success: !result.output.startsWith("Timeout") && !result.output.startsWith("Session failed"),
  };
}

// ─── Демонстрация ────────────────────────────────────────────────────────────

async function main() {
  log("INFO", "╔══════════════════════════════════════════════════╗");
  log("INFO", "║  OpenCode Orchestrator — Demo                   ║");
  log("INFO", "╚══════════════════════════════════════════════════╝");
  log("INFO", `Server: ${OPENCODE_URL}`);

  // ─── Сценарий 1: Простая задача ──────────────────────────────────────────

  log("INFO", "");
  log("INFO", "━━━ Сценарий 1: Простая задача (direct) ━━━");

  const simpleResult = await runDirect(
    "Проанализируй структуру текущего проекта и верни краткое описание: основные директории, технологический стек, точки входа.",
    "researcher-explorer"
  );

  log("INFO", `Результат: ${simpleResult.success ? "✅" : "❌"}`);
  log("INFO", `Вывод:\n${simpleResult.output.substring(0, 500)}`);

  // ─── Сценарий 2: Параллельный аудит ──────────────────────────────────────

  log("INFO", "");
  log("INFO", "━━━ Сценарий 2: Параллельный аудит (3 reviewer'а) ━━━");

  const auditResult = await runParallel([
    {
      task: "Проведи аудит безопасности: проверь SQL-инъекции, XSS, небезопасные зависимости, секреты в коде. Верни список находок с приоритетами.",
      agent: "reviewer-critic",
    },
    {
      task: "Проведи аудит производительности: найди N+1 запросы, неоптимизированные циклы, утечки памяти, лишние рендеры. Верни список находок.",
      agent: "reviewer-critic",
    },
    {
      task: "Проведи аудит архитектуры: проверь SRP, DRY, связность, когезию, ошибки проектирования. Верни список находок.",
      agent: "reviewer-critic",
    },
  ]);

  log("INFO", `Аудит: ${auditResult.success ? "✅" : "⚠️"}`);

  for (const result of auditResult.results) {
    log("INFO", `\n--- Reviewer ${result.stepIndex + 1} (${result.agent}) ---`);
    log("INFO", result.output.substring(0, 300));
  }

  // ─── Сценарий 3: Последовательный build-пайплайн ────────────────────────

  log("INFO", "");
  log("INFO", "━━━ Сценарий 3: Sequential build pipeline ━━━");

  const buildResult = await runSequential([
    {
      task: "Исследуй текущую кодовую базу. Определи: что уже реализовано, какие модули существуют, какой стек используется. Верни структурированный отчёт.",
      agent: "researcher-explorer",
    },
    {
      task: "На основе исследования создай план реализации: разбей на задачи, определи зависимости, оцени сложность. Формат: markdown с чеклистом.",
      agent: "architect-planner",
    },
    {
      task: "Реализуй план: создай/измени файлы, запусти тесты, убедись что всё работает. Следуй плану точно.",
      agent: "implementer-builder",
    },
    {
      task: "Проведи code review реализации: найди баги, проблемы с производительностью, нарушения стиля. Верни список замечаний.",
      agent: "reviewer-critic",
    },
  ]);

  log("INFO", `Pipeline: ${buildResult.success ? "✅" : "❌"}`);
  log("INFO", `Общая длительность: ${formatDuration(buildResult.totalDurationMs)}`);

  for (const step of buildResult.steps) {
    log(
      "INFO",
      `  Step ${step.stepIndex + 1} (${step.agent}): ${step.success ? "✅" : "❌"} | ${formatDuration(step.durationMs)}`
    );
  }

  // ─── Итоги ───────────────────────────────────────────────────────────────

  log("INFO", "");
  log("INFO", "╔══════════════════════════════════════════════════╗");
  log("INFO", "║  Demo complete                                   ║");
  log("INFO", "╚══════════════════════════════════════════════════╝");
}

main().catch((err) => {
  log("ERROR", `Fatal error: ${err}`);
  process.exit(1);
});
```

### Запуск скрипта

```bash
# Установка зависимостей
npm install @opencode-ai/sdk

# Запуск (при работающем opencode serve)
npx tsx orchestrator.ts
```

### Ключевые особенности

- **runSession** — создаёт сессию через SDK, отправляет промпт, poll'ит статус до завершения
- **runSequential** — последовательно выполняет шаги, передавая контекст предыдущих шагов
- **runParallel** — запускает все задачи параллельно через `Promise.all`
- **runDirect** — обёртка для простых задач без пайплайна
- **Timeout** — предотвращает зависание сессий
- **Логирование** — подробный вывод каждого шага с таймстампами

---

## 8. Шаг 5: Skills

### agentic-orchestrator SKILL.md

```markdown
# Agentic Orchestrator Skill

## Описание

Мультиагентный оркестратор для масштабных задач. Декомпозирует сложные задачи на подзадачи, распределяет между specialized subagent'ами, агрегирует результаты через spot-check.

## Триггеры

Загружать когда пользователь говорит:
- "оркестрируй это"
- "запусти команду агентов"
- "используй пайплайн"
- "сделай параллельный аудит"
- "пошаговая реализация"

## Пайплайны

### sequential: build
```
research → plan → implement → review → test
```
Для полного цикла разработки. Каждый шаг передаёт контекст следующему.

### sequential: refactor
```
research → plan → implement → review
```
Для рефакторинга без тестирования (тесты запускаются внутри implement).

### parallel: audit
```
Запуск 3 reviewer'ов параллельно:
- security audit
- performance audit
- architecture audit
→ Агрегация результатов
```
Для комплексного аудита кодовой базы.

### direct: simple
```
Одна сессия, один агент, одна задача
```
Для простых задач, не требующих оркестрации.

## Dispatch Templates

### research
```
Agent: researcher-explorer
Task: "{task_description}"
Context: project root at {project_path}
Output: structured research report
```

### plan
```
Agent: architect-planner
Task: "Create implementation plan for: {task_description}"
Context: {research_output}
Output: step-by-step plan with dependencies
```

### implement
```
Agent: implementer-builder
Task: "Implement according to plan: {plan_output}"
Context: project root at {project_path}
Output: files changed + test results
```

### review
```
Agent: reviewer-critic
Task: "Review the following changes: {implementation_output}"
Context: changed files from implementation
Output: list of issues with priorities
```

### test
```
Agent: integrator-qa
Task: "Run tests and validate: {task_description}"
Context: {implementation_output}
Output: test results + integration status
```

## Spot-check Protocol

После каждого шага:
1. Прочитай 2-3 ключевых файла через SDK file.read()
2. Запусти тесты
3. Сравни с ожиданием
4. При отклонении — скорректируй следующий шаг

## Мониторинг

Используй orchestrator-monitor плагин для отслеживания:
- Количество активных сессий
- Средняя длительность
- Процент ошибок
- Метрики по каждому агенту
```

---

## 9. Шаг 6: Запуск

### Пошаговая инструкция

```bash
# 1. Установка SDK
npm install @opencode-ai/sdk

# 2. Копирование конфигурации
# Убедись, что opencode.json находится в корне проекта
# и содержит конфигурацию агентов из Шага 1

# 3. Копирование агентов
# Файлы .md агентов должны быть в agents/
# agents/orchestrator-conductor.md
# agents/researcher-explorer.md
# agents/implementer-builder.md
# agents/reviewer-critic.md
# agents/architect-planner.md
# agents/integrator-qa.md
# agents/debug-troubleshooter.md
# agents/doc-maintainer.md

# 4. Копирование плагина
# .opencode/plugins/orchestrator-monitor.ts

# 5. Запуск OpenCode Server
opencode serve --port 4096

# 6. В отдельном терминале — запуск оркестратора
npx tsx orchestrator.ts

# 7. Мониторинг
# - TUI: opencode (подключится к тому же серверу)
# - Плагин: логи в консоли сервера
# - SDK: метрики через API
```

### Проверка работоспособности

```bash
# Проверь, что сервер доступен
curl http://localhost:4096/health

# Проверь список сессий
curl http://localhost:4096/session

# Проверь список агентов
curl http://localhost:4096/agent
```

---

## 10. Путь миграции от v1

### Совместимость компонентов

| Компонент v1 | Совместимость с v2 | Что нужно изменить |
|---|---|---|
| Agent .md файлы | ✅ 95% совместимы | Добавить `permission.task` в YAML-фронтматтер |
| Skills (SKILL.md) | ✅ Полная совместимость | Без изменений |
| Dispatch templates | ⚠️ Требуют адаптации | Заменить `task()` tool на SDK-вызовы |
| Spot-check | ⚠️ Требуют адаптации | Заменить agent's read tool на SDK `file.read()` |
| Оркестратор v1 (prompt-only) | ❌ Заменяется | Новый orchestrator.ts через SDK |

### Пошаговая миграция

**Шаг 1: Обновить agent .md файлы**

Добавить секцию `permission.task` в YAML-фронтматтер каждого агента. Пример:

```yaml
# Было:
---
description: Research agent
mode: subagent
tools:
  - read
  - glob
  - grep
---

# Стало:
---
description: Research agent
mode: subagent
tools:
  - read
  - glob
  - grep
permission:
  task:
    - research
---
```

**Шаг 2: Skills — без изменений**

Файлы `SKILL.md` не требуют модификаций. Поведенческие инструкции остаются теми же.

**Шаг 3: Адаптировать dispatch templates**

В v1 dispatch шаблоны были текстовыми инструкциями. В v2 они используют SDK-вызовы:

```typescript
// v1 (prompt-only):
// "Используй task() tool чтобы вызвать researcher-explorer"

// v2 (SDK-based):
const result = await runSession(task, "researcher-explorer");
```

**Шаг 4: Spot-check через SDK**

```typescript
// v1: Агент читал файлы через свой read tool
// v2: Оркестратор читает файлы через SDK напрямую

const fileContent = await client.file.read({
  sessionId,
  path: "src/index.ts",
});
```

**Шаг 5: Тестирование миграции**

Запусти оркестратор на маленьком пайплайне (2-3 шага) и убедись, что:
- Сессии создаются корректно
- Агенты получают правильные инструменты
- Task permissions работают
- Результаты агрегируются правильно

### Оценка усилий

| Задача | Время |
|---|---|
| Обновить agent .md файлы (8 агентов) | 30 минут |
| Создать orchestrator.ts | 2-3 часа |
| Создать orchestrator-monitor плагин | 1-2 часа |
| Адаптировать dispatch templates | 1 час |
| Тестирование и отладка | 2-3 часа |
| **Итого** | **7-10 часов** |

---

## 11. Финальная сводка

### Сравнение подходов

| Критерий | v1 (prompt-only) | v2 (SDK-based) | OpenHands |
|---|---|---|---|
| Управление сессиями | Через промпт агенту | Программно через SDK | Через UI/API |
| Параллелизм | Ограничен (агент сам управляет) | Нативный (Promise.all) | Нативный |
| Мониторинг | Нет | Плагин + SSE | Built-in UI |
| Точность контроля | Низкая (промпт = лимит) | Высокая (код = полный контроль) | Средняя |
| Отладка | Сложная (через промпт) | Простая (логи, breakpoints) | Через UI |
| Масштабируемость | Ограничена контекстом | Не ограничена | Не ограничена |
| Зависимости | Нет | @opencode-ai/sdk | OpenHands server |
| Гибкость | Низкая | Высокая | Средняя |
| Enterprise | Нет | Нет | Да |

### Что даёт SDK-based подход (v2)

1. **Программное управление** — создание, мониторинг и завершение сессий из кода
2. **Параллелизм** —真正的 параллельное выполнение через `Promise.all`
3. **Агрегация** — результаты собираются в структурированные объекты
4. **Таймауты** — защита от зависших сессий
5. **Мониторинг** — плагин с метриками в реальном времени
6. **Spot-check** — программная проверка через SDK file.read()
7. **Гибкость** — можно писать любую логику оркестрации на TypeScript
8. **Тестируемость** — каждый компонент можно тестировать отдельно

### Когда что использовать

| Сценарий | Рекомендация |
|---|---|
| Простые задачи, одна сессия | v1 (prompt-only) — проще, быстрее |
| Сложные пайплайны, параллелизм | v2 (SDK-based) — полный контроль |
| Команда, always-on, enterprise | OpenHands — готовые решения |
| Кастомный оркестратор, тонкая настройка | v2 (SDK-based) — максимальная гибкость |
| Быстрый прототип | v1 (prompt-only) — минимум кода |
| Продакшен пайплайны | v2 (SDK-based) — надёжность и мониторинг |

---

> **Итог:** OpenCode обладает всей необходимой инфраструктурой для построения масштабируемого оркестратора. SDK-based подход (v2) даёт программный контроль над сессиями, параллелизмом и мониторингом — всё, что нужно для production-ready пайплайнов. OpenHands остаётся лучшим выбором для enterprise/team-сценариев, где важны always-on, Docker sandbox и shared UI.
