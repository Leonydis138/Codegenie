pip install streamlit-sortables
import streamlit as st
import json, uuid, threading, time
from pathlib import Path
from datetime import datetime
from pyvis.network import Network
import plotly.express as px
from websocket import create_connection
import streamlit.components.v1 as components
from streamlit_sortables import sortable_list

# -----------------------------
# Config & WebSocket
# -----------------------------
WS_URL = "ws://localhost:8000/ws"

def start_ws():
    ws = create_connection(WS_URL)
    st.session_state.ws = ws
    while True:
        try:
            msg = ws.recv()
            data = json.loads(msg)
            st.session_state.project_data = data
        except:
            break

if "ws" not in st.session_state:
    st.session_state.project_data = None
    threading.Thread(target=start_ws, daemon=True).start()
    st.info("Connecting to server...")

# Wait for initial data
while st.session_state.project_data is None:
    time.sleep(0.1)

project = st.session_state.project_data["projects"][0]

# -----------------------------
# Helper Functions
# -----------------------------
def save_and_broadcast():
    st.session_state.ws.send(json.dumps(st.session_state.project_data))

def reorder_tasks(new_order):
    task_map = {t["id"]:t for t in project["tasks"]}
    project["tasks"] = [task_map[tid] for tid in new_order if tid in task_map]
    save_and_broadcast()

def reorder_subtasks(task_id,new_order):
    for t in project["tasks"]:
        if t["id"]==task_id:
            sub_map = {s["id"]:s for s in t["subtasks"]}
            t["subtasks"] = [sub_map[sid] for sid in new_order if sid in sub_map]
            save_and_broadcast()
            break

def update_task(task_id, field, value):
    for t in project["tasks"]:
        if t["id"]==task_id:
            t[field]=value
            save_and_broadcast()
            break

def update_subtask(task_id, subtask_id, field, value):
    for t in project["tasks"]:
        if t["id"]==task_id:
            for s in t["subtasks"]:
                if s["id"]==subtask_id:
                    s[field]=value
                    save_and_broadcast()
                    return

def add_subtask(task_id,title):
    for t in project["tasks"]:
        if t["id"]==task_id:
            new_id = str(uuid.uuid4())
            t["subtasks"].append({"id":new_id,"title":title,"status":"todo","depends_on":[]})
            save_and_broadcast()
            return

def delete_subtask(task_id, subtask_id):
    for t in project["tasks"]:
        if t["id"]==task_id:
            t["subtasks"] = [s for s in t["subtasks"] if s["id"]!=subtask_id]
            save_and_broadcast()
            return

def is_subtask_blocked(subtask, task_subtasks):
    for dep_id in subtask.get("depends_on",[]):
        dep = next((s for s in task_subtasks if s["id"]==dep_id), None)
        if dep and dep["status"] != "done":
            return True
    return False

# -----------------------------
# Streamlit UI
# -----------------------------
st.set_page_config(page_title="CodeGenie Real-Time Collaborative", layout="wide")
st.title("🧞 CodeGenie Real-Time Collaborative Task Manager")

# Drag-and-Drop Tasks
st.subheader("Drag & Drop Tasks")
task_titles = [t["title"] for t in project["tasks"]]
new_order_titles = sortable_list(task_titles,key="tasks_sortable")
if new_order_titles != task_titles:
    new_order_ids = [project["tasks"][task_titles.index(t)]["id"] for t in new_order_titles]
    reorder_tasks(new_order_ids)
    st.success("Tasks reordered!")

