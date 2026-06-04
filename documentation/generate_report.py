"""
LSPU Evacuation Simulation - Final Presentation Document Generator
Generates LSPU_Final_Presentation.docx using python-docx
"""

import os
from docx import Document
from docx.shared import Inches, Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import copy

# ─────────────────────────────────────────────
# PATHS
# ─────────────────────────────────────────────
BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
SNAP_DIR   = os.path.join(BASE_DIR, "..", "models", "snapshots")
WORKFLOW   = os.path.join(BASE_DIR, "diagram_workflow.png")
BEHAVIOR   = os.path.join(BASE_DIR, "diagram_behavior_tree.png")
SNAPSHOT_1 = os.path.join(SNAP_DIR, "LSPUEvacuation_model_display_CampusMap_cycle_0_time_1780560368547.png")
SNAPSHOT_2 = os.path.join(SNAP_DIR, "LSPUEvacuation_model_display_CampusMap_cycle_0_time_1780560369257.png")
OUTPUT     = os.path.join(BASE_DIR, "LSPU_Final_Presentation.docx")

# ─────────────────────────────────────────────
# HELPER FUNCTIONS
# ─────────────────────────────────────────────

def set_page_size_a4(doc):
    """Set document page to A4 with standard margins."""
    from docx.shared import Cm
    section = doc.sections[0]
    section.page_width  = Cm(21.0)
    section.page_height = Cm(29.7)
    section.left_margin   = Cm(2.54)
    section.right_margin  = Cm(2.54)
    section.top_margin    = Cm(2.54)
    section.bottom_margin = Cm(2.54)

def add_horizontal_rule(doc):
    """Add a thin horizontal rule."""
    p = doc.add_paragraph()
    pPr = p._p.get_or_add_pPr()
    pBdr = OxmlElement('w:pBdr')
    bottom = OxmlElement('w:bottom')
    bottom.set(qn('w:val'), 'single')
    bottom.set(qn('w:sz'), '6')
    bottom.set(qn('w:space'), '1')
    bottom.set(qn('w:color'), '4A90D9')
    pBdr.append(bottom)
    pPr.append(pBdr)
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after  = Pt(6)

def add_cover_page(doc):
    """Generate a styled cover page."""
    # University name
    univ = doc.add_paragraph()
    univ.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = univ.add_run("LAGUNA STATE POLYTECHNIC UNIVERSITY")
    run.bold = True
    run.font.size = Pt(14)
    run.font.color.rgb = RGBColor(0x1A, 0x56, 0xDB)  # blue

    dept = doc.add_paragraph()
    dept.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = dept.add_run("College of Computer Studies")
    run.font.size = Pt(12)

    doc.add_paragraph()  # spacer

    # Title block
    title_p = doc.add_paragraph()
    title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = title_p.add_run("Basic Campus Evacuation Routing Simulation\nUsing GIS Data")
    run.bold = True
    run.font.size = Pt(22)
    run.font.color.rgb = RGBColor(0x1A, 0x56, 0xDB)

    doc.add_paragraph()

    subtitle_p = doc.add_paragraph()
    subtitle_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = subtitle_p.add_run("Final Project Presentation Report")
    run.italic = True
    run.font.size = Pt(13)

    add_horizontal_rule(doc)
    doc.add_paragraph()

    # Info table
    tbl = doc.add_table(rows=4, cols=2)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.style = 'Table Grid'

    labels = ["Target Campus", "Simulation Platform", "Project Team", "Academic Year"]
    values = [
        "Laguna State Polytechnic University – Main Campus",
        "GAMA Platform (Agent-Based Modeling)",
        "Dheyn Michael Orlanda\nEulyn Vincee Ann Sto. Domingo",
        "2025 – 2026"
    ]

    for i, (lbl, val) in enumerate(zip(labels, values)):
        row = tbl.rows[i]
        # Label cell
        lc = row.cells[0]
        lc.text = lbl
        for para in lc.paragraphs:
            for run in para.runs:
                run.bold = True
                run.font.size = Pt(10)
        # Value cell
        vc = row.cells[1]
        vc.text = val
        for para in vc.paragraphs:
            for run in para.runs:
                run.font.size = Pt(10)

    doc.add_page_break()

