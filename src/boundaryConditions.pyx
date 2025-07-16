import numpy as np
import domain 

from domain import Domain

class BoundaryConditions:
    def __init__(self, nx:int, ny:int, domain:Domain, g=None, TBC=None):
        """
        Initialize the boundary conditions for a grid.

        Parameters:
            ncx (int): Number of cells in the x-direction.
            ncy (int): Number of cells in the y-direction.
            g (callable or float): Neumann flux as a constant or a function of (x, y).
            TBC (callable or float): Dirichlet temperature as a constant or a function of (x, y).
        """
        self.nx = nx
        self.ny = ny
        # Initialize and compute the dirichlet boundary matrix b and the Neumann boundary matrix for each side using indices
        # west side
        self.bW, self.cW = self.create_boundary_matrices(domain, 'west')
        # east side
        self.bE, self.cE = self.create_boundary_matrices(domain, 'east')
        # south side
        self.bS, self.cS = self.create_boundary_matrices(domain, 'south')
        # north side
        self.bN, self.cN = self.create_boundary_matrices(domain, 'north')

        # Set g and TBC as either functions or constants
        self.g = g if callable(g) else (lambda x, y: g)
        self.TBC = TBC if callable(TBC) else (lambda x, y: TBC)

    def create_boundary_matrices(self, domain:Domain, side:str):
        """
        create boundary matrices using vertex indices for Dirichlet and Neumann conditions.

        Parameters:
            domain to get the a dictionnary with key the side and value indices
            side (str): Boundary side ('west', 'east', 'south', 'north').

                Returns:
                    Tuple[np.ndarray, np.ndarray]: Dirichlet and Neumann boundary matrices.
        """
        if side not in ["west", "east", "south", "north"]:
            print(" the side value is in", ["west", "east", "south", "north"])

        if side == "west":
            indices_dirichlet_side = domain.dict_dirichlet_indices[side]
            indices_neumann_side = domain.dict_neumann_indices[side]
            b = np.zeros(self.nx * self.ny)
            c = np.zeros(self.nx * self.ny)
            b[indices_dirichlet_side] = 1
            c[indices_neumann_side] = 1
            c = c.reshape((self.nx, self.ny))[:-1, :-1]
            b = b.reshape((self.nx, self.ny))[:-1, :-1]

        elif side == "east":
            indices_dirichlet_side = domain.dict_dirichlet_indices[side]
            indices_neumann_side = domain.dict_neumann_indices[side]
            b = np.zeros(self.nx * self.ny)
            c = np.zeros(self.nx * self.ny)
            b[indices_dirichlet_side] = 1
            c[indices_neumann_side] = 1
            c = c.reshape((self.nx, self.ny))[1:, :-1]
            b = b.reshape((self.nx, self.ny))[1:, :-1]


        elif side =="north":
            indices_dirichlet_side = domain.dict_dirichlet_indices[side]
            indices_neumann_side = domain.dict_neumann_indices[side]
            b = np.zeros(self.nx * self.ny)
            c = np.zeros(self.nx * self.ny)
            b[indices_dirichlet_side] = 1
            c[indices_neumann_side] = 1
            c = c.reshape((self.nx, self.ny))[:-1, 1:]
            b = b.reshape((self.nx, self.ny))[:-1, 1:]


        elif side == "south":
            indices_dirichlet_side = domain.dict_dirichlet_indices[side]
            indices_neumann_side = domain.dict_neumann_indices[side]
            b = np.zeros(self.nx * self.ny)
            c = np.zeros(self.nx * self.ny)
            b[indices_dirichlet_side] = 1
            c[indices_neumann_side] = 1
            c = c.reshape((self.nx, self.ny))[1:,:-1]
            b = b.reshape((self.nx, self.ny))[1:,:-1]
        return b, c

    def customize_boundary_conditions_from_vertices(self, domain: Domain, vertices_position, g_func=None, tbc_func=None):
        """
        Customize the boundary conditions for g (flux) and TBC (Dirichlet temperature) based on vertex indices.

        Parameters:
            domain: give the arguments boundaries a dictionnary of the all vertex indices for each side
            vertices_position (Tuple[np.ndarray, np.ndarray]): Vertex coordinates (X, Y).
            g_func (callable): Function g(x, y) to compute Neumann flux at midpoints.
            tbc_func (callable): Function TBC(x, y) to compute Dirichlet temperature at midpoints.
        """
        X, Y = vertices_position
        ncx, ncy = X.shape[0] - 1, Y.shape[1] - 1  # Adjust to cells

        # Initialize g and TBC matrices
        self.g = np.zeros((ncx, ncy))
        self.TBC = np.zeros((ncx, ncy))

        # Helper function to calculate midpoint values
        def compute_midpoint_value(vertex_indices, func):
            values = []
            for v1, v2 in zip(vertex_indices[:-1], vertex_indices[1:]):  # Pair adjacent vertices
                x1, y1 = X.flatten()[v1], Y.flatten()[v1]
                x2, y2 = X.flatten()[v2], Y.flatten()[v2]
                midpoint_x, midpoint_y = (x1 + x2) / 2, (y1 + y2) / 2
                values.append(func(midpoint_x, midpoint_y))
            return np.array(values)
        """
        def compute_midpoint_value(vertex_indices, func):
            values = []
            print(vertex_indices.size)
            for v1 in vertex_indices:  # Pair adjacent vertices
                x1, y1 = X.flatten()[v1], Y.flatten()[v1]
                values.append(func(x1, y1))
            return np.array(values)
        """
        # Assign values for Dirichlet temperature (TBC)
        for side, vertex_indices in domain.boundaries.items():
            if vertex_indices.size > 0:
                values = compute_midpoint_value(vertex_indices, tbc_func)
                if side == "west":
                    self.TBC[0, :] = values
                elif side == "east":
                    self.TBC[-1, :] = values
                elif side == "south":
                    self.TBC[:, 0] = values
                elif side == "north":
                    self.TBC[:, -1] = values
        print(self.TBC)
        # Assign values for Neumann flux (g)
        for side, vertex_indices in domain.boundaries.items():
            if vertex_indices.size>0:
                values = compute_midpoint_value(vertex_indices, g_func)
                if side == "west":
                    self.g[0, :] = values
                elif side == "east":
                    self.g[-1, :] = values
                elif side == "south":
                    self.g[:, 0] = values
                elif side == "north":
                    self.g[:, -1] = values
        # Define g and TBC
        self.TBC = self.bW * self.TBC + self.bE * self.TBC + self.bS * self.TBC + self.bN * self.TBC
        self.g = self.cW*self.g + self.cE*self.g + self.cS*self.g + self.cN*self.g
