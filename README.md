icfpc-ouroboros-2012
====================

Strategy
========

1. find availble positions within _5_ steps
2. for each available position, evaluate heuristic
3. pick position with least heuristic value
4. repeat


Haskell/functional Approach
---------------------------

	-- get a list of points the robot travels
	getFullPath :: Point -> [Point]
	getFullPath p = [p: getNextPoint( availablePositions(p, m, 5), m )]

	-- get the available positions next to a robot given _s_ steps
	availablePositions :: (Point, Map, Int) -> [Point]
	availablePositions (p, m, s) = filter (willNotDie m) nearBy(p, s) 

	-- compute whether a robot can access a point
	willNotDie :: Map -> Point -> Bool


	-- get all points accessible within a fixed number of steps
	nearBy :: (Point, Int) -> [Point]


	-- get the next point a robot should move
	getNextPoint :: ([Point], Map) -> Point
	getNextPoint ( [availPos : xs], m ) = foldl smallerH (availPos xs) m


	-- compare two point's heuristic
	smallerH :: Point -> Point -> Point
	smallerH p1 p2 m = if (heuristic (p1, m) < heuristic (p2, m)) then p1 else p2 

	-- compute the heurisitc given a point
	heuristic :: (Point, Map) -> Int


C#/Imperitive Approach
----------------------


	// get the next point a robot should move given availe points it can move
	// dependencies:
	//		- Bool isNullOrEmpty(List l)
	//		- int heuristic(List<Point> points)
	Point getNextPoint(List<Point> availPointsList) 
	{
		if(isNullOrEmpty(availPointsList)) return null;
		int smallestVal = heuristic(availPointsList[0]);
		Point smallestPoint = availPointsList[0];
		foreach(Point p in availPointsList) 
		{
			if(heuristic(p) < smallestVal) 
			{
				smallestPoint = p;
			}
		}
		return p;
	}

	// dependencies: 
	// 		- Bool willDie(Point p)
	// 		- List<Point> getAllNearByPoints(Point p, int steps)
	List<Point> computeAvailablePoints(Point p, int steps) 
	{
		List<Point> nearByPoints = getAllNearByPoints(p, steps);
		for(Point p: nearByPoints) 
		{
			if(willDie(p)) {
				nearByPoints.remove(p);
			}
		}
	}


