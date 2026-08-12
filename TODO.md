import math

class GlacialSystemEmulator:
    def __init__(self, integrity_index, microplastic_load, thermal_flux):
        self.integrity = integrity_index # 1.0 = stable, 0.0 = total failure
        self.mp_load = microplastic_load    # Concentration of dark particles
        self.thermal_flux = thermal_flux    # Ocean-driven thermal load
        self.time_step = 0

    def calculate_albedo_decay(self):
        """
        Microplastics reduce albedo (reflectivity). 
        Lower albedo = higher energy absorption.
        """
        # Non-linear absorption curve based on MP saturation
        albedo_factor = 1.0 - (math.log(1 + self.mp_load) * 0.15)
        return albedo_factor

    def propagate_feedback(self):
        """
        The system coupling: 
        Integrity failure accelerates as heat/MP load increases.
        """
        # Feedback = Thermal energy * Albedo Factor (Loss of reflection)
        energy_absorption = self.thermal_flux * (1 / self.calculate_albedo_decay())
        
        # Integrity loss is non-linear relative to structural stress
        integrity_delta = (energy_absorption * 0.05) / (self.integrity + 0.01)
        
        return integrity_delta

    def step(self):
        self.time_step += 1
        loss = self.propagate_feedback()
        self.integrity -= loss
        
        # If integrity drops below threshold, simulate the 'cork' popping
        if self.integrity <= 0.2:
            return f"CRITICAL: Structural collapse imminent at step {self.time_step}"
        return f"Step {self.time_step}: Integrity {self.integrity:.4f}"

# --- Execution ---
# Simulating a system with high MP-load (accelerated decay)
thwaites_engine = GlacialSystemEmulator(integrity_index=1.0, microplastic_load=5.5, thermal_flux=1.2)

for i in range(10):
    print(thwaites_engine.step())