def add_section_heading(doc, text, level=1):
    """Add a styled section heading."""
    h = doc.add_heading(text, level=level)
    h.alignment = WD_ALIGN_PARAGRAPH.LEFT
    for run in h.runs:
        if level == 1:
            run.font.color.rgb = RGBColor(0x1A, 0x56, 0xDB)
            run.font.size = Pt(14)
        else:
            run.font.color.rgb = RGBColor(0x1E, 0x40, 0x80)
            run.font.size = Pt(12)
    return h

def add_body(doc, text):
    """Add a justified body paragraph."""
    p = doc.add_paragraph(text)
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.space_after = Pt(8)
    for run in p.runs:
        run.font.size = Pt(11)
    return p

def add_bullet(doc, text, level=0):
    """Add a bullet list item."""
    p = doc.add_paragraph(text, style='List Bullet')
    p.paragraph_format.left_indent = Cm(level * 0.5)
    for run in p.runs:
        run.font.size = Pt(11)
    return p

def embed_image(doc, path, caption, width=Inches(5.5)):
    """Embed an image with a caption if the file exists."""
    if os.path.exists(path):
        try:
            doc.add_picture(path, width=width)
            # Center the image paragraph
            last_para = doc.paragraphs[-1]
            last_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        except Exception as e:
            doc.add_paragraph(f"[Image could not be embedded: {e}]")
    else:
        doc.add_paragraph(f"[Image not found: {os.path.basename(path)}]")

    cap = doc.add_paragraph(caption)
    cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cap.paragraph_format.space_after = Pt(12)
    for run in cap.runs:
        run.italic = True
        run.font.size = Pt(9)
        run.font.color.rgb = RGBColor(0x55, 0x55, 0x55)

# ─────────────────────────────────────────────
# DOCUMENT ASSEMBLY
# ─────────────────────────────────────────────

doc = Document()
set_page_size_a4(doc)

# Default style tweaks
style = doc.styles['Normal']
style.font.name = 'Calibri'
style.font.size = Pt(11)

# ── COVER PAGE ──────────────────────────────
add_cover_page(doc)

# ── 1. PROJECT OBJECTIVE ────────────────────
add_section_heading(doc, "1. Project Objective")
add_body(doc,
    "This project aims to design, implement, and evaluate a basic campus evacuation routing "
    "simulation for Laguna State Polytechnic University (LSPU) Main Campus using real GIS data "
    "derived from OpenStreetMap (OSM). The primary objectives are:"
)
objectives = [
    "To simulate realistic emergency evacuation scenarios by leveraging actual campus road "
    "networks, building footprints, and spatial topology.",
    "To evaluate the efficiency of dual-gate evacuation routing by routing student agents along "
    "real road paths to two designated exit points.",
    "To model organic fire spread dynamics including radial growth and probabilistic spark "
    "jumping, and to measure their impact on student casualty rates.",
    "To simulate emergency responder (firefighter) intervention and assess their effectiveness "
    "in containing fire spread and reducing casualties.",
    "To provide real-time analytical insights through live time-series charts tracking the "
    "evolving status of evacuating, safe, and casualty populations throughout the simulation.",
    "To apply core Agent-Based Modeling (ABM) concepts—including autonomous agent behavior, "
    "spatial environments, and emergent system dynamics—to a real-world safety problem."
]
for obj in objectives:
    add_bullet(doc, obj)

add_horizontal_rule(doc)

