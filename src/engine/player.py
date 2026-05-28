# src/engine/player.py

from dataclasses import dataclass


@dataclass
class Player:
 
    name:   str
    is_ai:  bool
    index:  int


def make_human(name: str, index: int) -> Player:
    return Player(name=name, is_ai=False, index=index)


def make_ai(name: str, index: int) -> Player:
    return Player(name=name, is_ai=True, index=index)