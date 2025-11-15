# 🕊️ How to Talk to the Lark

A simple guide to running the web interface.

---

## Step 1: Install Flask (first time only)

Open your terminal and run:
```bash
pip install -r requirements.txt
```

---

## Step 2: Start the Lark

In your terminal, from the project folder, run:
```bash
python app.py
```

You should see:
```
============================================================
  🕊️  THE LONDON LARK
  Opening her wings...
============================================================

  Open your browser to: http://localhost:5000
```

---

## Step 3: Open Your Browser

Go to: **http://localhost:5000**

You'll see a dark, poetic page with a text box.

---

## Step 4: Talk to Her

Type something like:
- "I'm feeling melancholy and want somewhere quiet"
- "Something weird and playful in East London tonight"
- "Folk music in North London this weekend"

Press **Enter** or click **"Ask the Lark"**

---

## Step 5: Stop When Done

Press **Ctrl+C** in the terminal to stop the server.

---

## Troubleshooting

**"Port already in use"**
- Something else is running on port 5000
- Kill it with: `lsof -ti:5000 | xargs kill`
- Or change the port in `app.py` (last line)

**"Module not found"**
- Make sure you're in the right folder
- Run `pip install -r requirements.txt` again

**"Can't connect"**
- Make sure the server is running (you should see "Running on http://localhost:5000")
- Try http://127.0.0.1:5000 instead

---

## Just Want to Feel Her Voice?

That's what this is for. Type naturally. Ask for moods, locations, feelings.

See if she still feels like the Lark you imagined.
