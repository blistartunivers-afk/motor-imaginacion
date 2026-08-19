from scripts.generate_gallery import _cppn_intensity
from scripts.palettes import spatial_entropy_2d
import math

intensity = _cppn_intensity(256, 256, seed=1786893991)
print(f'256x256 spatial entropy: {spatial_entropy_2d(intensity):.4f}')

intensity2 = _cppn_intensity(48, 48, seed=0)
print(f'48x48 spatial entropy: {spatial_entropy_2d(intensity2):.4f}')

# Test multiple seeds
for s in [1786893991, 1786893992, 1786893993, 1786893994, 1786893995]:
    intensity = _cppn_intensity(256, 256, seed=s)
    print(f'seed={s} spatial={spatial_entropy_2d(intensity):.4f}')

for s in range(5):
    intensity = _cppn_intensity(48, 48, seed=s)
    print(f'seed={s} spatial={spatial_entropy_2d(intensity):.4f}')