"""
=====================================================================
 DRAGON QUEST MINI  -  Game RPG 2D Sederhana untuk Belajar OOP Python
=====================================================================
Jalankan :  python rpg_oop.py          (butuh Python 3.8+, Tkinter bawaan)
Kontrol  :  Panah / WASD = jalan | tabrak musuh = mulai battle
            Battle: A = serang, 1/2/3 = skill, R = kabur
            Klik item di daftar lalu tombol "Pakai Item"
Tujuan   :  Kalahkan Naga Merah di pojok kanan atas!

PETA MATERI OOP (cari tag [OOP-n] di kode ini):
 [OOP-1]  Class & Object            -> semua class, mis. Player(), Slime()
 [OOP-2]  Constructor __init__      -> setiap class
 [OOP-3]  Atribut & Method          -> Character.sembuhkan(), dll.
 [OOP-4]  Class variable            -> GameObject.jumlah_objek
 [OOP-5]  Encapsulation (private)   -> Character.__hp + @property
 [OOP-6]  Inheritance & super()     -> Character -> Player / Enemy -> Slime
 [OOP-7]  Method overriding         -> Enemy.terima_serangan, SuperPotion.gunakan
 [OOP-8]  Polymorphism              -> battle memanggil .serang() / .gunakan()
 [OOP-9]  Abstract class (ABC)      -> GameObject, Item, Skill, Character
 [OOP-10] Multiple inheritance      -> Peti(GameObject, Interaktif) / mixin
 [OOP-11] classmethod / staticmethod-> Potion.kecil(), GameLog.hias()
 [OOP-12] Magic / dunder methods    -> __str__ __eq__ __lt__ __add__ __len__ ...
 [OOP-13] Composition / Aggregation -> Player punya Inventory, Game punya Peta
 [OOP-14] Custom Exception          -> InventoryPenuhError, MPKurangError
 [OOP-15] Enum & dataclass          -> Elemen, Stats
 [OOP-16] Template method pattern   -> Skill.pakai() -> efek(), Enemy.giliran()
"""

import random
import tkinter as tk
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum

UKURAN = 48                 # ukuran 1 tile (piksel)
KOLOM, BARIS = 14, 10
PETA = [
    "##############",
    "#............#",
    "#..~~....#...#",
    "#..~~....#...#",
    "#........#...#",
    "#...##.......#",
    "#...##...~~..#",
    "#........~~..#",
    "#............#",
    "##############",
]


# ===================================================================
# [OOP-15] Enum & dataclass
# ===================================================================
class Elemen(Enum):
    FISIK = "Fisik"
    API = "Api"
    ES = "Es"


@dataclass
class Stats:
    atk: int = 0
    df: int = 0

    # [OOP-12] operator overloading: Stats + Stats
    def __add__(self, lain):
        return Stats(self.atk + lain.atk, self.df + lain.df)

    def __str__(self):
        return f"ATK {self.atk} / DEF {self.df}"


# ===================================================================
# [OOP-14] Custom Exception (hierarki exception)
# ===================================================================
class GameError(Exception):
    """Induk semua error game."""


class InventoryPenuhError(GameError):
    pass


class MPKurangError(GameError):
    pass


class AksiTidakValidError(GameError):
    pass


# ===================================================================
# [OOP-4] [OOP-11] Class variable, classmethod, staticmethod
# ===================================================================
class GameLog:
    _pesan = []          # class variable: dipakai bersama semua pemanggil
    listener = None      # fungsi callback ke UI

    @classmethod
    def tulis(cls, teks):
        cls._pesan.append(teks)
        if cls.listener:
            cls.listener(teks)

    @classmethod
    def total(cls):
        return len(cls._pesan)

    @staticmethod
    def hias(teks):      # staticmethod: tidak butuh self/cls
        return "• " + teks


# ===================================================================
# [OOP-9] Abstract class + [OOP-4] class variable
# ===================================================================
class GameObject(ABC):
    jumlah_objek = 0     # dihitung setiap objek baru dibuat

    def __init__(self, x, y, nama):
        self.x = x
        self.y = y
        self.nama = nama
        GameObject.jumlah_objek += 1

    @abstractmethod
    def gambar(self, canvas, px, py, s):
        """Setiap objek harus bisa menggambar dirinya (px,py = piksel, s = ukuran)."""