# ── 2. SIMULATION ENVIRONMENT ────────────────
add_section_heading(doc, "2. Simulation Environment")
add_body(doc,
    "The simulation environment is built upon authentic GIS data extracted from OpenStreetMap "
    "(OSM) for the LSPU Main Campus. The map file, LSPU_MAP.osm, is loaded directly into "
    "the GAMA Platform as a file object, and its envelope defines the entire world boundary "
    "of the simulation space. This approach ensures that all spatial interactions—pathfinding, "
    "building placement, and gate positioning—are grounded in real-world geography."
)
add_section_heading(doc, "2.1 Environment Layers", level=2)
layers = [
    ("Buildings", "Parsed from OSM building polygon tags. Structures that have a null or "
        "non-building type tag are filtered out immediately at initialization. Buildings "
        "serve as spawn locations for student agents and as obstacles in the environment. "
        "They are rendered in dark gray (#darkgray) with black borders."),
    ("Roads", "Extracted from OSM highway tags. Road segments form the basis of the road_network "
        "graph (as_edge_graph), which is the primary navigation layer used by both student "
        "and responder agents for GIS-based pathfinding. Roads are rendered in white to "
        "contrast against the dark background."),
    ("Gates", "Two evacuation gates are manually placed at strategic campus exit points and "
        "snapped to the nearest road node for path reachability. Gate 1 is positioned at "
        "coordinates approximating the Bottom evacuation zone {600.0, 900.0}, and Gate 2 "
        "at the Top-Right zone {850.0, 200.0}. Both are rendered as lime green squares with "
        "a white 'GATE' label."),
]
for title, desc in layers:
    p = doc.add_paragraph()
    run = p.add_run(f"{title}: ")
    run.bold = True
    run.font.size = Pt(11)
    run2 = p.add_run(desc)
    run2.font.size = Pt(11)
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.space_after = Pt(6)

add_horizontal_rule(doc)

# ── 3. AGENT BEHAVIORS ────────────────────────
add_section_heading(doc, "3. Agent Behaviors")

add_section_heading(doc, "3.1 Fire Agent", level=2)
add_body(doc,
    "The fire species is the primary environmental hazard in the simulation. It operates "
    "through two simultaneous reflexes that create organic, emergent fire spread behavior:"
)
add_bullet(doc, "Organic Radial Growth (spread reflex): Every simulation tick, each fire "
    "agent increases its fire_radius by a random value between 0.0 and 0.1 meters "
    "(fire_radius <- fire_radius + rnd(0.0, 0.1)). This continuous, stochastic growth "
    "simulates the natural intensification of a fire over time.")
add_bullet(doc, "Probabilistic Spark Jumping (jump reflex): On each tick, there is a 4% "
    "probability (flip(0.04)) that a fire agent spawns a new child fire within a 15-meter "
    "radius (rnd(-15.0, 15.0) offset). This jump is suppressed once the total fire population "
    "reaches 30 sparks to prevent simulation overload. The child fire starts with a radius "
    "of 1.0 meter, mimicking the behavior of flying embers.")
add_bullet(doc, "Proportional Spawning (initialization): The initial fire origin is "
    "constrained to buildings located within the inner 10%–60% bounds of the campus map "
    "in both X and Y axes. This proportional, randomized spawning ensures the fire starts "
    "in a realistic central campus location rather than on edge boundaries, and introduces "
    "a stochastic element to each simulation run.")
add_bullet(doc, "Visual Flicker Effect: The fire is drawn as three concentric circles with "
    "randomized orange opacity (rgb(255, rnd(80,120), 0, rnd(100,180))), a red mid-layer, "
    "and a yellow core. This opacity randomization creates a convincing visual flicker on "
    "each rendered frame.")

