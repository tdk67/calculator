import math
import streamlit as st

# -----------------------------------------------------------------------------
# Page Configuration & Layout
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="3D Quaternion Calculator",
    page_icon="🧮",
    layout="wide"
)

# Custom CSS for calculator LCD and keypad layout
st.markdown(
    """
    <style>
    .lcd-display {
        background-color: #0f172a;
        color: #38bdf8;
        font-family: 'Courier New', Courier, monospace;
        padding: 14px 18px;
        border-radius: 8px;
        border: 2px solid #1e293b;
        box-shadow: inset 0 2px 4px rgba(0,0,0,0.6);
        margin-top: 10px;
    }
    .lcd-metric-title {
        color: #94a3b8;
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 2px;
    }
    .lcd-metric-val {
        color: #38bdf8;
        font-size: 1.1rem;
        font-weight: bold;
    }
    .lcd-quaternion-val {
        color: #4ade80;
        font-size: 1.0rem;
        font-weight: bold;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# -----------------------------------------------------------------------------
# Mathematical Engine (Quaternions & 3D Projection)
# -----------------------------------------------------------------------------

def q_mult(q1: list[float], q2: list[float]) -> list[float]:
    """Hamilton product of two quaternions q1 and q2 (format: [w, x, y, z])."""
    w1, x1, y1, z1 = q1
    w2, x2, y2, z2 = q2
    return [
        w1*w2 - x1*x2 - y1*y2 - z1*z2,
        w1*x2 + x1*w2 + y1*z2 - z1*y2,
        w1*y2 - x1*z2 + y1*w2 + z1*x2,
        w1*z2 + x1*y2 - y1*x2 + z1*w2
    ]

def q_normalize(q: list[float]) -> list[float]:
    """Normalizes quaternion to unit length |q| = 1."""
    mag = math.sqrt(q[0]**2 + q[1]**2 + q[2]**2 + q[3]**2)
    if mag == 0:
        return [1.0, 0.0, 0.0, 0.0]
    return [q[0]/mag, q[1]/mag, q[2]/mag, q[3]/mag]

def rotate_vertex(v: list[float], q: list[float]) -> list[float]:
    """Rotates a 3D vertex v using quaternion conjugation p' = q * p * q_conj."""
    p = [0.0, v[0], v[1], v[2]]
    q_conj = [q[0], -q[1], -q[2], -q[3]]
    result = q_mult(q_mult(q, p), q_conj)
    return [result[1], result[2], result[3]]

def q_to_euler(q: list[float]) -> tuple[float, float, float]:
    """Extracts approximate Euler angles in degrees (Pitch X, Yaw Y, Roll Z) from unit quaternion."""
    w, x, y, z = q
    sinr_cosp = 2 * (w * x + y * z)
    cosr_cosp = 1 - 2 * (x * x + y * y)
    pitch_rad = math.atan2(sinr_cosp, cosr_cosp)

    sinp = 2 * (w * y - z * x)
    if abs(sinp) >= 1:
        yaw_rad = math.copysign(math.pi / 2, sinp)
    else:
        yaw_rad = math.asin(sinp)

    siny_cosp = 2 * (w * z + x * y)
    cosy_cosp = 1 - 2 * (y * y + z * z)
    roll_rad = math.atan2(siny_cosp, cosy_cosp)

    return (
        math.degrees(pitch_rad) % 360,
        math.degrees(yaw_rad) % 360,
        math.degrees(roll_rad) % 360
    )

# Initial default quaternion (30° Pitch X, 45° Yaw Y)
_ax = math.radians(30) / 2
_ay = math.radians(45) / 2
_qx = [math.cos(_ax), math.sin(_ax), 0, 0]
_qy = [math.cos(_ay), 0, math.sin(_ay), 0]
INITIAL_Q = q_normalize(q_mult(_qy, _qx))

# Geometry definitions for unit cube
@st.cache_data
def get_cube_geometry():
    vertices = [
        [-1, -1, -1], [ 1, -1, -1], [ 1,  1, -1], [-1,  1, -1],  # Back face (0,1,2,3)
        [-1, -1,  1], [ 1, -1,  1], [ 1,  1,  1], [-1,  1,  1]   # Front face (4,5,6,7)
    ]
    edges = [
        (0, 1), (1, 2), (2, 3), (3, 0),  # Back
        (4, 5), (5, 6), (6, 7), (7, 4),  # Front
        (0, 4), (1, 5), (2, 6), (3, 7)   # Connectors
    ]
    axes = [
        {"name": "X_b", "end": [1.5, 0.0, 0.0], "color": "#ef4444"},  # Red
        {"name": "Y_b", "end": [0.0, 1.5, 0.0], "color": "#22c55e"},  # Green
        {"name": "Z_b", "end": [0.0, 0.0, 1.5], "color": "#3b82f6"}   # Blue
    ]
    world_axes = [
        {"name": "X_w", "end": [1.8, 0.0, 0.0], "color": "#64748b"},
        {"name": "Y_w", "end": [0.0, 1.8, 0.0], "color": "#64748b"},
        {"name": "Z_w", "end": [0.0, 0.0, 1.8], "color": "#64748b"}
    ]
    return vertices, edges, axes, world_axes

CUBE_VERTICES, CUBE_EDGES, AXES_DEFINITIONS, WORLD_AXES_DEFINITIONS = get_cube_geometry()

# -----------------------------------------------------------------------------
# Session State Initialization
# -----------------------------------------------------------------------------
if 'q_current' not in st.session_state:
    st.session_state.q_current = list(INITIAL_Q)

if 'rot_frame' not in st.session_state:
    st.session_state.rot_frame = "Local Body Frame (Q · Δq)"

if 'step_deg' not in st.session_state:
    st.session_state.step_deg = 15.0

if 'calc_buffer' not in st.session_state:
    st.session_state.calc_buffer = ""
if 'active_axis' not in st.session_state:
    st.session_state.active_axis = "Rx"
if 'last_status' not in st.session_state:
    st.session_state.last_status = "Ready"

# -----------------------------------------------------------------------------
# Callbacks for Keypad & Controls
# -----------------------------------------------------------------------------
def reset_angles():
    st.session_state.q_current = [1.0, 0.0, 0.0, 0.0]
    st.session_state.calc_buffer = ""
    st.session_state.last_status = "Reset to Identity [1, 0, 0, 0]"

def reset_to_initial():
    st.session_state.q_current = list(INITIAL_Q)
    st.session_state.calc_buffer = ""
    st.session_state.last_status = "Reset to Initial Tilt (30° Pitch, 45° Yaw)"

def step_angle(axis: str, direction: int):
    step_rad = math.radians(st.session_state.step_deg * direction)
    half_angle = step_rad / 2
    
    if axis == 'x':
        dq = [math.cos(half_angle), math.sin(half_angle), 0.0, 0.0]
        axis_name = "Pitch X"
    elif axis == 'y':
        dq = [math.cos(half_angle), 0.0, math.sin(half_angle), 0.0]
        axis_name = "Yaw Y"
    elif axis == 'z':
        dq = [math.cos(half_angle), 0.0, 0.0, math.sin(half_angle)]
        axis_name = "Roll Z"

    # Local Body Frame (Post-multiplication Q_new = Q * dq) vs Global World Frame (Pre-multiplication Q_new = dq * Q)
    if "Local" in st.session_state.rot_frame:
        new_q = q_mult(st.session_state.q_current, dq)
        frame_text = "Local"
    else:
        new_q = q_mult(dq, st.session_state.q_current)
        frame_text = "World"

    st.session_state.q_current = q_normalize(new_q)
    step_deg_signed = st.session_state.step_deg * direction
    st.session_state.last_status = f"Rotated {axis_name} by {step_deg_signed:+.1f}° ({frame_text} Frame)"

def adjust_step(delta: float):
    new_step = max(5.0, min(90.0, st.session_state.step_deg + delta))
    st.session_state.step_deg = new_step
    st.session_state.last_status = f"Step size set to {new_step}°"

def append_calc_buffer(char: str):
    st.session_state.calc_buffer += char

def clear_calc_buffer():
    st.session_state.calc_buffer = ""
    st.session_state.last_status = "Buffer cleared"

def apply_calc_buffer():
    try:
        val_deg = float(st.session_state.calc_buffer)
        rad = math.radians(val_deg) / 2
        axis = st.session_state.active_axis
        
        if axis == "Rx":
            dq = [math.cos(rad), math.sin(rad), 0.0, 0.0]
        elif axis == "Ry":
            dq = [math.cos(rad), 0.0, math.sin(rad), 0.0]
        elif axis == "Rz":
            dq = [math.cos(rad), 0.0, 0.0, math.sin(rad)]

        if "Local" in st.session_state.rot_frame:
            new_q = q_mult(st.session_state.q_current, dq)
        else:
            new_q = q_mult(dq, st.session_state.q_current)

        st.session_state.q_current = q_normalize(new_q)
        st.session_state.last_status = f"Applied {val_deg:.1f}° to {axis}"
        st.session_state.calc_buffer = ""
    except ValueError:
        st.session_state.last_status = "Invalid number"
        st.session_state.calc_buffer = ""

# -----------------------------------------------------------------------------
# Main Header
# -----------------------------------------------------------------------------
st.title("🧮 3D Quaternion Calculator")
st.caption("Control 3D spatial cube orientation via calculator keypad inputs with live 4D quaternion math.")

# Active Quaternion State
q_final = st.session_state.q_current
euler_pitch, euler_yaw, euler_roll = q_to_euler(q_final)

# -----------------------------------------------------------------------------
# Side-by-Side Main Workspace Layout (Display + Keypad)
# -----------------------------------------------------------------------------
col_display, col_keypad = st.columns([6, 5], gap="large")

with col_display:
    st.subheader("📺 3D Display & LCD Screen")
    
    rot_f = st.segmented_control(
        "Rotation Reference Frame",
        ["Local Body Frame (Q · Δq)", "Global World Frame (Δq · Q)"],
        default=st.session_state.rot_frame
    )
    if rot_f:
        st.session_state.rot_frame = rot_f

    WIDTH, HEIGHT = 500, 300
    SCALE = 85.0
    CX, CY = WIDTH / 2, HEIGHT / 2

    # Distortion-Free Orthographic Projection
    def project_point(v_3d: list[float], q: list[float]) -> tuple[float, float, float]:
        r = rotate_vertex(v_3d, q)
        x_2d = r[0] * SCALE + CX
        y_2d = -r[1] * SCALE + CY  # Flip Y for Cartesian orientation
        return x_2d, y_2d, r[2]

    # Project Cube Vertices
    projected_vertices = []
    for v in CUBE_VERTICES:
        px, py, pz = project_point(v, q_final)
        projected_vertices.append((px, py, pz))

    # Build SVG markup
    svg_elements = []
    svg_elements.append('<rect width="100%" height="100%" fill="#090d16" rx="8"/>')

    # Render Fixed World Reference Frame (Dashed grey lines at origin)
    origin_world = project_point([0, 0, 0], [1, 0, 0, 0])
    for axis in WORLD_AXES_DEFINITIONS:
        end_world = project_point(axis["end"], [1, 0, 0, 0])
        svg_elements.append(
            f'<line x1="{origin_world[0]:.1f}" y1="{origin_world[1]:.1f}" '
            f'x2="{end_world[0]:.1f}" y2="{end_world[1]:.1f}" '
            f'stroke="{axis["color"]}" stroke-width="1.5" stroke-dasharray="3,3" opacity="0.4"/>'
        )

    # Render Local Cube Body Axes (Rotated with cube: Red X_b, Green Y_b, Blue Z_b)
    origin_2d = project_point([0, 0, 0], q_final)
    for axis in AXES_DEFINITIONS:
        end_2d = project_point(axis["end"], q_final)
        svg_elements.append(
            f'<line x1="{origin_2d[0]:.1f}" y1="{origin_2d[1]:.1f}" '
            f'x2="{end_2d[0]:.1f}" y2="{end_2d[1]:.1f}" '
            f'stroke="{axis["color"]}" stroke-width="3" stroke-linecap="round"/>'
        )
        svg_elements.append(
            f'<text x="{end_2d[0]+6:.1f}" y="{end_2d[1]+4:.1f}" '
            f'fill="{axis["color"]}" font-family="sans-serif" font-weight="bold" font-size="14">{axis["name"]}</text>'
        )

    # Render Cube Edges
    for edge in CUBE_EDGES:
        p1 = projected_vertices[edge[0]]
        p2 = projected_vertices[edge[1]]
        svg_elements.append(
            f'<line x1="{p1[0]:.1f}" y1="{p1[1]:.1f}" '
            f'x2="{p2[0]:.1f}" y2="{p2[1]:.1f}" '
            f'stroke="#00d2ff" stroke-width="2.5" stroke-linecap="round"/>'
        )

    # Render Vertices as Nodes
    for p in projected_vertices:
        svg_elements.append(
            f'<circle cx="{p[0]:.1f}" cy="{p[1]:.1f}" r="4.5" fill="#f43f5e"/>'
        )

    svg_code = f'''
    <div style="display: flex; justify-content: center; background-color: #090d16; padding: 6px; border-radius: 8px; border: 1px solid #1e293b;">
        <svg width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}">
            {"".join(svg_elements)}
        </svg>
    </div>
    '''
    st.markdown(svg_code, unsafe_allow_html=True)

    # LCD Status Display
    st.markdown(
        f"""
        <div class="lcd-display">
            <div style="display: flex; justify-content: space-between; margin-bottom: 6px;">
                <div>
                    <div class="lcd-metric-title">Orientation (Pitch / Yaw / Roll °)</div>
                    <div class="lcd-metric-val">X: {euler_pitch:5.1f}° | Y: {euler_yaw:5.1f}° | Z: {euler_roll:5.1f}°</div>
                </div>
                <div style="text-align: right;">
                    <div class="lcd-metric-title">Step / Status</div>
                    <div style="color: #f59e0b; font-weight: bold;">±{st.session_state.step_deg}° | {st.session_state.last_status}</div>
                </div>
            </div>
            <div style="display: flex; justify-content: space-between;">
                <div>
                    <div class="lcd-metric-title">Active Rotation Frame</div>
                    <div style="color: #38bdf8; font-size: 0.95rem; font-weight: bold;">{"Local Body Frame (Q · Δq)" if "Local" in st.session_state.rot_frame else "Global World Frame (Δq · Q)"}</div>
                </div>
                <div style="text-align: right;">
                    <div class="lcd-metric-title">Combined Quaternion [w, x, y, z]</div>
                    <div class="lcd-quaternion-val">[{q_final[0]:+.3f}, {q_final[1]:+.3f}, {q_final[2]:+.3f}, {q_final[3]:+.3f}]</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col_keypad:
    st.subheader("🎮 Calculator Control Keypad")

    tab_numpad, tab_direct = st.tabs(["Numpad 3D Stepping", "Direct Degree Keypad"])

    with tab_numpad:
        st.caption("Press keys to step cube rotation around X, Y, Z axes (Local Body Frame).")
        
        row1_c1, row1_c2, row1_c3, row1_c4 = st.columns(4)
        with row1_c1:
            st.button("7 (+Pitch X)", on_click=step_angle, args=('x', 1), width="stretch")
        with row1_c2:
            st.button("8 (+Yaw Y)", on_click=step_angle, args=('y', 1), width="stretch")
        with row1_c3:
            st.button("9 (+Roll Z)", on_click=step_angle, args=('z', 1), width="stretch")
        with row1_c4:
            st.button("C (Origin 0°)", on_click=reset_angles, width="stretch")

        row2_c1, row2_c2, row2_c3, row2_c4 = st.columns(4)
        with row2_c1:
            st.button("4 (-Pitch X)", on_click=step_angle, args=('x', -1), width="stretch")
        with row2_c2:
            st.button("5 (Reset Tilt)", on_click=reset_to_initial, width="stretch")
        with row2_c3:
            st.button("6 (+Roll Z)", on_click=step_angle, args=('z', 1), width="stretch")
        with row2_c4:
            st.button("+ (Step +15°)", on_click=adjust_step, args=(15.0,), width="stretch")

        row3_c1, row3_c2, row3_c3, row3_c4 = st.columns(4)
        with row3_c1:
            st.button("1 (-Yaw Y)", on_click=step_angle, args=('y', -1), width="stretch")
        with row3_c2:
            st.button("2 (-Roll Z)", on_click=step_angle, args=('z', -1), width="stretch")
        with row3_c3:
            st.button("3 (Step -5°)", on_click=adjust_step, args=(-5.0,), width="stretch")
        with row3_c4:
            st.button("- (Step -15°)", on_click=adjust_step, args=(-15.0,), width="stretch")

        row4_c1, row4_c2, row4_c3, row4_c4 = st.columns(4)
        with row4_c1:
            st.button("0 (Step +5°)", on_click=adjust_step, args=(5.0,), width="stretch")
        with row4_c2:
            st.button(". (Origin 0°)", on_click=reset_angles, width="stretch")
        with row4_c3:
            st.button("90° Roll Z", on_click=step_angle, args=('z', 6), width="stretch")
        with row4_c4:
            st.button("= Apply", on_click=reset_to_initial, type="primary", width="stretch")

    with tab_direct:
        st.caption("Select axis, enter numeric degrees, and press '=' to apply rotation.")
        
        sel_axis = st.segmented_control("Target Axis", ["Rx", "Ry", "Rz"], default=st.session_state.active_axis)
        if sel_axis:
            st.session_state.active_axis = sel_axis

        st.text_input("Buffer Entry (°)", value=st.session_state.calc_buffer or "0", disabled=True)

        d_r1_1, d_r1_2, d_r1_3, d_r1_4 = st.columns(4)
        with d_r1_1:
            st.button("7", key="d7", on_click=append_calc_buffer, args=("7",), width="stretch")
        with d_r1_2:
            st.button("8", key="d8", on_click=append_calc_buffer, args=("8",), width="stretch")
        with d_r1_3:
            st.button("9", key="d9", on_click=append_calc_buffer, args=("9",), width="stretch")
        with d_r1_4:
            st.button("C", key="dc", on_click=clear_calc_buffer, width="stretch")

        d_r2_1, d_r2_2, d_r2_3, d_r2_4 = st.columns(4)
        with d_r2_1:
            st.button("4", key="d4", on_click=append_calc_buffer, args=("4",), width="stretch")
        with d_r2_2:
            st.button("5", key="d5", on_click=append_calc_buffer, args=("5",), width="stretch")
        with d_r2_3:
            st.button("6", key="d6", on_click=append_calc_buffer, args=("6",), width="stretch")
        with d_r2_4:
            st.button("45°", key="d45", on_click=lambda: st.session_state.update({"calc_buffer": "45"}), width="stretch")

        d_r3_1, d_r3_2, d_r3_3, d_r3_4 = st.columns(4)
        with d_r3_1:
            st.button("1", key="d1", on_click=append_calc_buffer, args=("1",), width="stretch")
        with d_r3_2:
            st.button("2", key="d2", on_click=append_calc_buffer, args=("2",), width="stretch")
        with d_r3_3:
            st.button("3", key="d3", on_click=append_calc_buffer, args=("3",), width="stretch")
        with d_r3_4:
            st.button("90°", key="d90", on_click=lambda: st.session_state.update({"calc_buffer": "90"}), width="stretch")

        d_r4_1, d_r4_2, d_r4_3, d_r4_4 = st.columns(4)
        with d_r4_1:
            st.button("0", key="d0", on_click=append_calc_buffer, args=("0",), width="stretch")
        with d_r4_2:
            st.button(".", key="dpoint", on_click=append_calc_buffer, args=(".",), width="stretch")
        with d_r4_3:
            st.button("180°", key="d180", on_click=lambda: st.session_state.update({"calc_buffer": "180"}), width="stretch")
        with d_r4_4:
            st.button("= Apply", key="dapply", on_click=apply_calc_buffer, type="primary", width="stretch")

# -----------------------------------------------------------------------------
# Educational Quaternion Inspector (Comprehensive Math Pipeline)
# -----------------------------------------------------------------------------
st.divider()
st.header("🎓 Educational Quaternion Inspector")
st.caption("Complete 5-step mathematical pipeline showing how 3D transformations are encoded, chained, rotated, and projected onto 2D canvas pixels.")

col_e1, col_e2 = st.columns(2)

with col_e1:
    with st.container(border=True):
        st.subheader("1. Angle to Unit Quaternion Encoding")
        step_rad = math.radians(st.session_state.step_deg)
        half_r = step_rad / 2
        st.write(
            f"Keypad step angle **$\\theta = {st.session_state.step_deg}^\\circ$** is converted to radians "
            f"$\\theta_{{\\text{{rad}}}} = {step_rad:.4f}$ rad.\n\n"
            "Each axis rotation is stored as a 4D unit quaternion using the half-angle formula:\n"
            "$$q = \\left[ \\cos\\left(\\frac{\\theta}{2}\\right), u_x \\sin\\left(\\frac{\\theta}{2}\\right), u_y \\sin\\left(\\frac{\\theta}{2}\\right), u_z \\sin\\left(\\frac{\\theta}{2}\\right) \\right]$$"
        )
        
        dq_x = [math.cos(half_r), math.sin(half_r), 0.0, 0.0]
        dq_y = [math.cos(half_r), 0.0, math.sin(half_r), 0.0]
        dq_z = [math.cos(half_r), 0.0, 0.0, math.sin(half_r)]
        
        st.write(f"• **$\\Delta q_x$ (Pitch $+{st.session_state.step_deg}^\\circ$):** `[{dq_x[0]:.4f}, {dq_x[1]:.4f}, 0.0, 0.0]`")
        st.write(f"• **$\\Delta q_y$ (Yaw $+{st.session_state.step_deg}^\\circ$):** `[{dq_y[0]:.4f}, 0.0, {dq_y[2]:.4f}, 0.0]`")
        st.write(f"• **$\\Delta q_z$ (Roll $+{st.session_state.step_deg}^\\circ$):** `[{dq_z[0]:.4f}, 0.0, 0.0, {dq_z[3]:.4f}]`")

    with st.container(border=True):
        st.subheader("3. Local vs Global Quaternion Accumulation")
        st.write(
            "**Why Order Matters in Quaternion Multiplication ($q_1 \\otimes q_2 \\neq q_2 \\otimes q_1$):**\n\n"
            "* **Local Body Frame ($Q_{{\\text{{new}}}} = Q_{{\\text{{current}}}} \\otimes \\Delta q$):**\n"
            "  Post-multiplying applies incremental rotation relative to the cube's *own* local axes ($X_b, Y_b, Z_b$). "
            "  When clicking Roll Z, it spins in-place around $Z_b$, preserving existing tilt!\n\n"
            "* **Global World Frame ($Q_{{\\text{{new}}}} = \\Delta q \\otimes Q_{{\\text{{current}}}}$):**\n"
            "  Pre-multiplying applies rotation relative to fixed laboratory space ($X_w, Y_w, Z_w$)."
        )

    with st.container(border=True):
        st.subheader("5. 3D to 2D Orthographic Screen Projection")
        st.write(
            "To draw the rotated 3D vector $v' = (x', y', z')$ onto the 2D SVG canvas pixel grid:\n\n"
            "$$\\begin{aligned}"
            "x_{{\\text{{pixel}}}} &= x' \\cdot \\text{{scale}} + c_x \\\\"
            "y_{{\\text{{pixel}}}} &= -y' \\cdot \\text{{scale}} + c_y"
            "\\end{aligned}$$\n\n"
            "• **Scale:** $85.0$ pixels per 3D unit distance.\n"
            "• **Canvas Center Origin:** $(c_x, c_y) = (250.0, 150.0)$ pixels.\n"
            "• **Vertical Inversion:** $-y'$ flips vertical direction because SVG pixel coordinates measure downwards from top screen edge ($y=0$).\n\n"
            "**Why Distortion-Free?** Scaling is uniform (no depth division by $z'$), so opposite faces remain $100\\%$ parallel and equal in size at all angles."
        )

with col_e2:
    with st.container(border=True):
        st.subheader("2. Hamilton Product & Active Orientation State")
        st.write(
            "Quaternion multiplication chains rotations without matrix inversion or gimbal lock:\n"
            "$$\\begin{aligned}"
            "w &= w_1 w_2 - x_1 x_2 - y_1 y_2 - z_1 z_2 \\\\"
            "x &= w_1 x_2 + x_1 w_2 + y_1 z_2 - z_1 y_2 \\\\"
            "y &= w_1 y_2 - x_1 z_2 + y_1 w_2 + z_1 x_2 \\\\"
            "z &= w_1 z_2 + x_1 y_2 - y_1 x_2 + z_1 w_2"
            "\\end{aligned}$$"
        )
        st.write("**Current Active 4D Quaternion $Q$:**")
        st.code(
            f"Q = [{q_final[0]:+.4f}, {q_final[1]:+.4f}, {q_final[2]:+.4f}, {q_final[3]:+.4f}]",
            language="text"
        )

    with st.container(border=True):
        st.subheader("4. 3D Vector Sandwich Conjugation")
        st.write(
            "A 3D vertex $v = (x, y, z)$ is embedded as a pure quaternion $p = (0, x, y, z)$ and rotated via sandwich conjugation:\n"
            "$$p' = Q \\cdot (0, v) \\cdot Q^*$$\n"
        )
        sample_v = CUBE_VERTICES[6]  # [1, 1, 1]
        transformed_v = rotate_vertex(sample_v, q_final)
        st.write(f"**Sample Node `[1, 1, 1]` $\\rightarrow$ Rotated 3D Vector $v'$:**")
        st.code(
            f"v' = [{transformed_v[0]:+.4f}, {transformed_v[1]:+.4f}, {transformed_v[2]:+.4f}]",
            language="text"
        )

    with st.container(border=True):
        st.subheader("📐 Live Projection Calculation Example")
        px = transformed_v[0] * SCALE + CX
        py = -transformed_v[1] * SCALE + CY
        st.write(
            "**Worked Calculation for Sample Node `[1, 1, 1]`:**\n\n"
            f"1. **Rotated 3D Point $v'$:** $({transformed_v[0]:+.3f}, {transformed_v[1]:+.3f}, {transformed_v[2]:+.3f})$\n"
            f"2. **Calculate $x_{{\\text{{pixel}}}}$:** $({transformed_v[0]:+.3f} \\times 85.0) + 250.0 = \\mathbf{{{px:.1f}\\text{{ px}}}}$\n"
            f"3. **Calculate $y_{{\\text{{pixel}}}}$:** $(-({transformed_v[1]:+.3f}) \\times 85.0) + 150.0 = \\mathbf{{{py:.1f}\\text{{ px}}}}$\n\n"
            f"**Final Canvas SVG Render Point:** `({px:.1f}, {py:.1f})`"
        )