# ===================================================================
# [OOP-10] Mixin untuk multiple inheritance
# ===================================================================
class Interaktif:
    def interaksi(self, pemain):
        raise NotImplementedError("Subclass harus mengimplementasikan interaksi()")


# ===================================================================
# ITEM  ([OOP-9] abstract, [OOP-8] polymorphism, [OOP-11] classmethod)
# ===================================================================
class Item(ABC):
    sekali_pakai = True

    def __init__(self, nama, deskripsi=""):
        self.nama = nama
        self.deskripsi = deskripsi

    @abstractmethod
    def gunakan(self, pemain):
        ...

    # [OOP-12] dunder methods
    def __str__(self):
        return f"{self.nama} - {self.deskripsi}"

    def __eq__(self, lain):
        return isinstance(lain, Item) and self.nama == lain.nama

    def __hash__(self):
        return hash(self.nama)


class Potion(Item):
    def __init__(self, nama, pulih):
        super().__init__(nama, f"Pulihkan {pulih} HP")      # [OOP-6] super()
        self.pulih = pulih

    def gunakan(self, pemain):
        n = pemain.sembuhkan(self.pulih)
        return f"{pemain.nama} minum {self.nama}, HP +{n}"

    @classmethod                      # [OOP-11] alternative constructor
    def kecil(cls):
        return cls("Potion Kecil", 30)

    @classmethod
    def besar(cls):
        return cls("Potion Besar", 70)


class SuperPotion(Potion):
    def __init__(self):
        super().__init__("Super Potion", 60)
        self.deskripsi = "Pulihkan 60 HP + 20 MP"

    def gunakan(self, pemain):        # [OOP-7] overriding + memanggil induk
        pesan = super().gunakan(pemain)
        pemain.mp = min(pemain.mp_maks, pemain.mp + 20)
        return pesan + " dan MP +20"


class Pedang(Item):
    sekali_pakai = False              # equipment tidak habis

    def __init__(self, nama, bonus_atk):
        super().__init__(nama, f"Senjata ATK +{bonus_atk}")
        self.bonus = Stats(atk=bonus_atk)

    def gunakan(self, pemain):
        pemain.senjata = self
        return f"{pemain.nama} memakai {self.nama}!"


# ===================================================================
# [OOP-13] Composition: Player MEMILIKI Inventory
# ===================================================================
class Inventory:
    def __init__(self, kapasitas=6):
        self._items = []
        self.kapasitas = kapasitas

    def tambah(self, item):
        if len(self._items) >= self.kapasitas:
            raise InventoryPenuhError("Inventory penuh!")
        self._items.append(item)

    def hapus(self, item):
        self._items.remove(item)

    # [OOP-12] membuat objek berperilaku seperti list
    def __len__(self):
        return len(self._items)

    def __iter__(self):
        return iter(self._items)

    def __getitem__(self, i):
        return self._items[i]

    def __contains__(self, item):
        return item in self._items


# ===================================================================
# SKILL  ([OOP-9] abstract, [OOP-16] template method)
# ===================================================================
class Skill(ABC):
    def __init__(self, nama, biaya_mp):
        self.nama = nama
        self.biaya_mp = biaya_mp

    def pakai(self, pengguna, target):          # template method
        if pengguna.mp < self.biaya_mp:
            raise MPKurangError(f"MP tidak cukup untuk {self.nama}!")
        pengguna.mp -= self.biaya_mp
        return self.efek(pengguna, target)

    @abstractmethod
    def efek(self, pengguna, target):
        ...

    def __str__(self):
        return f"{self.nama} ({self.biaya_mp} MP)"


class Fireball(Skill):
    def __init__(self):
        super().__init__("Fireball", 10)

    def efek(self, pengguna, target):
        dmg = int(pengguna.stats.atk * 1.8) + random.randint(0, 4)
        n = target.terima_serangan(dmg, Elemen.API)
        return f"{pengguna.nama} melempar Fireball ke {target.nama}: -{n} HP"