add_section_heading(doc, "3.2 Student Agent", level=2)
add_body(doc,
    "The student species represents 150 individuals, each spawned at a random location "
    "inside a campus building. Students are assigned to one of two evacuation gates using "
    "a forced 50/50 even-odd index split (gate[0] for even-indexed students, gate[1] for "
    "odd-indexed), ensuring exactly 75 students route to each gate. The species uses the "
    "moving skill and operates through two concurrent reflexes:"
)
add_bullet(doc, "evacuate reflex (active when not safe and not casualty): The student "
    "navigates toward its assigned gate using the road_network graph at a randomized speed "
    "between 0.5 and 1.0 map units per tick (do goto target: my_gate.location on: road_network "
    "speed: rnd(0.5, 1.0)). When the distance to the gate falls within 2.5 meters, the "
    "student is marked as safe (is_safe = true) and the global count_safe counter increments. "
    "The GAMA goto primitive automatically uses Dijkstra's shortest path on the road graph, "
    "with an implicit off-road Euclidean distance fallback if the destination is not "
    "reachable through the graph.")
add_bullet(doc, "check_fire reflex (active when not safe and not casualty): Each tick, the "
    "student identifies the nearest active fire agent and checks if it is within that fire's "
    "current fire_radius. If so, the student is immediately marked as a casualty "
    "(is_casualty = true) and count_casualties increments. This per-spark radius check "
    "means students are only at risk if caught directly within a burning area.")

add_section_heading(doc, "3.3 Responder Agent (Firefighter)", level=2)
add_body(doc,
    "Five responder agents are spawned at the gate locations at simulation start. They "
    "operate via a single fight_fire reflex that implements a seek-and-suppress strategy:"
)
add_bullet(doc, "Target Acquisition: If the responder has no target (or its current target "
    "has been extinguished), it queries all active fire agents and selects the one closest "
    "to its current location (fire closest_to(self)).")
add_bullet(doc, "Pursuit: The responder navigates toward its target fire via the road_network "
    "at a speed of 1.5 map units per tick—50% faster than the average student.")
add_bullet(doc, "Suppression: Once within 15 meters of the target fire, the responder "
    "remotely shrinks the fire's radius by 0.2 meters per tick (fire_radius <- fire_radius - 0.2). "
    "If the radius drops to 0.5 meters or below, the fire agent is killed (do die), "
    "completely extinguishing that spark.")
add_bullet(doc, "Water Hose Visualization: When actively suppressing a fire within range, "
    "a cyan line is drawn from the responder's location to the fire's location, simulating "
    "a visual water hose effect.")

add_horizontal_rule(doc)

# ── 4. VISUALIZATION TECHNIQUES ──────────────
add_section_heading(doc, "4. Visualization Techniques")
add_body(doc,
    "The simulation renders two simultaneous 2D display windows within the GAMA experiment "
    "GUI, providing both spatial situational awareness and quantitative analytical feedback."
)
add_section_heading(doc, "4.1 Campus Map Display (CampusMap)", level=2)
add_body(doc,
    "The primary display renders the full campus environment on a dark (#222222) background "
    "to maximize contrast. The following color-coded visual conventions are used across "
    "all agent species:"
)
vis_items = [
    ("Dark Gray Buildings & White Roads", "GIS-derived campus infrastructure rendered from OSM data."),
    ("Lime Green Squares (Gates)", "The two evacuation exit points with 'GATE' labels."),
    ("Cyan Circle (Student – Evacuating)", "A student actively navigating toward its assigned gate."),
    ("Lime Green Circle (Student – Safe)", "A student who has successfully reached the gate exit."),
    ("Black Cross / Plus Symbol (Student – Casualty)", "A student who was caught within a fire's radius."),
    ("Layered Orange/Red/Yellow Circles (Fire)", "Each fire spark rendered with a flickering three-layer effect."),
    ("Blue Square (Responder)", "A firefighter agent navigating toward or suppressing a fire."),
    ("Cyan Line (Water Hose)", "A dynamic line drawn from a responder to its target fire when within 15m range."),
]
for title, desc in vis_items:
    p = doc.add_paragraph()
    run = p.add_run(f"• {title}: ")
    run.bold = True
    run.font.size = Pt(11)
    run2 = p.add_run(desc)
    run2.font.size = Pt(11)
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.space_after = Pt(4)

