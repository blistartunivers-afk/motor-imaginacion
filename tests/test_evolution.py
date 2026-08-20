import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from scripts.evolution import create_random_genome, mutate_genome, crossover_genomes

class TestEvolution(unittest.TestCase):
    def test_create_genome(self):
        genome = create_random_genome(seed=42)
        self.assertEqual(genome["version"], 1)
        self.assertEqual(len(genome["w1"]), 8)
        self.assertEqual(len(genome["act1"]), 8)
        self.assertEqual(len(genome["w2"]), 8)
        self.assertEqual(len(genome["act2"]), 8)
        self.assertEqual(len(genome["w3"]), 8)
        
    def test_mutation(self):
        g1 = create_random_genome(seed=100)
        g2 = mutate_genome(g1, mutation_rate=0.5, seed=101)
        self.assertEqual(g2["generation"], 1)
        self.assertNotEqual(g1["w1"], g2["w1"])
        
    def test_crossover(self):
        p1 = create_random_genome(seed=1)
        p2 = create_random_genome(seed=2)
        child = crossover_genomes(p1, p2, seed=3)
        self.assertEqual(child["generation"], 1)

if __name__ == "__main__":
    unittest.main()
