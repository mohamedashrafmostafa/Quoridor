# ♟️ Quoridor AI
 
**Course:** CSE472s - Artificial Intelligence
**Semester:** Spring 2026
**Department:** Computer and Systems Engineering Department
**Institution:** Ain Shams University - Faculty of Engineering, Specialized Programs
 
---
 
## 👥 Team Members
 
| # | Name                   | Student ID |
|---|------------------------|------------|
| 1 | Amr Ahmed Nagy         |2300162|
| 2 | Mohamed Ashraf Mohamed |2300475|
| 3 | Omar Ahmed Morshed     |2300131|
| 4 | Ali Ahmed Ayman        |2300346|
| 5 | Mohamed Ehab Abdelbary |2300570|
 
---
 
## 📖 Project Description
 
Quoridor AI is a complete implementation of the abstract strategy board game **Quoridor**, originally invented by Mirko Marchesi (1997) and winner of the Mensa Mind Game award. The game is played on a 9×9 board where two players race to move their pawn to the opposite side while strategically placing walls to block their opponent. This project implements the full ruleset, a graphical user interface, and an AI opponent powered by the Minimax algorithm with Alpha-Beta pruning.
 
---
 
## ✨ Implemented Features
 
1. **Full Quoridor Ruleset:** Complete 2-player implementation including orthogonal pawn movement, wall placement, jump-over mechanics, and diagonal fallback moves.
2. **Wall Validation:** Walls cannot overlap, cross, or completely block a player's path — enforced via a pathfinding check on every placement attempt.
3. **Human vs. Human Mode:** Two players can play locally on the same machine.
4. **Human vs. Computer Mode:** Play against an AI opponent.
5. **AI Opponent:** A computer opponent that evaluates future game states and selects optimal moves.
6. **Valid Move Highlighting:** Legal moves are highlighted on the board to guide the player.
7. **Game State Visualization:** The board, pawns, walls, turn indicator, and wall counts are all displayed in real time.
8. **Winner Announcement & Game Reset:** The game detects win conditions and allows the player to restart.
---
 
## 🤖 AI Algorithm
 
The computer opponent uses the **Minimax algorithm with Alpha-Beta Pruning**:
 
- **Minimax** builds a game tree of possible future moves, assuming both players play optimally. The AI maximizes its own advantage while minimizing the opponent's.
- **Alpha-Beta Pruning** cuts off branches of the game tree that cannot influence the final decision, significantly reducing computation time and allowing a deeper search depth.
- **Heuristic Evaluation** uses the difference in shortest path lengths (via BFS/Dijkstra) between the two players as the board evaluation score — the AI favors positions where its path to the goal is shorter than the opponent's.
---
 
## 🏗️ Architecture & Design
 
The project is separated into three clean layers:
 
| Layer | Responsibility |
|---|---|
| **Game Logic** | Board state, move validation, wall placement, win detection |
| **AI Engine** | Minimax tree search, Alpha-Beta pruning, heuristic evaluation |
| **GUI / Presentation** | Board rendering, user input, game state display |
 
This separation ensures the AI and game logic can be tested independently of the interface.
 
---
 

 
## 🎮 Controls
 
| Action | Control |
|---|---|
| Move pawn | Click a highlighted square |
| Place wall | Click between two squares on the board edge |
| Reset game | Click the **Reset** button |
 
---
 
## 📥 How to Get the Project
 
Clone the repository using Git:
 
```bash
git clone https://github.com/amrrnagy/Quoridor.git
cd Quoridor
```
 
Or download it directly from GitHub:
[https://github.com/amrrnagy/Quoridor](https://github.com/amrrnagy/Quoridor_AI)
 
---
 ## 🚀 How to Play / Run the Game

You can run Quoridor AI either by downloading the standalone executable (no installation required) or by running the Python source code directly.

### Option 1: Play Immediately 
If you just want to play the game without installing Python or any dependencies:
1. Go to the **[Releases](../../releases)** section on the right side of this GitHub repository.
2. Download the latest `Quoridor.exe` file.
3. Double-click the downloaded file to play immediately!

---

### Option 2: Run from Source
If you want to view, edit, or run the raw Python code, ensure you have Python (version 3.x recommended) installed on your system.

1. **Clone and navigate to the project directory:**
   ```bash
   git clone [https://github.com/amrrnagy/Quoridor.git]
   cd Quoridor
   ```

2. **Set up a virtual environment (Recommended):**
   This keeps your project dependencies isolated from your global Python installation.
   ```bash
   python -m venv venv
   
   # Activate on Windows:
   venv\Scripts\activate
   
   # Activate on macOS/Linux:
   source venv/bin/activate
   ```

3. **Install the required dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Execute the game:**
   ```bash
   python main.py
   ```
---
 
## 🎬 Demo Video
<div>
  <a href="https://youtu.be/WKwINbpfrHU" target="_blank">
    <img src="https://img.youtube.com/vi/WKwINbpfrHU/maxresdefault.jpg" alt="Watch the Quoridor AI Demo Video" width="720" style="border-radius: 10px; box-shadow: 0px 4px 10px rgba(0,0,0,0.3);" />
  </a>
</div>

---
## 🖼️ User Interface & Gameplay

Here is a look at the Quoridor AI interface and gameplay flow:

### 1. Main Menu
Choose your game mode (Human vs. Human or Human vs. Computer) and select your AI difficulty level.

<img width="1002" height="714" alt="Screenshot 2026-05-28 211919" src="https://github.com/user-attachments/assets/e7fb973d-b834-4db7-a7c7-140571beb26e" />

---

### 2. Gameplay
The 9×9 grid features valid move highlighting, pawn tracking, and real-time wall placement validation.

<img width="999" height="714" alt="Screenshot 2026-05-28 211944" src="https://github.com/user-attachments/assets/54f5aa62-df79-4782-87f9-6bb308c51265" />

---

### 3. Game Over
The system instantly detects when a pawn reaches the opposing baseline, halts inputs, and declares the winner.

<img width="371" height="340" alt="Screenshot 2026-05-28 212008" src="https://github.com/user-attachments/assets/045780db-7ebb-454f-a5bc-52da91670816" />

---


 
*Computer and Systems Engineering Department — Ain Shams University — Spring 2026*
