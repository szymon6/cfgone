
# 🛠️ Cfgone

Minimal Python package that loads your config in one line of code.

## 📦 Installation

```bash
pip install cfgone
```

## ⚡ Quick Start

Create a `config.yaml` file in your current directory:

```yaml
app:
  name: "MyApp"
  port: 8080
  debug: true

database:
  host: "localhost"
  port: 5432
```

Use it in your code:

```python
import cfgone as cfg

print(f"Starting {cfg.app.name} on port {cfg.app.port}")

# Output: Starting MyApp on port 8080
```

## 🧬 Config Inheritance

Split your config into multiple files:

**`base.yaml`**

```yaml
app:
  name: "BaseApp"
  debug: false

database:
  host: "localhost"
```

**`config.yaml`**

```yaml
extends:
  - "base.yaml"

app:
  name: "MyApp"  # overrides base
  port: 8080     # adds new setting

database:
  port: 5432     # merges with base
```

Access your merged config:

```python
import cfgone as cfg

print(cfg.app.name)      # "MyApp"
print(cfg.database.host) # "localhost" (from base.yaml)
```





