\
# gpp/patterns/data_locality.py
"""
Data Locality Pattern

Intent:
Optimize performance by arranging data in memory to maximize CPU cache utilization.
CPUs load data in cache lines. Accessing data that is close together in memory
(spatially local) or accessed sequentially (temporally local) can significantly
reduce memory latency.

One common technique to achieve data locality is "Structure of Arrays" (SoA),
as opposed to "Array of Structures" (AoS).

- AoS: [obj1, obj2, obj3] where obj = {x, y, z}
  Memory: [x1,y1,z1, x2,y2,z2, x3,y3,z3]
  If you process all 'x' components, you jump over 'y' and 'z'.

- SoA: positions_x = [x1,x2,x3], positions_y = [y1,y2,y3], positions_z = [z1,z2,z3]
  Memory for x: [x1,x2,x3] (contiguous)
  Processing all 'x' components means sequential memory access, which is cache-friendly.

This example demonstrates a ParticleSystem using SoA.
"""

class ParticleSystem:
    """
    Manages particles using a Structure of Arrays (SoA) approach
    to improve data locality when updating particles.
    """
    def __init__(self, max_particles: int):
        if not isinstance(max_particles, int) or max_particles <= 0:
            raise ValueError("max_particles must be a positive integer.")

        self.max_particles: int = max_particles
        self.num_active_particles: int = 0

        # Store components in separate arrays (SoA)
        self.positions_x: list[float] = [0.0] * max_particles
        self.positions_y: list[float] = [0.0] * max_particles
        self.velocities_x: list[float] = [0.0] * max_particles
        self.velocities_y: list[float] = [0.0] * max_particles
        self.active: list[bool] = [False] * max_particles

    def add_particle(self, pos_x: float, pos_y: float, vel_x: float, vel_y: float) -> int | None:
        """
        Adds a particle to the system.
        Tries to reuse an inactive slot first.
        Returns the particle ID (index) if successful, None otherwise.
        """
        for i in range(self.max_particles):
            if not self.active[i]:
                self._initialize_particle(i, pos_x, pos_y, vel_x, vel_y)
                return i
        
        # If no inactive slot is found and system is full
        # print("Particle system full. Cannot add new particle.") # Optional: logging
        return None

    def _initialize_particle(self, idx: int, pos_x: float, pos_y: float, vel_x: float, vel_y: float):
        """Helper to set particle data and mark as active."""
        self.positions_x[idx] = pos_x
        self.positions_y[idx] = pos_y
        self.velocities_x[idx] = vel_x
        self.velocities_y[idx] = vel_y
        self.active[idx] = True
        self.num_active_particles += 1

    def remove_particle(self, particle_id: int):
        """
        Marks a particle as inactive.
        The data remains in the arrays but will be ignored by updates
        and can be overwritten by a new particle.
        """
        if 0 <= particle_id < self.max_particles and self.active[particle_id]:
            self.active[particle_id] = False
            self.num_active_particles -= 1
        else:
            # Optional: raise error or log
            # print(f"Particle with id {particle_id} not found or already inactive.")
            pass


    def update(self, dt: float):
        """
        Update all active particles.
        Processing each component array contiguously demonstrates data locality.
        """
        if self.num_active_particles == 0:
            return

        # Update X positions
        # This loop accesses positions_x[i] and velocities_x[i]
        # If active[i] is true, these accesses are mostly sequential for active particles.
        for i in range(self.max_particles):
            if not self.active[i]:
                continue
            self.positions_x[i] += self.velocities_x[i] * dt

        # Update Y positions
        # Similarly, this loop accesses positions_y[i] and velocities_y[i]
        for i in range(self.max_particles):
            if not self.active[i]:
                continue
            self.positions_y[i] += self.velocities_y[i] * dt
            
    def get_particle_data(self, particle_id: int) -> dict | None:
        """
        Retrieves the data for a specific active particle.
        Returns a dictionary with particle data or None if inactive/invalid.
        """
        if 0 <= particle_id < self.max_particles and self.active[particle_id]:
            return {
                "pos_x": self.positions_x[particle_id],
                "pos_y": self.positions_y[particle_id],
                "vel_x": self.velocities_x[particle_id],
                "vel_y": self.velocities_y[particle_id],
            }
        return None

    def get_active_particles_data(self) -> list[dict]:
        """
        Retrieves data for all active particles.
        """
        particles_data = []
        for i in range(self.max_particles):
            if self.active[i]:
                particles_data.append({
                    "id": i,
                    "pos_x": self.positions_x[i],
                    "pos_y": self.positions_y[i],
                    "vel_x": self.velocities_x[i],
                    "vel_y": self.velocities_y[i],
                })
        return particles_data

# For conceptual comparison: Array of Structures (AoS)
# This would typically have worse cache performance for component-wise updates.
class ParticleAoS:
    def __init__(self, pos_x, pos_y, vel_x, vel_y):
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.vel_x = vel_x
        self.vel_y = vel_y

class ParticleSystemAoS:
    def __init__(self, max_particles):
        self.particles: list[ParticleAoS | None] = [None] * max_particles
        self.num_active_particles = 0

    def add_particle(self, pos_x, pos_y, vel_x, vel_y):
        for i in range(len(self.particles)):
            if self.particles[i] is None:
                self.particles[i] = ParticleAoS(pos_x, pos_y, vel_x, vel_y)
                self.num_active_particles +=1
                return i
        return None # System full

    def update(self, dt):
        # When updating, e.g., all x positions, memory access is scattered
        # p.pos_x and p.vel_x are not necessarily contiguous for different particles.
        for p_obj in self.particles:
            if p_obj:
                p_obj.pos_x += p_obj.vel_x * dt
        
        for p_obj in self.particles:
            if p_obj:
                p_obj.pos_y += p_obj.vel_y * dt
