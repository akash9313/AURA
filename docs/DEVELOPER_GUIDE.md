# AURA AI OS — Production Developer Guide & Engineering Handbook

> **Document Authority**: Master Developer & Engineering Handbook  
> **Target Audience**: Core Systems Engineers, AI Scientists, DevOps Engineers, Plugin Authors  
> **Status**: Approved & Enforced  

---

## 1. Developer Setup & Environment Bootstrap

### 1.1 Prerequisites
- **Python**: 3.11 or higher (Python 3.14 recommended).
- **Node.js**: v20 or higher.
- **Git**: 2.38 or higher.

### 1.2 Quick Start Bootstrap
```bash
# Clone the repository
git clone https://github.com/akash9313/AURA.git
cd AURA

# Run developer environment diagnostic runner
python scripts/dev_setup.py

# Run benchmark suite
python benchmarks/benchmark_engine.py
```

---

## 2. Testing Pyramid & Quality Standards

```
                      / \
                     / UI \         (Selenium / Playwright / Frontend Webview)
                    /------\
                   / System \       (End-to-End Workflow Execution & Speech Loop)
                  /----------\
                 / Integration\     (EventBus + Memory + Vision + Windows Automation)
                /--------------\
               /   Unit Tests   \   (Fast, Mocked Hardware/LLM Peripherals, >85% Coverage)
              --------------------
```

### 2.1 Automated Test Suites
- **Backend Unit Tests**: `python -m unittest discover -s backend/tests -t backend`
- **Frontend Type Checks**: `cd frontend && npx tsc`
- **Security Scans**: `bandit -r backend/`
- **Code Quality**: `black --check backend/` & `ruff check backend/`

---

## 3. Plugin SDK & Extensions

Plugins allow third-party developers to extend AURA with custom tools, providers, and capabilities without modifying core engine logic.

### 3.1 Creating a New Plugin
```bash
# Generate boilerplate template
python sdk/plugin_cli.py create --name "MyCustomExtension" --out plugins/

# Validate manifest integrity
python sdk/plugin_cli.py validate --dir plugins/MyCustomExtension

# Package into distributable archive
python sdk/plugin_cli.py package --dir plugins/MyCustomExtension --out dist/
```

---

## 4. Release Process & Semantic Versioning

AURA follows **Semantic Versioning (`MAJOR.MINOR.PATCH`)**:
- **MAJOR**: Breaking kernel event enum changes or complete architecture shifts.
- **MINOR**: New subsystem engines (e.g., Cognitive Engine, Vision Engine, Browser Agent).
- **PATCH**: Bug fixes, performance optimizations, and documentation updates.

---

## 5. Engineering Roadmap (v0.5 → v1.0)

| Version | Target Milestone | Status | Key Deliverables |
| :--- | :--- | :--- | :--- |
| **v0.5** | **Cognitive Core & Orchestrator** | ✅ Completed | EventBus kernel, Memory Engine, Agent Orchestrator, Windows Engine. |
| **v0.6** | **Browser Agent & Vision Engine** | ✅ Completed | Playwright browser automation, Vision OCR, UI element detector. |
| **v0.7** | **Cognitive Engine & Planning** | ✅ Completed | 8-stage Cognitive Execution Loop, GoalManager, DecisionEngine, Reflection. |
| **v0.8** | **AURA Desktop Application Shell** | ✅ Completed | Tauri/React glassmorphism UI, Command Palette (`Ctrl+K`), Voice Waveform. |
| **v0.9** | **Developer Platform & Plugin SDK** | ✅ Completed | GitHub Actions CI/CD, Docker stack, Plugin SDK CLI, Benchmarking suite. |
| **v1.0** | **Native Production Release** | 🚀 Target | Distributed multi-device sync, local hardware NPU offloading, cloud marketplace. |
