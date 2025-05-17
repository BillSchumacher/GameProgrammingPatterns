# filepath: c:\\Users\\willi\\GameProgrammingPatterns\\tests\\test_data_locality_pattern.py
import unittest
from gamepp.patterns.data_locality import ParticleSystem


class TestDataLocalityPattern(unittest.TestCase):
    def test_initialization(self):
        ps = ParticleSystem(max_particles=100)
        self.assertEqual(ps.max_particles, 100)
        self.assertEqual(ps.num_active_particles, 0)
        self.assertEqual(len(ps.positions_x), 100)
        self.assertEqual(len(ps.active), 100)
        self.assertFalse(any(ps.active))

        with self.assertRaises(ValueError):
            ParticleSystem(max_particles=0)
        with self.assertRaises(ValueError):
            ParticleSystem(max_particles=-5)

    def test_add_particle(self):
        ps = ParticleSystem(max_particles=10)

        p_id1 = ps.add_particle(1.0, 2.0, 0.1, 0.2)
        self.assertEqual(p_id1, 0, "First particle should get ID 0")
        self.assertEqual(ps.num_active_particles, 1)
        self.assertTrue(ps.active[p_id1])
        self.assertEqual(ps.positions_x[p_id1], 1.0)
        self.assertEqual(ps.positions_y[p_id1], 2.0)
        self.assertEqual(ps.velocities_x[p_id1], 0.1)
        self.assertEqual(ps.velocities_y[p_id1], 0.2)

        p_id2 = ps.add_particle(3.0, 4.0, 0.3, 0.4)
        self.assertEqual(p_id2, 1, "Second particle should get ID 1")
        self.assertEqual(ps.num_active_particles, 2)
        self.assertTrue(ps.active[p_id2])
        self.assertEqual(ps.positions_x[p_id2], 3.0)

    def test_particle_system_full(self):
        ps = ParticleSystem(max_particles=1)
        p_id1 = ps.add_particle(1.0, 2.0, 0.1, 0.2)
        self.assertIsNotNone(p_id1)
        self.assertEqual(ps.num_active_particles, 1)

        # Try to add another particle when system is full
        full_id = ps.add_particle(3.0, 4.0, 0.3, 0.4)
        self.assertIsNone(full_id, "Should return None when system is full")
        self.assertEqual(ps.num_active_particles, 1, "Active count should not change")

    def test_update_particles(self):
        ps = ParticleSystem(max_particles=2)
        p_id1 = ps.add_particle(1.0, 10.0, 1.0, 0.5)  # pos_x, pos_y, vel_x, vel_y
        p_id2 = ps.add_particle(5.0, 20.0, -0.5, 1.0)
        dt = 2.0

        ps.update(dt)

        # Particle 1:
        # new_pos_x = 1.0 + (1.0 * 2.0) = 3.0
        # new_pos_y = 10.0 + (0.5 * 2.0) = 11.0
        data1 = ps.get_particle_data(p_id1)
        self.assertIsNotNone(data1)
        self.assertAlmostEqual(data1["pos_x"], 3.0)
        self.assertAlmostEqual(data1["pos_y"], 11.0)

        # Particle 2:
        # new_pos_x = 5.0 + (-0.5 * 2.0) = 4.0
        # new_pos_y = 20.0 + (1.0 * 2.0) = 22.0
        data2 = ps.get_particle_data(p_id2)
        self.assertIsNotNone(data2)
        self.assertAlmostEqual(data2["pos_x"], 4.0)
        self.assertAlmostEqual(data2["pos_y"], 22.0)

    def test_get_particle_data(self):
        ps = ParticleSystem(max_particles=5)
        p_id = ps.add_particle(1.1, 2.2, 0.3, 0.4)

        data = ps.get_particle_data(p_id)
        self.assertIsNotNone(data)
        self.assertAlmostEqual(data["pos_x"], 1.1)
        self.assertAlmostEqual(data["pos_y"], 2.2)
        self.assertAlmostEqual(data["vel_x"], 0.3)
        self.assertAlmostEqual(data["vel_y"], 0.4)

        # Test getting data for non-existent or inactive particle
        non_existent_data = ps.get_particle_data(99)  # Invalid ID
        self.assertIsNone(non_existent_data)

        inactive_particle_id = ps.max_particles - 1  # A valid ID but not yet active
        if (
            p_id != inactive_particle_id
        ):  # ensure we are not testing the active particle
            data_inactive = ps.get_particle_data(inactive_particle_id)
            self.assertIsNone(data_inactive)

    def test_remove_particle(self):
        ps = ParticleSystem(max_particles=2)
        p_id0 = ps.add_particle(1, 1, 1, 1)
        self.assertEqual(ps.num_active_particles, 1)

        ps.remove_particle(p_id0)
        self.assertFalse(ps.active[p_id0])
        self.assertEqual(ps.num_active_particles, 0)
        data_removed = ps.get_particle_data(p_id0)
        self.assertIsNone(data_removed, "Data for removed particle should be None")

        # Test removing non-existent or already removed particle
        ps.remove_particle(p_id0)  # Try removing again
        self.assertEqual(ps.num_active_particles, 0)  # Count should not change

        ps.remove_particle(99)  # Try removing invalid ID
        self.assertEqual(ps.num_active_particles, 0)  # Count should not change

    def test_reuse_slot_after_removal(self):
        ps = ParticleSystem(max_particles=2)
        p_id0 = ps.add_particle(1, 1, 1, 1)  # Uses slot 0
        p_id1 = ps.add_particle(2, 2, 2, 2)  # Uses slot 1
        self.assertEqual(ps.num_active_particles, 2)

        ps.remove_particle(p_id0)  # Remove particle from slot 0
        self.assertFalse(ps.active[p_id0])
        self.assertEqual(ps.num_active_particles, 1)

        # Add a new particle, it should reuse slot 0
        p_id_new = ps.add_particle(3, 3, 3, 3)
        self.assertEqual(p_id_new, p_id0, "Should reuse the freed slot 0")
        self.assertTrue(ps.active[p_id_new])
        self.assertEqual(ps.num_active_particles, 2)

        data_new = ps.get_particle_data(p_id_new)
        self.assertIsNotNone(data_new)
        self.assertEqual(data_new["pos_x"], 3)

        # Ensure particle in slot 1 is untouched
        data_p1 = ps.get_particle_data(p_id1)
        self.assertIsNotNone(data_p1)
        self.assertEqual(data_p1["pos_x"], 2)

    def test_update_with_inactive_particles(self):
        ps = ParticleSystem(max_particles=3)
        p0 = ps.add_particle(1, 1, 1, 1)  # vel_x = 1
        p1 = ps.add_particle(2, 2, 1, 1)  # vel_x = 1
        p2 = ps.add_particle(3, 3, 1, 1)  # vel_x = 1

        ps.remove_particle(p1)  # p1 is now inactive, its original pos_x = 2

        ps.update(dt=1.0)

        # p0 should update
        data_p0 = ps.get_particle_data(p0)
        self.assertIsNotNone(data_p0)
        self.assertEqual(data_p0["pos_x"], 2)  # 1 + 1*1

        # p1 should be inactive and its data should not be accessible via get_particle_data
        self.assertFalse(ps.active[p1])
        self.assertIsNone(ps.get_particle_data(p1))
        # Check original values are still there in the raw array but marked inactive
        self.assertEqual(ps.positions_x[p1], 2)  # Original value, not updated

        # p2 should update
        data_p2 = ps.get_particle_data(p2)
        self.assertIsNotNone(data_p2)
        self.assertEqual(data_p2["pos_x"], 4)  # 3 + 1*1

    def test_get_active_particles_data(self):
        ps = ParticleSystem(max_particles=3)
        p0_id = ps.add_particle(1, 1, 0, 0)
        p1_id = ps.add_particle(2, 2, 0, 0)

        active_data = ps.get_active_particles_data()
        self.assertEqual(len(active_data), 2)
        self.assertTrue(any(d["id"] == p0_id and d["pos_x"] == 1 for d in active_data))
        self.assertTrue(any(d["id"] == p1_id and d["pos_x"] == 2 for d in active_data))

        ps.remove_particle(p0_id)
        active_data_after_remove = ps.get_active_particles_data()
        self.assertEqual(len(active_data_after_remove), 1)
        self.assertTrue(
            any(d["id"] == p1_id and d["pos_x"] == 2 for d in active_data_after_remove)
        )
        self.assertFalse(any(d["id"] == p0_id for d in active_data_after_remove))


if __name__ == "__main__":
    unittest.main()
