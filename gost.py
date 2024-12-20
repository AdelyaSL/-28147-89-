import tkinter as tk
from tkinter import messagebox
import binascii
import os

S = [
    [0xF, 0xC, 0x2, 0xA, 0x6, 0x4, 0x5, 0x0, 0x7, 0x9, 0xE, 0xD, 0x1, 0xB, 0x8, 0x3],
    [0xB, 0x6, 0x3, 0x4, 0xC, 0xF, 0xE, 0x2, 0x7, 0xD, 0x8, 0x0, 0x5, 0xA, 0x9, 0x1],
    [0x1, 0xC, 0xB, 0x0, 0xF, 0xE, 0x6, 0x5, 0xA, 0xD, 0x4, 0x8, 0x9, 0x3, 0x7, 0x2],
    [0x1, 0x5, 0xE, 0xC, 0xA, 0x7, 0x0, 0xD, 0x6, 0x2, 0xB, 0x4, 0x9, 0x3, 0xF, 0x8],
    [0x0, 0xC, 0x8, 0x9, 0xD, 0x2, 0xA, 0xB, 0x7, 0x3, 0x6, 0x5, 0x4, 0xE, 0xF, 0x1],
    [0x8, 0x0, 0xF, 0x3, 0x2, 0x5, 0xE, 0xB, 0x1, 0xA, 0x4, 0x7, 0xC, 0x9, 0xD, 0x6],
    [0x3, 0x0, 0x6, 0xF, 0x1, 0xE, 0x9, 0x2, 0xD, 0x8, 0xC, 0x4, 0xB, 0xA, 0x5, 0x7],
    [0x1, 0xA, 0x6, 0x8, 0xF, 0xB, 0x0, 0x4, 0xC, 0x3, 0x5, 0x9, 0x7, 0xD, 0x2, 0xE],
]

def s_transform(value):
    result = 0
    for i in range(8):
        result |= S[i][(value >> (4 * i)) & 0xF] << (4 * i)
    return result

def encrypt_block(block, key, decrypt=False):
    left = (block >> 32) & 0xFFFFFFFF
    right = block & 0xFFFFFFFF
    keys = key[::-1] if decrypt else key 

    for round in range(16):
        temp = (right + keys[round % 8]) & 0xFFFFFFFF
        temp = s_transform(temp)
        temp = ((temp << 11) | (temp >> (32 - 11))) & 0xFFFFFFFF
        temp ^= left
        left = right
        right = temp

    return (right << 32) | left

def text_to_blocks(text):
    data = text.encode('utf-8')
    padding = (8 - len(data) % 8) % 8
    data += bytes([padding] * padding)
    blocks = [int.from_bytes(data[i:i + 8], 'big') for i in range(0, len(data), 8)]
    return blocks

def blocks_to_text(blocks):
    data = b"".join(block.to_bytes(8, 'big') for block in blocks)
    padding = data[-1]
    return data[:-padding].decode('utf-8')

def generate_key():
    return os.urandom(32)

def encrypt_message(message, key):
    key_blocks = [int.from_bytes(key[i:i + 4], 'big') for i in range(0, len(key), 4)]
    blocks = text_to_blocks(message)
    encrypted_blocks = [encrypt_block(block, key_blocks) for block in blocks]
    return " ".join(f"{block:016x}" for block in encrypted_blocks)  # Маленькие буквы

def decrypt_message(encrypted_message, key):
    key_blocks = [int.from_bytes(key[i:i + 4], 'big') for i in range(0, len(key), 4)]
    blocks = [int(block, 16) for block in encrypted_message.split()]
    decrypted_blocks = [encrypt_block(block, key_blocks, decrypt=True) for block in blocks]
    return blocks_to_text(decrypted_blocks)

def run_gui():
    def on_generate_key():
        key = generate_key()
        entry_key.delete(0, tk.END)
        entry_key.insert(0, binascii.hexlify(key).decode('utf-8'))

    def on_encrypt():
        message = entry_message.get()
        key_input = entry_key.get()
        try:
            key = bytes.fromhex(key_input)
            if len(key) != 32:
                raise ValueError
        except ValueError:
            messagebox.showerror("Ошибка", "Ключ должен быть длиной 256 бит (64 символа в шестнадцатеричном формате).")
            return
        encrypted = encrypt_message(message, key)
        text_result.delete("1.0", tk.END)
        text_result.insert(tk.END, encrypted)

    def on_decrypt():
        encrypted_message = entry_message.get().strip()
        key_input = entry_key.get()
        try:
            key = bytes.fromhex(key_input)
            if len(key) != 32:
                raise ValueError
        except ValueError:
            messagebox.showerror("Ошибка", "Ключ должен быть длиной 256 бит (64 символа в шестнадцатеричном формате).")
            return

        if not encrypted_message:
            messagebox.showerror("Ошибка", "Поле сообщения пустое. Вставьте зашифрованное сообщение для расшифровки.")
            return

        try:
            decrypted = decrypt_message(encrypted_message, key)
            text_result.delete("1.0", tk.END)
            text_result.insert(tk.END, decrypted)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось расшифровать сообщение: {e}")

    window = tk.Tk()
    window.title("ГОСТ 28147-89 Шифрование и Расшифровка")

    tk.Label(window, text="Сообщение:").grid(row=0, column=0, sticky=tk.W)
    entry_message = tk.Entry(window, width=40)
    entry_message.grid(row=0, column=1)

    tk.Button(window, text="Сгенерировать ключ", command=on_generate_key).grid(row=1, column=0, columnspan=2)

    tk.Label(window, text="Ключ:").grid(row=2, column=0, sticky=tk.W)
    entry_key = tk.Entry(window, width=40)
    entry_key.grid(row=2, column=1)

    tk.Button(window, text="Зашифровать", command=on_encrypt).grid(row=3, column=0, columnspan=2)

    tk.Button(window, text="Расшифровать", command=on_decrypt).grid(row=4, column=0, columnspan=2)

    tk.Label(window, text="Результат:").grid(row=5, column=0, sticky=tk.W)
    text_result = tk.Text(window, height=10, width=50)
    text_result.grid(row=6, column=0, columnspan=2)

    window.mainloop()

if __name__ == "__main__":
    run_gui()
