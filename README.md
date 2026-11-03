<div align="center">

# 🤖 ARES — Autonomous Runtime AI Agent

**A local voice-controlled assistant that runs tasks on your PC.**

![Python](https://img.shields.io/badge/Python-3-3776AB?style=flat-square&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-000000?style=flat-square&logo=flask&logoColor=white)
![Whisper](https://img.shields.io/badge/Speech-faster--whisper-111827?style=flat-square)
![Windows](https://img.shields.io/badge/Windows-0078D6?style=flat-square&logo=windows&logoColor=white)

![License: MIT](https://img.shields.io/badge/License-MIT-22c55e?style=flat-square)

</div>

---

## What it does

Say what you need, and ARES does it. It listens through the microphone, turns speech into text locally with Whisper, works out the task and runs it — opening apps, typing, clicking, or kicking off a scheduled job. Everything runs on your own machine.

## Features

- 🎙️ **Voice in, voice out** — local speech recognition (faster-whisper) and text-to-speech
- 🧠 **AI core** that turns a request into steps
- 🖱️ **Desktop automation** — keyboard, mouse, clipboard and window control
- ⏰ **Triggers and scheduler** — run tasks at a time or when something happens
- 🌐 **Web dashboard** to watch and control the agent
- 🪵 Structured logging for every action

## Project layout

```
agent/        agent logic
ai/           AI helpers
automation/   desktop actions
tasks/        task definitions
triggers/     event triggers
voice/        speech in / out
web/          web UI
main_web.py   start the web UI
start_ares.py start the agent
```

## Run it

```bash
pip install -r requirements.txt
python start_ares.py        # agent
python main_web.py          # web dashboard
```

On Windows you can also use `START_ARES_VOICE.bat`. Run `setup_whisper.bat` once to download the speech model.

## License

MIT — see [LICENSE](LICENSE).

---

<div align="center">
Built by <a href="https://github.com/SuvadipPanja">Suvadip Panja</a>
</div>