# Tasks & Subtasks
st.subheader("📝 Tasks & Subtasks Editor")
for t in project["tasks"]:
    with st.expander(f"{t['title']} - {t['status']} - {t.get('priority','N/A')}"):
        title = st.text_input("Title", t["title"], key=f"title_{t['id']}")
        status = st.selectbox("Status", ["todo","in-progress","done"], index=["todo","in-progress","done"].index(t["status"]))
        if st.button("Save Task", key=f"save_{t['id']}"):
            update_task(t['id'],"title",title)
            update_task(t['id'],"status",status)
            st.success("Task updated!")

        # Subtasks Drag-and-Drop
        st.markdown("**Subtasks (Drag & Drop)**")
        sub_titles = [s["title"] for s in t["subtasks"]]
        new_sub_order = sortable_list(sub_titles,key=f"sub_sortable_{t['id']}")
        if new_sub_order != sub_titles:
            new_sub_ids = [t["subtasks"][sub_titles.index(s)]["id"] for s in new_sub_order]
            reorder_subtasks(t['id'],new_sub_ids)
            st.success("Subtasks reordered!")

        for s in t["subtasks"]:
            blocked = is_subtask_blocked(s,t['subtasks'])
            cols = st.columns([3,2,2,1])
            with cols[0]:
                new_title = st.text_input("Title", s["title"], key=f"sub_title_{s['id']}")
            with cols[1]:
                new_status = st.selectbox("Status", ["todo","in-progress","done"], index=["todo","in-progress","done"].index(s["status"]))
                if blocked:
                    st.markdown("⚠️ Blocked due to dependencies")
                    new_status = "todo"
            with cols[2]:
                dep_ids = [x['id'] for x in t["subtasks"] if x['id']!=s['id']]
                dep_titles = {x['id']:x['title'] for x in t["subtasks"] if x['id']!=s['id']}
                new_deps = st.multiselect("Depends On", options=dep_ids, format_func=lambda x: dep_titles[x], default=s.get("depends_on",[]), key=f"sub_dep_{s['id']}")
            with cols[3]:
                if st.button("Save", key=f"save_sub_{s['id']}"):
                    s["depends_on"] = new_deps
                    update_subtask(t['id'],s['id'],"title",new_title)
                    update_subtask(t['id'],s['id'],"status",new_status)
                    st.success("Subtask updated!")
            with st.expander("Delete Subtask"):
                if st.button("Delete", key=f"del_sub_{s['id']}"):
                    delete_subtask(t['id'],s['id'])
                    st.warning("Subtask deleted!")
                    st.experimental_rerun()

        # Add new subtask
        new_sub_title = st.text_input("New Subtask Title", key=f"new_sub_{t['id']}")
        if st.button("Add Subtask", key=f"add_sub_{t['id']}") and new_sub_title.strip():
            add_subtask(t['id'],new_sub_title.strip())
            st.success("Subtask added!")
            st.experimental_rerun()

# -----------------------------
# Dashboard & Analytics
# -----------------------------
st.subheader("Project Dashboard")
total_tasks = len(project["tasks"])
completed_tasks = len([t for t in project["tasks"] if t["status"]=="done"])
blocked_subtasks = sum(is_subtask_blocked(s,t["subtasks"]) for t in project["tasks"] for s in t.get("subtasks",[]))
st.metric("Total Tasks", total_tasks)
st.metric("Completed Tasks", f"{completed_tasks} ({completed_tasks/total_tasks*100:.1f}%)" if total_tasks>0 else "0%")
st.metric("Blocked Subtasks", blocked_subtasks)
st.progress(completed_tasks/total_tasks if total_tasks>0 else 0)

# -----------------------------
# PyVis Dependency Graph
# -----------------------------
def draw_graph():
    net = Network(height="600px", width="100%", directed=True)
    status_colors = {"todo":"gray","in-progress":"skyblue","done":"green"}
    for t in project["tasks"]:
        overdue = datetime.strptime(t.get("due",datetime.today().strftime("%Y-%m-%d")),"%Y-%m-%d") < datetime.today()
        color = "red" if overdue else status_colors.get(t["status"],"gray")
        net.add_node(t["id"], label=t["title"], color=color, size=25, physics=True)
        for s in t["subtasks"]:
            blocked = is_subtask_blocked(s,t["subtasks"])
            s_color = "orange" if blocked else status_colors.get(s["status"],"gray")
            net.add_node(s["id"], label=s["title"], color=s_color, size=15, physics=True)
            net.add_edge(t["id"], s["id"])
            for dep_id in s.get("depends_on",[]):
                net.add_edge(dep_id,s["id"], color="orange", physics=False)
    for dep in project.get("dependencies",[]):
        net.add_edge(dep[0], dep[1], color="black")
    net.toggle_physics(True)
    net.show_buttons(filter_=['physics'])
    net.save_graph("graph.html")
    html = open("graph.html").read()
    components.html(html, height=600, scrolling=True)

st.subheader("Dependency Graph")
draw_graph()

# -----------------------------
# Gantt Chart
# -----------------------------
st.subheader("Gantt Chart")
df = pd.DataFrame(project["tasks"])
df['start'] = datetime.today()
df['end'] = pd.to_datetime(df.get('due',datetime.today().strftime("%Y-%m-%d")))
color_map = {"todo":"gray","in-progress":"skyblue","done":"green"}
fig = px.timeline(df, x_start="start", x_end="end", y="title", color="status", color_discrete_map=color_map, hover_data=["title","priority"])
fig.update_yaxes(autorange="reversed")
st.plotly_chart(fig,use_container_width=True)
