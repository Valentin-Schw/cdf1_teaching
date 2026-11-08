"""
Geometry basics -- reusable Rhino.Geometry functions for Grasshopper.

Adding a new function with Copilot
-----------------------------------
1. Open this file and select this chat model, then ask Copilot something like:
   "Add a function here, all in Rhino geometry, that builds a <your shape/idea>.
   Follow the same style as create_cone / create_fractal_tree (defaults for
   optional inputs, a docstring listing params, return a Rhino.Geometry object)."
2. Once the function is added, ask Copilot:
   "Give me the Python code to use this function in a Grasshopper GHPython 3
   component, importing it from computational_design_and_fabrication."
3. Copy the snippet Copilot gives you into a GHPython component, wire up the
   inputs as sliders/panels, and set the output variable (e.g. `a`).
"""

import math
import random
import Rhino.Geometry as rg  # import der voreingestellten Rhino-Bibliothek

def create_cone(base_point=None, height=10.0, radius=5.0, cap_bottom=True):
    """
    Build a cone as a Brep.

    base_point : Rhino.Geometry.Point3d -- center of the cone's base circle
    height     : float -- cone height along the base plane's normal (Z by default)
    radius     : float -- base circle radius
    cap_bottom : bool  -- whether to cap the base circle (closed vs open cone)

    Returns a Rhino.Geometry.Brep.
    """
    if base_point is None:
        base_point = rg.Point3d(0, 0, 0)

    plane = rg.Plane(base_point, rg.Vector3d.ZAxis)
    cone = rg.Cone(plane, height, radius)
    return cone.ToBrep(cap_bottom)


def create_cylinder(base_point=None, radius=5.0, height=10.0):
    """
    Erzeugt einen geschlossenen Zylinder als Brep.

    base_point : Rhino.Geometry.Point3d -- Mittelpunkt der Grundfläche
    radius     : float -- Radius des Zylinders
    height     : float -- Höhe entlang der Welt-Z-Achse

    Returns a Rhino.Geometry.Brep.
    """
    if base_point is None:
        base_point = rg.Point3d(0, 0, 0)
    if not isinstance(base_point, rg.Point3d):
        raise TypeError("base_point muss ein Rhino.Geometry.Point3d sein.")
    if radius <= 0:
        raise ValueError("radius muss größer als 0 sein.")
    if height <= 0:
        raise ValueError("height muss größer als 0 sein.")

    plane = rg.Plane(base_point, rg.Vector3d.ZAxis)
    circle = rg.Circle(plane, float(radius))
    cylinder = rg.Cylinder(circle, float(height))
    return cylinder.ToBrep(True, True)


def create_random_quarter_cylinder(center=None, radius=1.0, height=10.0):
    """
    Erzeugt einen zufällig in einer Grid-Zelle platzierten Viertelzylinder.

    center : Rhino.Geometry.Point3d -- Mittelpunkt der Grid-Zelle
    radius : float -- Radius x; die Grid-Zelle hat die Seitenlänge 2 * x
    height : float -- Höhe des Viertelzylinders in +Z-Richtung

    Returns a closed Rhino.Geometry.Brep or None for invalid dimensions.
    """
    if center is None:
        center = rg.Point3d(0, 0, 0)
    if not isinstance(center, rg.Point3d):
        raise TypeError("center muss ein Rhino.Geometry.Point3d sein.")
    if radius <= 0:
        print("Fehler: radius muss größer als 0 sein.")
        return None
    if height <= 0:
        print("Fehler: height muss größer als 0 sein.")
        return None

    radius = float(radius)
    height = float(height)

    # Eine Ecke wählen und die lokalen Achsen in die Zelle hinein ausrichten.
    corner_x, corner_y = random.choice((-1, 1)), random.choice((-1, 1))
    corner = center + rg.Vector3d(
        0.5 * corner_x * radius,
        0.5 * corner_y * radius,
        0
    )
    inward_x = rg.Vector3d(-corner_x, 0, 0)
    inward_y = rg.Vector3d(0, -corner_y, 0)
    local_plane = rg.Plane(corner, inward_x, inward_y)

    start = corner + radius * local_plane.XAxis
    end = corner + radius * local_plane.YAxis
    midpoint = corner + (
        radius / math.sqrt(2.0)
    ) * (local_plane.XAxis + local_plane.YAxis)
    arc = rg.Arc(start, midpoint, end)
    profile = rg.PolyCurve()
    profile.Append(rg.LineCurve(corner, start))
    profile.Append(arc.ToNurbsCurve())
    profile.Append(rg.LineCurve(end, corner))

    if not profile.IsClosed or not profile.IsValid:
        raise RuntimeError(
            "Das Viertelkreis-Profil ist nicht geschlossen oder ungültig."
        )

    extrusion = rg.Extrusion.Create(profile, height, True)
    if extrusion is None:
        raise RuntimeError(
            "Die Extrusion des Viertelkreis-Profils konnte nicht erzeugt werden."
        )

    quarter_cylinder = extrusion.ToBrep()
    if quarter_cylinder is None or not quarter_cylinder.IsValid:
        raise RuntimeError(
            "Der Viertelzylinder konnte nicht als gültiger Brep erzeugt werden."
        )
    return quarter_cylinder