add_section_heading(doc, "4.2 System Architecture Workflow Diagram", level=2)
embed_image(doc, WORKFLOW, "Figure 1: System Architecture Workflow – Initialization, Simulation Loop, and Analytics Output", width=Inches(5.5))

add_section_heading(doc, "4.3 Student Agent Behavior Tree", level=2)
embed_image(doc, BEHAVIOR, "Figure 2: Student Agent Behavior Tree – Decision Logic per Simulation Tick", width=Inches(4.0))

add_horizontal_rule(doc)

# ── 5. ANALYTICS AND MONITORING TOOLS ────────
add_section_heading(doc, "5. Analytics and Monitoring Tools")
add_body(doc,
    "A dedicated Analytics display window renders a live time-series chart titled "
    "'Live Evacuation & Casualty Status'. This chart plots three dynamically updating "
    "data series over simulation time (by cycle number) on a dark background (#333333):"
)
analytics = [
    ("Evacuating – Cyan line", "Tracks count_evacuating, computed dynamically as "
        "total_students - count_safe - count_casualties. This value starts at 150 and "
        "monotonically decreases as students either reach safety or become casualties."),
    ("Safe – Lime Green line", "Tracks count_safe, incrementing each time a student "
        "reaches within 2.5m of its assigned gate. This curve rises toward 150 as the "
        "evacuation progresses successfully."),
    ("Casualties – Red line", "Tracks count_casualties, incrementing each time a student "
        "is caught within a fire's radius. A steep rise in this curve indicates rapid "
        "fire spread or inadequate responder coverage."),
]
for title, desc in analytics:
    p = doc.add_paragraph()
    run = p.add_run(f"• {title}: ")
    run.bold = True
    run.font.size = Pt(11)
    run2 = p.add_run(desc)
    run2.font.size = Pt(11)
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.space_after = Pt(6)

add_body(doc,
    "The chart provides researchers with an immediate visual signal of evacuation efficiency. "
    "A healthy simulation run shows a rapid rise in the Safe (lime) line with minimal growth "
    "in the Casualties (red) line, indicating that students are successfully evacuating "
    "before the fire expands to engulf them."
)

add_horizontal_rule(doc)

# ── 6. SIMULATION RESULTS ────────────────────
add_section_heading(doc, "6. Simulation Results")
add_body(doc,
    "The following screenshots were captured at Cycle 0 during the simulation initialization "
    "phase, providing the initial state of the LSPU campus evacuation scenario."
)

add_section_heading(doc, "6.1 Campus Map – Initial State (Cycle 0)", level=2)
embed_image(doc, SNAPSHOT_1, "Figure 3: LSPUEvacuation – CampusMap at Cycle 0 (Run 1) – Initial deployment of student agents (red dots) across campus buildings", width=Inches(4.5))
add_body(doc,
    "As seen in Figure 3, at the simulation's initial state (Cycle 0), all 150 student "
    "agents appear as red markers distributed across the campus building footprints. The "
    "dark gray building outlines and white road network are clearly visible, confirming "
    "the successful parsing and rendering of the LSPU_MAP.osm GIS data. No students "
    "have yet begun evacuating, and the fire origin has been placed in the inner campus zone."
)

add_section_heading(doc, "6.2 Campus Map – Second Run Initialization (Cycle 0)", level=2)
embed_image(doc, SNAPSHOT_2, "Figure 4: LSPUEvacuation – CampusMap at Cycle 0 (Run 2) – Stochastic re-spawning demonstrates randomized initial student placement", width=Inches(4.5))
add_body(doc,
    "Figure 4 demonstrates the stochastic nature of the simulation's initialization. "
    "In a second independent run at Cycle 0, student agents are spawned at different "
    "building locations compared to Run 1, confirming that the any_location_in(one_of(building)) "
    "initialization logic produces unique spatial configurations per run. This variability "
    "is essential for ABM validity, ensuring that results are not artifacts of a single "
    "deterministic starting condition. The consistent road network and building layout "
    "confirm that the GIS environment layer loads deterministically while the agent "
    "population is stochastically distributed."
)

