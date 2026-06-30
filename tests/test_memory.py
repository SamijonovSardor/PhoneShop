"""Conversation memory moduli testi."""
import sys
import io
import gc

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

import shutil
import tempfile
from pathlib import Path

from src.memory import ConversationMemory


def _make_memory(max_messages: int = 4) -> tuple[ConversationMemory, Path]:
    tmp_dir = Path(tempfile.mkdtemp(prefix="memory_test_"))
    db_path = tmp_dir / "test.db"
    return ConversationMemory(db_path=db_path, max_messages=max_messages), tmp_dir


def _cleanup(mem: ConversationMemory, tmp_dir: Path) -> None:
    del mem
    gc.collect()
    try:
        shutil.rmtree(tmp_dir, ignore_errors=True)
    except Exception:
        pass


def test_basic_operations() -> None:
    mem, tmp_dir = _make_memory()
    try:
        chat_id = 12345
        assert mem.count(chat_id) == 0
        assert mem.get_history(chat_id) == []

        mem.add_message(chat_id, "user", "Salom")
        mem.add_message(chat_id, "assistant", "Va alaykum!")
        assert mem.count(chat_id) == 2

        history = mem.get_history(chat_id)
        assert len(history) == 2
        assert history[0]["role"] == "user"
        assert history[0]["content"] == "Salom"
        assert history[1]["role"] == "assistant"
        print("[OK] Asosiy qo'shish va olish ishlaydi")
    finally:
        _cleanup(mem, tmp_dir)


def test_sliding_window() -> None:
    mem, tmp_dir = _make_memory(max_messages=3)
    try:
        chat_id = 111
        for i in range(5):
            mem.add_message(chat_id, "user", f"savol {i}")
            mem.add_message(chat_id, "assistant", f"javob {i}")

        history = mem.get_history(chat_id)
        assert len(history) == 3, f"Kutilgan 3 ta, topildi: {len(history)}"
        assert history[0]["content"] == "javob 3"
        assert history[1]["content"] == "savol 4"
        assert history[2]["content"] == "javob 4"
        print(f"[OK] Sliding window: 10 xabardan 3 tasi saqlandi (oxirgi 3)")
    finally:
        _cleanup(mem, tmp_dir)


def test_clear() -> None:
    mem, tmp_dir = _make_memory()
    try:
        chat_id = 222
        mem.add_message(chat_id, "user", "test1")
        mem.add_message(chat_id, "assistant", "test2")
        assert mem.count(chat_id) == 2

        deleted = mem.clear(chat_id)
        assert deleted == 2
        assert mem.count(chat_id) == 0
        print("[OK] Clear ishlaydi")
    finally:
        _cleanup(mem, tmp_dir)


def test_separate_chats() -> None:
    mem, tmp_dir = _make_memory()
    try:
        mem.add_message(1, "user", "User 1 xabari")
        mem.add_message(2, "user", "User 2 xabari")
        mem.add_message(1, "assistant", "User 1 ga javob")

        assert mem.count(1) == 2
        assert mem.count(2) == 1
        assert mem.get_history(1)[0]["content"] == "User 1 xabari"
        assert mem.get_history(2)[0]["content"] == "User 2 xabari"
        print("[OK] Har bir chat_id alohida saqlanadi")
    finally:
        _cleanup(mem, tmp_dir)


def test_role_validation() -> None:
    mem, tmp_dir = _make_memory()
    try:
        try:
            mem.add_message(1, "system", "bu xato bo'lishi kerak")
            assert False, "system role qabul qilinmasligi kerak"
        except ValueError:
            print("[OK] Noto'g'ri role rad etiladi")
    finally:
        _cleanup(mem, tmp_dir)


def test_persistence() -> None:
    """Restart simulyatsiyasi - yangi instance yaratish."""
    mem1, tmp_dir = _make_memory()
    chat_id = 999
    mem1.add_message(chat_id, "user", "Doimiy xabar")
    mem1.add_message(chat_id, "assistant", "Doimiy javob")
    del mem1
    gc.collect()

    db_path = tmp_dir / "test.db"
    mem2 = ConversationMemory(db_path=db_path, max_messages=4)
    try:
        history = mem2.get_history(chat_id)
        assert len(history) == 2, f"Kutilgan 2 ta, topildi: {len(history)}"
        assert history[0]["content"] == "Doimiy xabar"
        print("[OK] Restart'dan keyin tarix saqlanib qoladi")
    finally:
        _cleanup(mem2, tmp_dir)


if __name__ == "__main__":
    print("[TEST] Memory testlari boshlanmoqda...\n")
    test_basic_operations()
    print()
    test_sliding_window()
    print()
    test_clear()
    print()
    test_separate_chats()
    print()
    test_role_validation()
    print()
    test_persistence()
    print("\n[SUCCESS] Barcha memory testlari muvaffaqiyatli o'tdi!")