class IceShard(Skill):
    def __init__(self):
        super().__init__("Ice Shard", 12)

    def efek(self, pengguna, target):
        dmg = int(pengguna.stats.atk * 1.8) + random.randint(0, 4)
        n = target.terima_serangan(dmg, Elemen.ES)
        return f"{pengguna.nama} menembakkan Ice Shard ke {target.nama}: -{n} HP"


class Heal(Skill):
    def __init__(self):
        super().__init__("Heal", 8)

    def efek(self, pengguna, target):
        n = pengguna.sembuhkan(40)
        return f"{pengguna.nama} merapal Heal, HP +{n}"


# ===================================================================
# CHARACTER  ([OOP-5] encapsulation, [OOP-9] abstract)
# ===================================================================
class Character(GameObject):
    def __init__(self, x, y, nama, hp, stats, warna):
        super().__init__(x, y, nama)
        self.__hp_maks = hp          # private (name mangling)
        self.__hp = hp
        self.stats_dasar = stats
        self.warna = warna

    # ---- property = getter/setter yang aman ----
    @property
    def hp(self):
        return self.__hp

    @hp.setter
    def hp(self, nilai):
        self.__hp = max(0, min(nilai, self.__hp_maks))   # selalu 0..maks

    @property
    def hp_maks(self):
        return self.__hp_maks

    @property
    def hidup(self):
        return self.__hp > 0

    @property
    def stats(self):
        return self.stats_dasar

    def naikkan_hp_maks(self, n):
        self.__hp_maks += n

    # ---- method biasa ----
    def terima_serangan(self, dmg, elemen=Elemen.FISIK):
        dmg = max(1, dmg - self.stats.df)
        self.hp -= dmg
        return dmg

    def sembuhkan(self, jumlah):
        sebelum = self.hp
        self.hp += jumlah
        return self.hp - sebelum

    @abstractmethod
    def serang(self, target):
        """Polymorphism: tiap karakter menyerang dengan caranya sendiri."""

    def gambar_hp(self, canvas, px, py, s):
        lebar = s * 0.9
        rasio = self.hp / self.hp_maks
        canvas.create_rectangle(px + s * .05, py - 8, px + s * .05 + lebar, py - 2,
                                fill="#400", outline="black")
        canvas.create_rectangle(px + s * .05, py - 8, px + s * .05 + lebar * rasio, py - 2,
                                fill="#4caf50" if rasio > .35 else "#f44336", outline="")

    # [OOP-12]
    def __str__(self):
        return f"{self.nama} (HP {self.hp}/{self.hp_maks})"

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.nama} hp={self.hp}>"

    def __lt__(self, lain):          # bisa di-sort / dibandingkan: a < b
        return self.hp < lain.hp


