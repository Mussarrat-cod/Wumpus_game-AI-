# app.py
from flask import Flask, render_template, request, jsonify, session
from wumpus import WumpusWorld
from ai_agent import SimpleAgent
import os

app = Flask(__name__, static_folder="static", template_folder="templates")
app.secret_key = os.environ.get("SECRET_KEY", "dev_secret_change_me")

# In-memory store per session
WORLD_KEY = "w_world"
AI_KEY = "w_ai_enabled"

# Simple global store—maps session id -> (world, agent)
store = {}

def get_world():
    sid = session.get("_id")
    if not sid:
        sid = os.urandom(16).hex()
        session["_id"] = sid
    if sid not in store:
        w = WumpusWorld(size=4, pits_count=3)
        w.reset()
        store[sid] = {"world": w, "agent": SimpleAgent()}
    return store[sid]["world"], store[sid]["agent"]

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/new", methods=["POST"])
def api_new():
    world, _ = get_world()
    size = request.json.get("size", 4)
    pits = request.json.get("pits", 3)
    world.size = int(size)
    world.pits_count = int(pits)
    world.reset()
    session[AI_KEY] = False
    return jsonify(world.state())

@app.route("/api/state", methods=["GET"])
def api_state():
    world, _ = get_world()
    return jsonify(world.state())

@app.route("/api/move", methods=["POST"])
def api_move():
    world, _ = get_world()
    direction = request.json.get("direction")
    return jsonify(world.move(direction))

@app.route("/api/grab", methods=["POST"])
def api_grab():
    world, _ = get_world()
    return jsonify(world.grab())

@app.route("/api/shoot", methods=["POST"])
def api_shoot():
    world, _ = get_world()
    direction = request.json.get("direction")
    return jsonify(world.shoot(direction))

@app.route("/api/climb", methods=["POST"])
def api_climb():
    world, _ = get_world()
    return jsonify(world.climb())

@app.route("/api/reveal", methods=["POST"])
def api_reveal():
    world, _ = get_world()
    return jsonify(world.reveal())

@app.route("/api/ai/toggle", methods=["POST"])
def api_ai_toggle():
    enabled = bool(request.json.get("enabled", False))
    session[AI_KEY] = enabled
    world, _ = get_world()
    world.status = f"AI {'enabled' if enabled else 'disabled'}."
    return jsonify(world.state())

@app.route("/api/ai/step", methods=["POST"])
def api_ai_step():
    world, agent = get_world()
    if world.game_over:
        return jsonify(world.state())
    enabled = session.get(AI_KEY, False)
    if not enabled:
        world.status = "AI is disabled."
        return jsonify(world.state())
    action = agent.next_action(world)
    t = action.get("type")
    if t == "move":
        res = world.move(action["dir"])
    elif t == "grab":
        res = world.grab()
    elif t == "shoot":
        res = world.shoot(action.get("dir", "right"))
    elif t == "climb":
        res = world.climb()
    else:
        world.status = "AI waits."
        res = world.state()
    return jsonify(res)

if __name__ == "__main__":
    app.run(debug=True)