def split_random_points(
    points,
    count_sphere=0,
    count_cylinder=0,
    count_cone=0,
    count_quarter_cylinder=0,
    count_cuboid=0
):
    """
    Wählt Punkte zufällig aus und weist sie fünf Geometriegruppen zu.

    points : list[Rhino.Geometry.Point3d] -- verfügbare Punkte
    count_sphere : int -- Anzahl der Punkte für Kugeln
    count_cylinder : int -- Anzahl der Punkte für Zylinder
    count_cone : int -- Anzahl der Punkte für Kegel
    count_quarter_cylinder : int -- Anzahl der Punkte für Viertelzylinder
    count_cuboid : int -- Anzahl der Punkte für Quader

    Returns
    -------
    tuple
        (cone_points, sphere_points, quarter_cylinder_points,
        cylinder_points, cuboid_points) als fünf Listen von
        Rhino.Geometry.Point3d.
    """
    empty_result = ([], [], [], [], [])

    def flatten_points(data):
        """Wandelt Grasshopper-DataTrees und verschachtelte Listen flach."""
        if data is None:
            return []

        if hasattr(data, "BranchCount") and hasattr(data, "Branch"):
            flattened = []
            for branch_index in range(data.BranchCount):
                flattened.extend(
                    flatten_points(data.Branch(branch_index))
                )
            return flattened

        if hasattr(data, "Branches"):
            flattened = []
            for branch in data.Branches:
                flattened.extend(flatten_points(branch))
            return flattened

        if isinstance(data, (list, tuple)):
            flattened = []
            for item in data:
                flattened.extend(flatten_points(item))
            return flattened

        # Rhino-/Grasshopper-Listen können .NET-Enumerable sein.
        if not isinstance(data, rg.Point3d):
            try:
                iterator = iter(data)
            except TypeError:
                pass
            else:
                flattened = []
                for item in iterator:
                    flattened.extend(flatten_points(item))
                return flattened

        return [data]

    points = flatten_points(points)

    if not points:
        print("Fehler: Es wurde keine Punktliste angegeben.")
        return empty_result

    counts = (
        count_sphere,
        count_cylinder,
        count_cone,
        count_quarter_cylinder,
        count_cuboid
    )
    if any(count is None for count in counts):
        print("Fehler: Alle fünf Count-Werte müssen angegeben werden.")
        return empty_result

    try:
        counts = tuple(int(count) for count in counts)
    except (TypeError, ValueError):
        print("Fehler: Die Count-Werte müssen ganze Zahlen sein.")
        return empty_result

    if any(count < 0 for count in counts):
        print("Fehler: Die Count-Werte dürfen nicht negativ sein.")
        return empty_result

    total_count = sum(counts)
    if total_count > len(points):
        print(
            "Fehler: Insgesamt werden {} Punkte benötigt, "
            "aber nur {} Punkte sind verfügbar.".format(
                total_count, len(points)
            )
        )
        return empty_result

    selected_points = random.sample(list(points), total_count)
    random.shuffle(selected_points)

    sphere_end = counts[0]
    cylinder_end = sphere_end + counts[1]
    cone_end = cylinder_end + counts[2]
    quarter_cylinder_end = cone_end + counts[3]

    sphere_points = selected_points[:sphere_end]
    cylinder_points = selected_points[sphere_end:cylinder_end]
    cone_points = selected_points[cylinder_end:cone_end]
    quarter_cylinder_points = selected_points[cone_end:quarter_cylinder_end]
    cuboid_points = selected_points[quarter_cylinder_end:]

    return (
        cone_points,
        sphere_points,
        quarter_cylinder_points,
        cylinder_points,
        cuboid_points
    )



def create_sphere(center_point=None, radius=5.0):
    """
    Build a sphere as a Brep.

    center_point : Rhino.Geometry.Point3d -- center of the sphere
    radius       : float -- sphere radius

    Returns a Rhino.Geometry.Brep.
    """
    if center_point is None:
        center_point = rg.Point3d(0, 0, 0)

    my_sphere = rg.Sphere(center_point, radius)
    return my_sphere.ToBrep()



