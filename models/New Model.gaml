model LSPUEvacuationFire

global {
    // 1. ENVIRONMENT SETUP
    file map_file <- file("../includes/LSPU_MAP.osm");
    geometry shape <- envelope(map_file);
    graph road_network;

    // Detailed Analytics Variables
    int total_students <- 150;
    int count_safe <- 0;
    int count_casualties <- 0;
    
    // Dynamic variable that auto-updates
    int count_evacuating -> {total_students - count_safe - count_casualties};

    init {
        // Generate Map
        create building from: map_file with: [type::string(read("building"))] {
            if (type = nil or type = "no") { do die; }
        }
        create road from: map_file with: [highway_type::string(read("highway"))] {
            if (highway_type = nil) { do die; }
        }
        road_network <- as_edge_graph(road);

        // =========================================================
        // 2. CREATE THE GATES (Manual Placement + Road Snapping)
        // =========================================================
        // NOTE: If these are slightly off, pause the simulation, 
        // point your mouse where you want them, read the {X, Y} in 
        // the bottom left of your screen, and type them here!
        
        // Gate 1: Bottom Evacuation Zone (gate[0])
        create gate number: 1 {
            point manual_target <- {600.0, 900.0}; 
            // Snaps exactly to the nearest street so pathfinding always works
            location <- (road closest_to manual_target).location; 
        }

        // Gate 2: Top-Right Evacuation Zone (gate[1])
        create gate number: 1 {
            point manual_target <- {850.0, 200.0}; 
            location <- (road closest_to manual_target).location; 
        }

        // 3. CREATE THE FIRE ORIGIN
        create fire number: 1 {
            location <- any_location_in(one_of(building));
        }

        // =========================================================
        // 4. CREATE STUDENTS (Forced 50/50 Split)
        // =========================================================
        create student number: total_students {
            location <- any_location_in(one_of(building));
        }
        
        // Explicitly divide students evenly between the two gates
        int i <- 0;
        ask student {
            if (even(i)) {
                my_gate <- gate[0]; // Exactly half go to Gate 1 (Bottom)
            } else {
                my_gate <- gate[1]; // Exactly half go to Gate 2 (Top-Right)
            }
            i <- i + 1;
        }

        // 5. CREATE RESPONDERS (Firefighters)
        create responder number: 5 {
            location <- any_location_in(one_of(gate)); // Spawn at the gates
        }
    }
}

// ==========================================
// ENVIRONMENT SPECIES
// ==========================================
species building {
    string type;
    aspect default { draw shape color: #darkgray border: #black; }
}

species road {
    string highway_type;
    aspect default { draw shape color: #white; }
}

species gate {
    aspect default { 
        draw square(25) color: #lime border: #white; 
        draw "GATE" color: #white size: 12 at: location + {0, 20}; // Label the gates
    }
}

// ==========================================
// DYNAMIC SPECIES (Fire, Students, Responders)
// ==========================================
species fire {
    float fire_radius <- 5.0;
    
    // Fire expands every simulation tick
    reflex spread {
        fire_radius <- fire_radius + 0.2; 
    }
    
    aspect default {
        // Layered circles for an animated/realistic fire effect
        draw circle(fire_radius) color: rgb(255, 100, 0, 150); // Outer orange aura
        draw circle(fire_radius * 0.7) color: #red;            // Inner red flame
        draw circle(fire_radius * 0.4) color: #yellow;         // Hot core
    }
}

species student skills: [moving] {
    gate my_gate;
    bool is_safe <- false;
    bool is_casualty <- false;

    // Behavior 1: Run to the gate
    reflex evacuate when: !is_safe and !is_casualty {
        
        if (distance_to(self, my_gate.location) <= 2.5) {
            is_safe <- true;
            count_safe <- count_safe + 1;
        } else {
            do goto target: my_gate.location on: road_network speed: rnd(0.5, 1.0); 
        }
    }

    // Behavior 2: Die if the fire catches them
    reflex check_fire when: !is_safe and !is_casualty {
        fire current_fire <- first(fire);
        
        if (distance_to(self, current_fire) <= current_fire.fire_radius) {
            is_casualty <- true;
            count_casualties <- count_casualties + 1;
        }
    }

    aspect default {
        if (is_safe) {
            draw circle(3) color: #lime; // Safe
        } else if (is_casualty) {
            draw cross(5, 2) color: #black; // Casualty marker
        } else {
            draw circle(3) color: #cyan; // Evacuating civilians
        }
    }
}

species responder skills: [moving] {
    // Behavior: Drive directly to the fire
    reflex respond {
        do goto target: first(fire) on: road_network speed: 1.5; 
    }

    aspect default {
        draw square(6) color: #blue border: #white; // Blue units for responders
    }
}

// ==========================================
// DETAILED ANALYTICS OUTPUT
// ==========================================
experiment EvacuationSim type: gui {
    output {
        display CampusMap type: 2d background: rgb("#222222") {
            species building aspect: default;
            species road aspect: default;
            species gate aspect: default;
            species fire aspect: default;
            species student aspect: default;
            species responder aspect: default;
        }
        
        display Analytics type: 2d {
            chart "Live Evacuation & Casualty Status" type: series background: rgb("#333333") color: #white {
                data "Evacuating (Cyan)" value: count_evacuating color: #cyan;
                data "Safe (Lime)" value: count_safe color: #lime;
                data "Casualties (Black)" value: count_casualties color: #red; // Red line for casualty trend
            }
        }
    }
}