add_body(doc,
    "Both snapshots confirm that the simulation environment correctly initializes "
    "the campus map, student agents, and evacuation infrastructure. The dual-gate "
    "evacuation routing, fire spread mechanics, and responder behavior emerge "
    "organically once the simulation advances beyond Cycle 0."
)

add_horizontal_rule(doc)

# ── 7. FUTURE IMPROVEMENTS ────────────────────
add_section_heading(doc, "7. Future Improvements")
add_body(doc,
    "While the current simulation successfully demonstrates core evacuation routing and "
    "fire suppression dynamics, several enhancements can improve its realism and "
    "analytical depth:"
)
improvements = [
    ("Crowd Congestion Mechanics", "Introduce agent-to-agent collision avoidance and density-based "
        "speed reduction. As students converge on the two gates, bottleneck effects should "
        "slow movement, more accurately modeling real crowd dynamics."),
    ("Varied Student Mobility Profiles", "Differentiate student agents by walking speed, mobility "
        "impairment, or panic level. Adding a distribution of speeds (e.g., elderly, disabled, "
        "or children) would produce more realistic casualty and evacuation time distributions."),
    ("Multiple Simultaneous Fire Origins", "Allow more than one fire to ignite simultaneously "
        "or in sequence, simulating compound emergency scenarios. This would test the limits "
        "of the 5-responder team and provide richer casualty data."),
    ("Dynamic Gate Capacity Limits", "Implement gate throughput limits to model bottlenecking "
        "at exit points, forcing agents to re-route if their primary gate becomes overloaded."),
    ("Responder Communication & Coordination", "Enable responder agents to share target "
        "information so they do not all converge on the same fire spark, improving their "
        "collective efficiency in multi-fire scenarios."),
    ("Wind-Influenced Fire Spread", "Add directional wind vectors that bias the fire's "
        "spark-jumping probability in a dominant direction, creating more realistic "
        "asymmetric fire propagation patterns."),
    ("3D Visualization and Floor Plans", "Extend the simulation into a 3D environment "
        "using GAMA's OpenGL renderer to model multi-floor buildings and stairwell "
        "evacuation bottlenecks."),
    ("Integration with Real-Time Sensor Data", "Connect the simulation to IoT sensor "
        "streams (smoke detectors, occupancy sensors) to run the model as a real-time "
        "decision support tool during actual emergency events."),
]
for title, desc in improvements:
    p = doc.add_paragraph()
    run = p.add_run(f"• {title}: ")
    run.bold = True
    run.font.size = Pt(11)
    run2 = p.add_run(desc)
    run2.font.size = Pt(11)
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.space_after = Pt(6)

add_horizontal_rule(doc)

# ── 8. APPLICATION OF ABM CONCEPTS ────────────
add_section_heading(doc, "8. Application of Agent-Based Modeling Concepts")
add_body(doc,
    "This project is a direct application of foundational Agent-Based Modeling principles, "
    "demonstrating how complex system-level behavior emerges from simple, locally-defined "
    "agent rules:"
)

add_section_heading(doc, "8.1 Autonomous Decision-Making", level=2)
add_body(doc,
    "Each agent species operates independently based on its own local state and perception. "
    "Student agents do not receive centralized coordination commands; they individually "
    "check their distance to their gate and the nearest fire on every tick, making "
    "autonomous decisions to move, stop, or become a casualty. Responder agents "
    "independently scan for the nearest fire target and self-assign without a dispatcher. "
    "Fire agents autonomously grow and jump based on probabilistic rules. This decentralized "
    "architecture is the defining characteristic of ABM and would be impossible to replicate "
    "with a traditional equation-based model."
)

