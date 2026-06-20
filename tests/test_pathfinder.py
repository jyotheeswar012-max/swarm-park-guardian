from core.pathfinder import pso_path

def test_path_returns_waypoints():
    path = pso_path((0,0), (100,100), obstacles=[])
    assert len(path) == 5

def test_path_starts_near_start():
    path = pso_path((0,0), (100,100), obstacles=[])
    assert abs(path[0][0]) < 1 and abs(path[0][1]) < 1

def test_path_ends_near_end():
    path = pso_path((0,0), (100,100), obstacles=[])
    assert abs(path[-1][0] - 100) < 1 and abs(path[-1][1] - 100) < 1
