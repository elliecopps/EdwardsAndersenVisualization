# EdwardsAndersenVisualization
A visualization of the Edwards Andersen spin glass model. 

Running this code will bring up a visualization of the Edwards Andersen spin glass model. The red bonds are called ferromagnetic bonds. They are satisfied when the two spins they connect face in the same direction. The blue bonds are antiferromagnetic bonds. They are satisfied when their spins face in opposite directions.

The goal of the algorithm is to find the lowest energy state(s) of the system, where the fewest possible number of bonds is broken/unsatisfied. To accomplish this, we first identify each square of four spins that will have at least one unsatisfied bond. These groups are called frustrated plaquettes. Next, we pair the plaquettes and find the minimum-length strings between them. Each bond that these strings pass through will be frustrated in our ground state configuration. Based on the bonds we have determined will be frustrated, we can figure out which direction each of the spins will face.

As of now, the algorithm does not work for all cases. Our assumption that the minimum string length will always produce ground states does not seem to be correct for the boundary conditions that we have chosen. The code will let you know if you encounter a configuration that will not work.

This algorithm is based on the algorithm detailed in: Landry, J. W., and S. N. Coppersmith. “Ground States of Two-Dimensional±JEdwards-Anderson Spin Glasses.” Physical Review B, vol. 65, no. 13, 2002, doi:10.1103/physrevb.65.134404. 