add_section_heading(doc, "8.2 Spatial Environments and GIS Integration", level=2)
add_body(doc,
    "The simulation environment is not an abstract grid but a spatially accurate "
    "representation of a real campus, loaded from OpenStreetMap GIS data. The use of "
    "as_edge_graph(road) converts the OSM road layer into a traversable navigation "
    "network, enabling agents to perform realistic graph-based pathfinding (Dijkstra's "
    "algorithm) along actual campus roads. The spatial constraint of fire spawning to "
    "the inner 10%–60% campus bounding zone demonstrates how geographic constraints "
    "can be embedded directly into agent initialization rules. This GIS-informed "
    "approach makes the simulation outputs directly applicable to real-world emergency "
    "planning for LSPU."
)

add_section_heading(doc, "8.3 Emergent Behavior and System-Level Dynamics", level=2)
add_body(doc,
    "The most powerful demonstration of ABM in this project is the emergence of "
    "unpredictable system-level outcomes from simple agent rules. No single agent "
    "controls the overall evacuation outcome; instead, the interplay of fire spread, "
    "student routing, and responder suppression creates complex, nonlinear dynamics:"
)
emergent = [
    "A fire that jumps toward a road corridor can cut off a student's shortest path, "
    "forcing the goto primitive's fallback logic and creating spontaneous bottlenecks.",
    "Five responders pursuing different fire sparks can simultaneously suppress three "
    "fires while two others grow unchecked, creating spatial asymmetry in the hazard zone.",
    "The 4% jump probability can, by chance, cause a rapid cascade of 30 sparks within "
    "a few ticks, overwhelming the responders and causing a sudden spike in casualties "
    "on the live analytics chart—an emergent 'flashpoint' event.",
    "The 50/50 gate split means that a fire positioned between the two gates acts as "
    "a natural barrier, creating differential casualty rates between the two student "
    "cohorts even though both groups follow identical individual rules.",
]
for item in emergent:
    add_bullet(doc, item)

add_body(doc,
    "These emergent dynamics validate the core ABM thesis: local rules governing "
    "individual agents produce global behavior that is qualitatively richer than "
    "the sum of its parts. The simulation demonstrates that campus evacuation safety "
    "is a genuinely complex adaptive system, where the specific spatial configuration "
    "of fire, students, roads, and responders produces unique outcomes in every run—"
    "mirroring the irreducible uncertainty of real emergency scenarios."
)

add_horizontal_rule(doc)

# ── REFERENCES ────────────────────────────────
add_section_heading(doc, "References")
refs = [
    "GAMA Platform Development Team. (2024). GAMA Platform Documentation – Agent-Based Spatial Simulation. https://gama-platform.org",
    "OpenStreetMap Contributors. (2024). LSPU Main Campus Map Data. https://www.openstreetmap.org",
    "Taillandier, P., et al. (2019). Building, composing and experimenting complex spatial models with the GAMA platform. GeoInformatica, 23(2), 299–322.",
    "Macal, C. M., & North, M. J. (2010). Tutorial on agent-based modelling and simulation. Journal of Simulation, 4(3), 151–162.",
    "Orlanda, D. M., & Sto. Domingo, E. V. A. (2026). Basic Campus Evacuation Routing Simulation Using GIS Data [GAML Source Code]. GitHub. https://github.com/Necookie/LSPU_EVACUATIONSIM_GAMA",
]
for ref in refs:
    p = doc.add_paragraph(ref, style='List Number')
    p.paragraph_format.space_after = Pt(4)
    for run in p.runs:
        run.font.size = Pt(10)

# ─────────────────────────────────────────────
# SAVE
# ─────────────────────────────────────────────
doc.save(OUTPUT)
print("Document saved successfully to:")
print(f"   {OUTPUT}")