# ===================================================================
# PLAYER  ([OOP-6] inheritance, [OOP-13] composition)
# ===================================================================
class Player(Character):
    def __init__(self, x, y, nama="Hero"):
        super().__init__(x, y, nama, 100, Stats(12, 3), "#2979ff")
        self.mp = self.mp_maks = 50
        self.level = 1
        self.exp = 0
        self.emas = 0
        self.senjata = None
        self.inventory = Inventory()                       # composition
        self.skills = [Fireball(), IceShard(), Heal()]     # composition

    @property
    def stats(self):                                       # overriding property
        bonus = self.senjata.bonus if self.senjata else Stats()
        return self.stats_dasar + bonus                    # pakai __add__

    @property
    def exp_butuh(self):
        return self.level * 30

    def serang(self, target):
        dmg = self.stats.atk + random.randint(-2, 3)
        n = target.terima_serangan(dmg)
        return f"{self.nama} menebas {target.nama}: -{n} HP"

    def pakai_item(self, indeks):
        if not 0 <= indeks < len(self.inventory):
            raise AksiTidakValidError("Pilih item di daftar dulu!")
        item = self.inventory[indeks]
        pesan = item.gunakan(self)           # polymorphism
        if item.sekali_pakai:
            self.inventory.hapus(item)
        return pesan

    def tambah_exp(self, jumlah):
        pesan = [f"{self.nama} mendapat {jumlah} EXP."]
        self.exp += jumlah
        while self.exp >= self.exp_butuh:
            self.exp -= self.exp_butuh
            self.level += 1
            self.stats_dasar = Stats(self.stats_dasar.atk + 3, self.stats_dasar.df + 1)
            self.naikkan_hp_maks(15)
            self.hp = self.hp_maks
            self.mp_maks += 10
            self.mp = self.mp_maks
            pesan.append(f"LEVEL UP! Sekarang level {self.level}!")
        return " ".join(pesan)

    def gambar(self, canvas, px, py, s):
        canvas.create_rectangle(px + .25 * s, py + .4 * s, px + .75 * s, py + .9 * s,
                                fill=self.warna, outline="black")
        canvas.create_oval(px + .28 * s, py + .1 * s, px + .72 * s, py + .5 * s,
                           fill="#ffcc99", outline="black")
        canvas.create_oval(px + .38 * s, py + .26 * s, px + .45 * s, py + .33 * s, fill="black")
        canvas.create_oval(px + .55 * s, py + .26 * s, px + .62 * s, py + .33 * s, fill="black")
        canvas.create_line(px + .8 * s, py + .85 * s, px + .95 * s, py + .35 * s,
                           fill="silver", width=max(2, s // 14))
        self.gambar_hp(canvas, px, py, s)


# ===================================================================
# ENEMY  ([OOP-6] hierarki, [OOP-7] overriding, [OOP-8] polymorphism)
# ===================================================================
class Enemy(Character):
    lemah = None                     # elemen kelemahan (diisi subclass)

    def __init__(self, x, y, nama, hp, stats, warna, exp, emas):
        super().__init__(x, y, nama, hp, stats, warna)
        self.exp = exp
        self.emas = emas
        self.giliran_ke = 0

    def terima_serangan(self, dmg, elemen=Elemen.FISIK):    # overriding
        if self.lemah is not None and elemen == self.lemah:
            dmg = int(dmg * 1.5)
            GameLog.tulis(f"Efektif! {self.nama} lemah terhadap {elemen.value}!")
        return super().terima_serangan(dmg, elemen)

    def giliran(self, target):       # [OOP-16] template method
        self.giliran_ke += 1
        return self.serang(target)


class Slime(Enemy):
    lemah = Elemen.API

    def __init__(self, x, y):
        super().__init__(x, y, "Slime", 30, Stats(6, 0), "#66bb6a", 20, 5)

    def serang(self, target):
        n = target.terima_serangan(self.stats.atk + random.randint(0, 2))
        return f"Slime menabrak {target.nama}: -{n} HP"

    def gambar(self, canvas, px, py, s):
        canvas.create_oval(px + .1 * s, py + .4 * s, px + .9 * s, py + .92 * s,
                           fill=self.warna, outline="#1b5e20")
        canvas.create_oval(px + .3 * s, py + .55 * s, px + .4 * s, py + .65 * s, fill="black")
        canvas.create_oval(px + .6 * s, py + .55 * s, px + .7 * s, py + .65 * s, fill="black")
        self.gambar_hp(canvas, px, py, s)


class Goblin(Enemy):
    lemah = Elemen.ES

    def __init__(self, x, y):
        super().__init__(x, y, "Goblin", 55, Stats(11, 2), "#2e7d32", 40, 12)

    def serang(self, target):
        kritikal = random.random() < 0.25
        dmg = self.stats.atk * (2 if kritikal else 1)
        n = target.terima_serangan(dmg)
        teks = "KRITIKAL! " if kritikal else ""
        return f"{teks}Goblin menusuk {target.nama}: -{n} HP"

    def gambar(self, canvas, px, py, s):
        canvas.create_polygon(px + .15 * s, py + .3 * s, px + .3 * s, py + .2 * s,
                              px + .3 * s, py + .45 * s, fill=self.warna, outline="black")
        canvas.create_polygon(px + .85 * s, py + .3 * s, px + .7 * s, py + .2 * s,
                              px + .7 * s, py + .45 * s, fill=self.warna, outline="black")
        canvas.create_rectangle(px + .28 * s, py + .2 * s, px + .72 * s, py + .9 * s,
                                fill=self.warna, outline="black")
        canvas.create_oval(px + .36 * s, py + .35 * s, px + .46 * s, py + .45 * s, fill="red")
        canvas.create_oval(px + .54 * s, py + .35 * s, px + .64 * s, py + .45 * s, fill="red")
        self.gambar_hp(canvas, px, py, s)


class Naga(Enemy):
    lemah = Elemen.ES

    def __init__(self, x, y):
        super().__init__(x, y, "Naga Merah", 180, Stats(18, 5), "#c62828", 150, 100)

    def serang(self, target):
        if self.giliran_ke % 3 == 0:                     # tiap giliran ke-3
            n = target.terima_serangan(self.stats.atk * 2, Elemen.API)
            return f"Naga menyemburkan NAPAS API! {target.nama}: -{n} HP"
        n = target.terima_serangan(self.stats.atk + random.randint(0, 4))
        return f"Naga mencakar {target.nama}: -{n} HP"

    def gambar(self, canvas, px, py, s):
        canvas.create_polygon(px + .0 * s, py + .2 * s, px + .3 * s, py + .55 * s,
                              px + .1 * s, py + .8 * s, fill="#8e0000", outline="black")
        canvas.create_polygon(px + 1. * s, py + .2 * s, px + .7 * s, py + .55 * s,
                              px + .9 * s, py + .8 * s, fill="#8e0000", outline="black")
        canvas.create_oval(px + .2 * s, py + .3 * s, px + .8 * s, py + .95 * s,
                           fill=self.warna, outline="black")
        canvas.create_polygon(px + .3 * s, py + .1 * s, px + .38 * s, py + .35 * s,
                              px + .22 * s, py + .35 * s, fill="#ffeb3b", outline="black")
        canvas.create_polygon(px + .7 * s, py + .1 * s, px + .78 * s, py + .35 * s,
                              px + .62 * s, py + .35 * s, fill="#ffeb3b", outline="black")
        canvas.create_oval(px + .36 * s, py + .45 * s, px + .46 * s, py + .55 * s, fill="yellow")
        canvas.create_oval(px + .54 * s, py + .45 * s, px + .64 * s, py + .55 * s, fill="yellow")
        self.gambar_hp(canvas, px, py, s)


# ===================================================================
# [OOP-10] MULTIPLE INHERITANCE: GameObject + Interaktif
# ===================================================================
class Peti(GameObject, Interaktif):
    def __init__(self, x, y, item, emas=0):
        super().__init__(x, y, "Peti")
        self.item = item
        self.emas = emas
        self.terbuka = False

    def interaksi(self, pemain):
        if self.terbuka:
            return "Peti ini sudah kosong."
        try:
            pemain.inventory.tambah(self.item)
        except InventoryPenuhError as e:          # [OOP-14] menangkap exception
            return f"{e} Tidak bisa mengambil {self.item.nama}."
        self.terbuka = True
        pemain.emas += self.emas
        return f"Peti terbuka! Dapat {self.item.nama} dan {self.emas} emas."

    def gambar(self, canvas, px, py, s):
        warna = "#6d4c41" if not self.terbuka else "#3e2723"
        canvas.create_rectangle(px + .12 * s, py + .35 * s, px + .88 * s, py + .85 * s,
                                fill=warna, outline="black")
        canvas.create_rectangle(px + .12 * s, py + .35 * s, px + .88 * s, py + .5 * s,
                                fill="#8d6e63", outline="black")
        if not self.terbuka:
            canvas.create_rectangle(px + .44 * s, py + .45 * s, px + .56 * s, py + .62 * s,
                                    fill="gold", outline="black")


class Penyembuh(GameObject, Interaktif):
    def __init__(self, x, y):
        super().__init__(x, y, "Penyembuh")
        self.sisa = 3

    def interaksi(self, pemain):
        if self.sisa <= 0:
            return "Penyembuh: Maaf, kekuatanku sudah habis..."
        self.sisa -= 1
        pemain.hp = pemain.hp_maks
        pemain.mp = pemain.mp_maks
        return f"Penyembuh memulihkan HP & MP-mu! (sisa {self.sisa}x)"

    def gambar(self, canvas, px, py, s):
        canvas.create_oval(px + .15 * s, py + .15 * s, px + .85 * s, py + .85 * s,
                           fill="#f8bbd0", outline="black")
        canvas.create_rectangle(px + .42 * s, py + .25 * s, px + .58 * s, py + .75 * s,
                                fill="white", outline="")
        canvas.create_rectangle(px + .25 * s, py + .42 * s, px + .75 * s, py + .58 * s,
                                fill="white", outline="")


# ===================================================================
# [OOP-13] Peta (dipakai Game lewat composition)
# ===================================================================
class Peta:
    WARNA = {".": "#8bc34a", "#": "#616161", "~": "#29b6f6"}

    def __init__(self, data):
        self.data = data

    def bisa_dilewati(self, x, y):
        return 0 <= y < len(self.data) and 0 <= x < len(self.data[0]) and self.data[y][x] == "."

    def gambar(self, canvas):
        for y, baris in enumerate(self.data):
            for x, t in enumerate(baris):
                px, py = x * UKURAN, y * UKURAN
                canvas.create_rectangle(px, py, px + UKURAN, py + UKURAN,
                                        fill=self.WARNA[t], outline="#7cb342" if t == "." else "#424242")
                if t == "#":
                    canvas.create_line(px, py + 24, px + UKURAN, py + 24, fill="#424242")
                    canvas.create_line(px + 24, py, px + 24, py + 24, fill="#424242")
                if t == "~":
                    canvas.create_arc(px + 8, py + 14, px + 40, py + 34, start=0, extent=180,
                                      style="arc", outline="white", width=2)


# ===================================================================
# BATTLE  (mengatur giliran; tidak tahu apa-apa tentang UI)
# ===================================================================
class Battle:
    def __init__(self, pemain, musuh):
        self.pemain = pemain
        self.musuh = musuh
        self.selesai = False
        self.menang = None           # True / False / None (kabur)
        GameLog.tulis(f"Pertarungan melawan {musuh.nama} dimulai!")

    def _jalankan(self, aksi):
        if self.selesai:
            return
        try:
            GameLog.tulis(aksi())
        except GameError as e:       # aksi tidak valid = tidak memakan giliran
            GameLog.tulis(f"! {e}")
            return
        if not self.musuh.hidup:
            self._menang()
            return
        GameLog.tulis(self.musuh.giliran(self.pemain))     # polymorphism
        if not self.pemain.hidup:
            self.selesai, self.menang = True, False
            GameLog.tulis("Kamu kalah...")

    def _menang(self):
        self.selesai, self.menang = True, True
        GameLog.tulis(f"{self.musuh.nama} dikalahkan!")
        self.pemain.emas += self.musuh.emas
        GameLog.tulis(self.pemain.tambah_exp(self.musuh.exp) + f" (+{self.musuh.emas} emas)")

    def serang(self):
        self._jalankan(lambda: self.pemain.serang(self.musuh))

    def skill(self, i):
        self._jalankan(lambda: self.pemain.skills[i].pakai(self.pemain, self.musuh))

    def item(self, i):
        self._jalankan(lambda: self.pemain.pakai_item(i))

    def kabur(self):
        if random.random() < 0.5:
            self.selesai, self.menang = True, None
            GameLog.tulis("Kamu berhasil kabur!")
        else:
            GameLog.tulis("Gagal kabur!")
            GameLog.tulis(self.musuh.giliran(self.pemain))
            if not self.pemain.hidup:
                self.selesai, self.menang = True, False


# ===================================================================
# GAME (UI Tkinter)  - menyatukan semua objek (composition)
# ===================================================================
class Game:
    def __init__(self, root):
        self.root = root
        root.title("Dragon Quest Mini - OOP Python")
        root.resizable(False, False)

        self.canvas = tk.Canvas(root, width=KOLOM * UKURAN, height=BARIS * UKURAN, bg="black")
        self.canvas.grid(row=0, column=0, rowspan=2)

        panel = tk.Frame(root, padx=6, pady=6)
        panel.grid(row=0, column=1, sticky="n")
        self.lbl = tk.Label(panel, justify="left", anchor="w", font=("Consolas", 10), width=40)
        self.lbl.pack(fill="x")
        tk.Label(panel, text="Inventory:", anchor="w").pack(fill="x")
        self.lst = tk.Listbox(panel, height=5, exportselection=False)
        self.lst.pack(fill="x")
        tk.Button(panel, text="Pakai Item", command=self.pakai_item).pack(fill="x", pady=2)

        self.frm = tk.Frame(panel)
        self.frm.pack(fill="x")
        self.tombol = {}
        defs = [("Serang (A)", lambda: self.aksi("serang")),
                ("Fireball (1)", lambda: self.aksi("skill", 0)),
                ("Ice Shard (2)", lambda: self.aksi("skill", 1)),
                ("Heal (3)", lambda: self.aksi("skill", 2)),
                ("Kabur (R)", lambda: self.aksi("kabur"))]
        for i, (teks, cmd) in enumerate(defs):
            b = tk.Button(self.frm, text=teks, command=cmd, width=13)
            b.grid(row=i // 2, column=i % 2, padx=1, pady=1)
            self.tombol[teks] = b
        tk.Button(panel, text="Mulai Ulang", command=self.mulai_baru).pack(fill="x", pady=4)

        self.log = tk.Text(root, width=48, height=14, state="disabled", wrap="word",
                           bg="#1e1e1e", fg="#e0e0e0", font=("Consolas", 9))
        self.log.grid(row=1, column=1, padx=6, pady=4, sticky="n")

        GameLog.listener = self.tampil_log
        root.bind("<Key>", self.tombol_ditekan)
        self.mulai_baru()

    # ---------- setup ----------
    def mulai_baru(self):
        self.peta = Peta(PETA)
        self.pemain = Player(1, 1)
        for item in (Potion.kecil(), Potion.kecil(), Pedang("Pedang Besi", 5)):
            self.pemain.inventory.tambah(item)
        self.objek = [
            Slime(3, 4), Slime(11, 8), Goblin(7, 6), Naga(11, 3),
            Peti(12, 1, Potion.besar(), 20), Peti(2, 8, SuperPotion(), 30),
            Peti(6, 8, Pedang("Pedang Baja", 10), 50),
            Penyembuh(6, 1),
        ]
        self.battle = None
        self.akhir = None            # None / "menang" / "kalah"
        self.log.config(state="normal")
        self.log.delete("1.0", "end")
        self.log.config(state="disabled")
        GameLog.tulis("Selamat datang! Kalahkan Naga Merah di pojok kanan atas.")
        GameLog.tulis("Tips: Slime lemah Api, Goblin & Naga lemah Es.")
        self.refresh()

    # ---------- input ----------
    def tombol_ditekan(self, e):
        k = e.keysym.lower()
        if self.akhir:
            return
        if self.battle:
            peta = {"a": ("serang",), "1": ("skill", 0), "2": ("skill", 1),
                    "3": ("skill", 2), "r": ("kabur",)}
            if k in peta:
                self.aksi(*peta[k])
            return
        arah = {"up": (0, -1), "w": (0, -1), "down": (0, 1), "s": (0, 1),
                "left": (-1, 0), "a": (-1, 0), "right": (1, 0), "d": (1, 0)}
        if k in arah:
            if e.widget is self.lst and k in ("up", "down"):
                return               # biarkan listbox memakai panah atas/bawah
            self.gerak(*arah[k])

    def objek_di(self, x, y):
        for o in self.objek:
            if (o.x, o.y) == (x, y):
                return o
        return None

    def gerak(self, dx, dy):
        nx, ny = self.pemain.x + dx, self.pemain.y + dy
        if not self.peta.bisa_dilewati(nx, ny):
            return
        o = self.objek_di(nx, ny)
        if isinstance(o, Enemy):
            self.battle = Battle(self.pemain, o)
        elif isinstance(o, Interaktif):                  # duck typing / mixin
            GameLog.tulis(o.interaksi(self.pemain))
        else:
            self.pemain.x, self.pemain.y = nx, ny
        self.refresh()

    # ---------- aksi ----------
    def aksi(self, nama, *arg):
        if not self.battle:
            GameLog.tulis("! Tidak sedang bertarung.")
            return
        getattr(self.battle, nama)(*arg)
        self.cek_battle()
        self.refresh()

    def pakai_item(self):
        sel = self.lst.curselection()
        idx = sel[0] if sel else -1
        if self.akhir:
            return
        if self.battle:
            self.battle.item(idx)
            self.cek_battle()
        else:
            try:
                GameLog.tulis(self.pemain.pakai_item(idx))
            except GameError as e:
                GameLog.tulis(f"! {e}")
        self.refresh()

    def cek_battle(self):
        b = self.battle
        if not b or not b.selesai:
            return
        if b.menang is True:
            self.objek.remove(b.musuh)
            if isinstance(b.musuh, Naga):
                self.akhir = "menang"
                GameLog.tulis("SELAMAT! Kamu menyelamatkan kerajaan!")
        elif b.menang is False:
            self.akhir = "kalah"
        self.battle = None

    # ---------- tampilan ----------
    def tampil_log(self, teks):
        self.log.config(state="normal")
        self.log.insert("end", GameLog.hias(teks) + "\n")
        self.log.see("end")
        self.log.config(state="disabled")

    def refresh(self):
        c = self.canvas
        c.delete("all")
        if self.battle:
            self.gambar_battle()
        else:
            self.peta.gambar(c)
            for o in self.objek:
                o.gambar(c, o.x * UKURAN, o.y * UKURAN, UKURAN)
            self.pemain.gambar(c, self.pemain.x * UKURAN, self.pemain.y * UKURAN, UKURAN)
        if self.akhir:
            c.create_rectangle(120, 170, 550, 310, fill="black", outline="white", width=3)
            teks = "KAMU MENANG!" if self.akhir == "menang" else "GAME OVER"
            c.create_text(335, 240, text=teks, fill="gold" if self.akhir == "menang" else "red",
                          font=("Arial", 32, "bold"))
        p = self.pemain
        self.lbl.config(text=(
            f"{p.nama}  Lv {p.level}  EXP {p.exp}/{p.exp_butuh}\n"
            f"HP {p.hp}/{p.hp_maks}   MP {p.mp}/{p.mp_maks}   Emas {p.emas}\n"
            f"{p.stats}   Senjata: {p.senjata.nama if p.senjata else '-'}\n"
            f"Objek dibuat: {GameObject.jumlah_objek}   Log: {GameLog.total()}"))
        self.lst.delete(0, "end")
        for item in p.inventory:                         # Inventory bisa di-iterasi
            self.lst.insert("end", str(item))
        status = "normal" if (self.battle and not self.akhir) else "disabled"
        for b in self.tombol.values():
            b.config(state=status)

    def gambar_battle(self):
        c = self.canvas
        c.create_rectangle(0, 0, KOLOM * UKURAN, BARIS * UKURAN, fill="#b3e5fc", outline="")
        c.create_rectangle(0, 300, KOLOM * UKURAN, BARIS * UKURAN, fill="#7cb342", outline="")
        m = self.battle.musuh
        self.pemain.gambar(c, 90, 170, 150)
        m.gambar(c, 420, 150 if not isinstance(m, Naga) else 120, 170)
        c.create_text(165, 140, text=str(self.pemain), font=("Arial", 11, "bold"))
        c.create_text(505, 110, text=str(m), font=("Arial", 11, "bold"))
        c.create_text(335, 20, text="BATTLE!  A=Serang  1/2/3=Skill  R=Kabur",
                      font=("Arial", 12, "bold"), fill="#b71c1c")


if __name__ == "__main__":
    root = tk.Tk()
    Game(root)
    root.mainloop()
