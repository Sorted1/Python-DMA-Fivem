# FiveM Memory ESP & Invisibility PoC

This is a **proof-of-concept (PoC)** Python script using [`memprocfs`](https://github.com/ufrisk/MemProcFS) to interact with live memory in **FiveM/GTA V**, demonstrating:

- **World-to-screen transformation**
- **Local player position retrieval**
- **Player invisibility toggling**
- **Pedestrian list enumeration**

> ⚠️ **Disclaimer**: This code is for educational and research purposes only. Misuse of this code in multiplayer or anti-cheat environments may violate terms of service or laws. Use responsibly.

---

## Features

- 🔍 `world_to_screen` — Projects 3D world coordinates to 2D screen space.
- 👤 `localpos` — Extracts local player coordinates from memory.
- 🫥 `invisable` — Toggles local player invisibility.
- 🧍 `pedlist` — Reads and logs entities in the replay interface ped list.

---

## Requirements

- Python 3.8+
- NumPy
- `memprocfs` Python bindings
- `FiveM_GTAProcess.exe` must be running and MemProcFS must have access.

Install requirements:

```bash
pip install numpy memprocfs
```
## Usage
```bash
python main.py
```
The script will:
1. Attach to the FiveM process via MemProcFS.
2. Continuously prompt for invisibility toggle (`yes` or `no`).
3. Log local player coordinates.
4. Print nearby ped pointers to the console.

---

## Offsets Used

These offsets are verified as of the version b3258. You may need to update them using tools like ReClass or IDA if the game updates:

```python
viewport_offset = 0x201DBA0
world_offset = 0x25B14B0
localplayer_offset = 0x8
pos_offset = 0x90
replay_interface_offset = 0x1FBD4F0
```

---

## Notes

- This is **not an internal cheat**. It reads live memory externally using MemProcFS.
- Ensure MemProcFS is running and has access to the process. Run as admin.
- Tested on Windows 10 with FiveM (b3258 build).

---

## Limitations

- The world-to-screen matrix is read directly from memory but not synchronized with the exact draw tick, so ESP render timing may be off.
- `invisable` only toggles a basic visibility flag — it may not work on all servers.
- `pedlist` does not filter out dead or non-player peds.

---

## License

MIT License

---

## Credits

- [`memprocfs`](https://github.com/ufrisk/MemProcFS) by @ufrisk  
- [Cheat Engine](https://cheatengine.org/) & ReClass.NET community

---

## Screenshot

_No visual overlay used — console-based logging only._