def boolean_difference(brep_a, brep_b):
    """
    Perform a boolean difference operation between two Breps.

    brep_a : Rhino.Geometry.Brep -- the first Brep
    brep_b : Rhino.Geometry.Brep -- the second Brep to subtract from the first

    Returns a list of Rhino.Geometry.Brep resulting from the difference.
    """
    if brep_a is None or brep_b is None:
        raise ValueError("Both brep_a and brep_b must be provided.")

    result = rg.Brep.CreateBooleanDifference(brep_a, brep_b, 0.001)
    return result


def copy_brep_along_z(brep, distance, copy_count):
    """
    Create copies of a Brep, each offset in the +Z direction.

    brep : Rhino.Geometry.Brep -- the Brep to copy
    distance : float -- the Z spacing between consecutive copies
    copy_count : int -- the number of copies to create

    Returns a list of Rhino.Geometry.Brep copies; copy i is moved by distance * (i + 1).
    """
    if brep is None:
        raise ValueError("brep must be provided.")
    if copy_count < 0:
        raise ValueError("copy_count must not be negative.")

    copies = []
    for i in range(1, int(copy_count) + 1):
        copy = brep.DuplicateBrep()
        copy.Transform(rg.Transform.Translation(rg.Vector3d(0, 0, distance * i)))
        copies.append(copy)
    return copies


def create_random_polyomino(n, plane=None, size=1.0, seed=None):
    """
    Erzeugt eine zufällige, zusammenhängende Fläche aus gleich großen Quadraten.

    n     : int   -- Anzahl der Quadrate; bei n <= 0 werden leere Ausgaben
                    zurückgegeben und eine Warnung ausgegeben.
    plane : Plane -- Ebene des Rasters; standardmäßig World XY.
    size  : float -- Kantenlänge jedes Quadrats.
    seed  : int   -- optionaler Startwert für reproduzierbare Ergebnisse.

    Returns
    -------
    tuple
        (squares, surfaces, centers, cells)
        squares  -- geschlossene rg.PolylineCurve-Objekte
        surfaces -- je Quadrat eine planare rg.Brep-Fläche
        centers  -- Mittelpunkt jedes Quadrats als rg.Point3d
        cells    -- Rasterkoordinaten als Strings, z. B. "(0, 0)"

    Beispiel für eine Grasshopper-Script-Komponente:

        from cdf.geometry_basics import create_random_polyomino
        a, b, c, d = create_random_polyomino(N, Plane, Size, Seed)

    Dabei werden die vier Ausgänge der Komponente mit a, b, c und d
    verbunden. Für optionale Eingänge können in Grasshopper None-Werte
    verwendet werden.
    """
    if not isinstance(n, int):
        raise TypeError("n muss eine ganze Zahl sein.")
    if n <= 0:
        print("Warnung: n muss größer als 0 sein; es werden keine Quadrate erzeugt.")
        return [], [], [], []
    if not isinstance(size, (int, float)) or size <= 0:
        raise ValueError("size muss eine positive Zahl sein.")

    if plane is None:
        plane = rg.Plane.WorldXY
    if not isinstance(plane, rg.Plane) or not plane.IsValid:
        raise ValueError("plane muss eine gültige Rhino.Geometry.Plane sein.")

    # Eine lokale Zufallsquelle verändert nicht den globalen Zufallszustand.
    rng = random.Random(seed)
    cells = {(0, 0)}

    while len(cells) < n:
        candidates = set()
        for i, j in cells:
            candidates.update(
                ((i + 1, j), (i - 1, j), (i, j + 1), (i, j - 1))
            )
        candidates.difference_update(cells)
        chosen = rng.choice(tuple(candidates))
        cells.add(chosen)

    ordered_cells = sorted(cells, key=lambda cell: (cell[1], cell[0]))
    squares = []
    surfaces = []
    centers = []
    cell_text = []

    for i, j in ordered_cells:
        origin = plane.Origin + (i * size) * plane.XAxis + (j * size) * plane.YAxis
        corners = [
            origin,
            origin + size * plane.XAxis,
            origin + size * plane.XAxis + size * plane.YAxis,
            origin + size * plane.YAxis,
            origin,
        ]
        polyline = rg.Polyline(corners)
        curve = rg.PolylineCurve(polyline)
        planar_breps = rg.Brep.CreatePlanarBreps(curve)
        if not planar_breps:
            raise RuntimeError("Die planare Fläche konnte nicht erzeugt werden.")

        squares.append(curve)
        surfaces.append(planar_breps[0])
        centers.append(
            origin + 0.5 * size * plane.XAxis + 0.5 * size * plane.YAxis
        )
        cell_text.append("({}, {})".format(i, j))

    return squares, surfaces, centers, cell_text