# 👗 Stylebot — AI-Powered Outfit Stylist for Wildberries

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)]()
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)]()
[![Redis](https://img.shields.io/badge/Redis-Cache-red.svg)]()
[![License](https://img.shields.io/badge/License-MIT-green.svg)]()
[![AI](https://img.shields.io/badge/OpenAI-Integrated-orange.svg)]()

**Stylebot** is an intelligent stylist bot for **Wildberries**, powered by AI.  
It helps users create personalized looks and outfits based on preferences, trends, and inventory — all through an interactive Telegram bot interface.  

Built with ❤️ using **Python**, **aiogram**, and **OpenAI**.

---

## 🚀 Features

- 🤖 **AI Outfit Generator** — Uses OpenAI to suggest personalized looks.  
- 💬 **Complex Dialog System** — Built with `aiogram-dialog` for rich, multi-step conversations.  
- 🛍️ **Wildberries Private API Integration** — Fetches live data from the WB catalog.  
- 💰 **Payment System (YooKassa)** — Integrated payments for premium styling sessions.  
- 🧠 **Database Layer (SQLAlchemy)** — Clean ORM-based structure for user and outfit data.  
- ⚙️ **Redis + Cron Jobs** — For caching, background tasks, and automated maintenance.  
- 🧪 **Pre-commit Hooks & Unit Tests** — Ensures code quality and stability.  
- 🐳 **Fully Dockerized** — Easy to deploy anywhere.

---

## 🧩 Tech Stack

| Component | Description |
|------------|-------------|
| **Language** | Python |
| **Frameworks** | aiogram, aiogram-dialog |
| **AI** | OpenAI API |
| **Database** | PostgreSQL + SQLAlchemy |
| **Cache/Queue** | Redis |
| **Payments** | YooKassa |
| **Testing** | unittest |
| **DevOps** | Docker, cron, pre-commit |

---

## ⚙️ Installation & Setup

### 1. Clone the repository
```bash
git clone https://github.com/cra9had/stylebot.git
cd stylebot
```

### 2. Environment setup
Rename configuration files and fill them with your data:
```bash
mv .env.example .env          # Fill in: BOT_TOKEN, OPENAI_API_KEY, DB_URL, etc.
mv redis_example.conf redis.conf
mv docker-compose_example.conf docker-compose.conf  # Sync DB settings with .env
```

### 3. Configure cron job
On the host machine (Linux):
```bash
crontab -e
```
Add the following line to automatically restart the sub_checker daily:
```bash
0 0 * * * sudo /usr/bin/docker-compose restart sub_checker
```

### 4. Build and run
```bash
sudo docker-compose build
sudo docker-compose up
```

### 5. Stop the bot
Terminate the process manually or:
```bash
sudo docker-compose down
```

---

## 🧠 AI Integration

Stylebot leverages **OpenAI’s models** to:
- Understand user preferences (color, budget, event type)
- Generate stylistic outfit suggestions
- Combine Wildberries catalog data into ready-to-buy looks

---

## 💸 Payments

Integrated with **YooKassa** for seamless in-bot payments — allowing users to unlock advanced styling features or personalized recommendations.

---

## 🧪 Development

Run tests:
```bash
python -m unittest discover tests
```

Run pre-commit hooks:
```bash
pre-commit run --all-files
```

---

## 🐳 Docker Overview

Stylebot runs entirely in Docker containers:
- `bot` — main Telegram bot
- `redis` — caching layer
- `db` — PostgreSQL
- `sub_checker` — scheduled background service (via cron)

---

## 🤝 Contributing

Pull requests are welcome!  
Please make sure to run `pre-commit` and tests before submitting.

---

## 📜 License

This project is licensed under the **MIT License** — see [LICENSE](LICENSE) for details.

---

## ✨ Author

**cra9had**  
🔗 [github.com/cra9had/stylebot](https://github.com/cra9had/stylebot)

---

> _“Fashion meets AI — Stylebot helps you dress smarter.”_
