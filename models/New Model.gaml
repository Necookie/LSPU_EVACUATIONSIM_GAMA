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

        // 2. CREATE THE GATES (Manual Placement + Road Snapping)
        // Gate 1: Bottom Evacuation Zone 
        create gate number: 1 {
            point manual_target <- {600.0, 900.0}; 
            location <- (road closest_to manual_target).location; 
        }

        // Gate 2: Top-Right Evacuation Zone 
        create gate number: 1 {
            point manual_target <- {850.0, 200.0}; 
            location <- (road closest_to manual_target).location; 
        }

        // 3. CREATE THE FIRE ORIGIN
        create fire number: 1 {
            location <- any_location_in(one_of(building));
            fire_radius <- 3.0; // Start small
        }

        // 4. CREATE STUDENTS (Forced 50/50 Split)
        create student number: total_students {
            location <- any_location_in(one_of(building));
        }
        
        int i <- 0;
        ask student {
            if (even(i)) { my_gate <- gate[0]; } 
            else { my_gate <- gate[1]; }
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
        draw "GATE" color: #white size: 12 at: location + {0, 20}; 
    }
}

// ==========================================
// DYNAMIC SPECIES (Fire, Students, Responders)
// ==========================================
species fire {
    float fire_radius;
    
    // 1. Organic Growth: Grows slowly and randomly instead of a perfect line
    reflex spread {
        fire_radius <- fire_radius + rnd(0.0, 0.1); 
    }
    
    // 2. Jumping Sparks: Small chance to spawn a new fire nearby (max 30 fires to prevent lag)
    reflex jump when: flip(0.04) and length(fire) < 30 {
        create fire number: 1 {
            // Spawn anywhere within 15 meters of the parent fire
            location <- myself.location + {rnd(-15.0, 15.0), rnd(-15.0, 15.0)};
            fire_radius <- 1.0;
        }
    }
    
    aspect default {
        // Randomly alter the opacity of the orange aura to make it "flicker"
        draw circle(fire_radius) color: rgb(255, rnd(80, 120), 0, rnd(100, 180)); 
        draw circle(fire_radius * 0.7) color: #red;            
        draw circle(fire_radius * 0.4) color: #yellow;         
    }
}

species student skills: [moving] {
    gate my_gate;
    bool is_safe <- false;
    bool is_casualty <- false;

    reflex evacuate when: !is_safe and !is_casualty {
        if (distance_to(self, my_gate.location) <= 2.5) {
            is_safe <- true;
            count_safe <- count_safe + 1;
        } else {
            do goto target: my_gate.location on: road_network speed: rnd(0.5, 1.0); 
        }
    }

    // UPDATED: Now checks distance to the *closest* fire spark, not just the original one
    reflex check_fire when: !is_safe and !is_casualty {
        if (length(fire) > 0) {
            fire nearest_fire <- fire closest_to(self);
            if (nearest_fire != nil and distance_to(self, nearest_fire) <= nearest_fire.fire_radius) {
                is_casualty <- true;
                count_casualties <- count_casualties + 1;
            }
        }
    }

    aspect default {
        if (is_safe) {
            draw circle(3) color: #lime; 
        } else if (is_casualty) {
            draw cross(5, 2) color: #black; 
        } else {
            draw circle(3) color: #cyan; 
        }
    }
}

species responder skills: [moving] {
    fire target_fire; // The specific spark this firetruck is hunting

    reflex fight_fire {
        // If we don't have a target, or our target was put out, find a new one!
        if (target_fire = nil or dead(target_fire)) {
            if (length(fire) > 0) {
                target_fire <- fire closest_to(self);
            }
        }
        
        // If there is still a fire to fight
        if (target_fire != nil and !dead(target_fire)) {
            // Drive towards it
            do goto target: target_fire on: road_network speed: 1.5; 
            
            // If within hose range (15 meters), extinguish it!
            if (distance_to(self, target_fire) <= 15.0) {
                ask target_fire {
                    fire_radius <- fire_radius - 0.2; // Shrink the fire
                    if (fire_radius <= 0.5) {
                        do die; // Fire is completely put out
                    }
                }
            }
        }
    }

    aspect default {
        draw square(6) color: #blue border: #white; 
        
        // VISUAL TRICK: Draw a water hose line if we are actively putting out a fire!
        if (target_fire != nil and !dead(target_fire) and distance_to(self, target_fire) <= 15.0) {
            draw line([location, target_fire.location]) color: #cyan width: 2;
        }
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
                data "Casualties (Black)" value: count_casualties color: #red; 
            }
        }
    }
}