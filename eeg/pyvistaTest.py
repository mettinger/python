from pyvista import examples
import time

mesh = examples.download_dragon()
mesh['scalars'] = mesh.points[:, 1]
mesh.plot(cpos='xy', cmap='plasma',pbr=True, metallic=1.0, roughness=0.6,zoom=1.7)

