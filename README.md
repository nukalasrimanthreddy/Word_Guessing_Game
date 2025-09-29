# Word Guessing Game

A web-based Word Guessing Game built with **Django** and **MongoDB**. Players can register, login, and play a daily word guessing game with limited attempts. Admins can view daily and user-wise reports.

---

## Features

- **Player Features:**
  - Register and login
  - Start a new game
  - Submit guesses and get feedback (green, orange, grey)
  - Play up to 3 games per day
  - Track guesses and game status

- **Admin Features:**
  - View daily reports (number of users, words tried, total guesses, correct guesses)
  - View user-specific reports

---

## Technologies Used

- Python 3.x  
- Django  
- MongoDB (Atlas or local)  
- HTML/CSS for frontend  

---

## Setup Instructions

### 1. Clone the Repository (if using Git)
```bash
git clone https://github.com/nukalasrimanthreddy/Word_Guessing_Game.git
cd Word_Guessing_Game
```

### 2. Or Download the ZIP
Extract the ZIP and navigate to the project folder.

### 3. Create `.env` File  
Inside the project root, create a file named `.env` and add your MongoDB connection string:  
```env
MONGO_URI=your_mongodb_connection_string
```

### 4. Setup Virtual Environment
```bash
python -m venv venv
```

### 5. Activate Virtual Environment
Windows:
```bash
venv\Scripts\activate
```
Mac/Linux:
```bash
source venv/bin/activate
```

### 6. Install Dependencies
```bash
pip install -r requirements.txt
```

### 7. Start the Server
```bash
python manage.py runserver
```

The website will be available at: http://localhost:8000

---

## Notes
**Ensure you have an active internet connection because the app uses a MongoDB database hosted on MongoDB Atlas.**

**If you have MongoDB installed locally, update the `.env` file with your local connection string.**

---

## MongoDB Collections
- **users** – Stores user credentials and type (player/admin)
- **words** – Stores the list of words for the game
- **games** – Stores active and completed game records
- **guesses** – Stores all guesses submitted by players

---

## How to Play
- Register as a player.
- Login to start playing.
- Click "Start Game" to get a random word.
- Enter your guesses in the input box (5-letter words).
  
**Feedback colors:**
- Green: Correct letter in correct position
- Orange: Correct letter in wrong position
- Grey: Letter not in word
  
**Maximum 5 guesses per game.**

**Admins can login to view reports but cannot play games.**

---

## Author
**Nukala Srimanth Reddy**  

**GitHub: https://github.com/nukalasrimanthreddy**
