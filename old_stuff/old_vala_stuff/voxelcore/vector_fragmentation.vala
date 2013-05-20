using libvoxelpress.plugins;
using libvoxelpress.vectors;
using libvoxelpress.fragments;


class Point : GLib.Object {
	/*
	  A Point is different than a Coordinate in that Points use doubles to represent
	  spatial locations - Fragments represent space in integers.

	  The Point's constructor is responsible from converting from absolute vector
	  positions to the raster grid.
	 */
	public double x {get; set;}
	public double y {get; set;}
	public double z {get; set;}

	public Point(Vec3 vec, double resolution, double thickness) {
		this.x = vec.data[0] / resolution;
		this.y = vec.data[1] / resolution;
		this.z = vec.data[2] / thickness;
	}

	public Point.with_coords(double x, double y, double z) {
		this.x = x;
		this.y = y;
		this.z = z;
	}
}


class Edge : GLib.Object {
	public Point[] ends {get; private set;}
	private Point low_x;
	private Point low_y;
	private Point low_z;
	private Point high_x;
	private Point high_y;
	private Point high_z;
	public double xmin {
		get {
			return low_x.x;
		}
	}
	public double xmax {
		get {
			return high_x.x;
		}
	}
	public double ymin {
		get {
			return low_y.y;
		}
	}
	public double ymax {
		get {
			return high_y.y;
		}
	}
	public double zmin {
		get {
			return low_z.z;
		}
	}
	public double zmax {
		get {
			return high_z.z;
		}
	}

	public Edge(Point i, Point k) {
		ends = {i, k};
		low_x = i.x < k.x ? i : k;
		low_y = i.y < k.y ? i : k;
		low_z = i.z < k.z ? i : k;
		high_x = low_x == i ? k : i;
		high_y = low_y == i ? k : i;
		high_z = low_z == i ? k : i;
	}

	public Point? slice_x(double x) {
		if (low_x.x <= x && x <= high_x.x && low_x.x != high_x.x) {
			double alpha = (x-low_x.x)/(high_x.x-low_x.x);
			double y = mix(low_x.y, high_x.y, alpha);
			double z = mix(low_x.z, high_x.z, alpha);
			return new Point.with_coords(x, y, z);
		}
		else {
			return null;
		}
	}

	public Point? slice_z(double z) {
		if (low_z.z <= z && z <= high_z.z && low_z.z != high_z.z) {
			double alpha = (z-low_z.z)/(high_z.z-low_z.z);
			double x = mix(low_z.x, high_z.x, alpha);
			double y = mix(low_z.y, high_z.y, alpha);
			return new Point.with_coords(x, y, z);
		}
		else {
			return null;
		}
	}

	public double? sample_x(double y) {
		if (low_y.y <= y && y <= high_y.y) {
			double alpha = (y - low_y.y) / (high_y.y - low_y.y);
			return mix(low_y.x, high_y.x, alpha);
		}
		else {
			return null;
		}
	}

	public double? sample_y(double x) {
		if (low_x.x <= x && x <= high_x.x) {
			double alpha = (x - low_x.x) / (high_x.x - low_x.x);
			return mix(low_x.y, high_x.y, alpha);
		}
		else {
			return null;
		}
	}

	public double? sample_z(double y) {
		if (low_y.y <= y && y <= high_y.y) {
			double alpha = (y - low_y.y) / (high_y.y - low_y.y);
			return mix(low_y.z, high_y.z, alpha);
		}
		else {
			return null;
		}
	}
}


namespace voxelcore {
	public class Vector2Fragment : GLib.Object, VectorPlugin {
		// implied final plugin for the vector_stage
		private double resolution;
		private double thickness;
		private BlockedModel cache;

		public Vector2Fragment(double resolution, double thickness, BlockedModel cache) {
			this.resolution = resolution;
			this.thickness = thickness;
			this.cache = cache;
		}

		private void push(double x, double y, double z) {
			// "Math.round" seems to give the best results (vs float and trunc)
			cache.push((int) Math.round(x),(int) Math.round(y),(int) Math.round(z),new Fragment());
		}

		public void transform (Face face) throws VectorModelError {
			/*
			  FIXME:
			  1)  There has got to be a more efficient way to do this.

			  2)  Little gaps probably come only generating infill voxels for a face,
			      and not actually generating voxels along the edges.
				  Note that lack of symetry in an object can also come from its placement.

			  3)  "Scale" doesn't work at all now... o_O
			 */
			Point[] points = {};
			foreach (var vert in face.vertices) {
				var point = new Point(vert, resolution, thickness);
				points += point;
				push(point.x, point.y, point.z);
			}
			Edge[] edges = {
				new Edge(points[0], points[1]),
				new Edge(points[1], points[2]),
				new Edge(points[2], points[0])
			};
			double? xmin = null;
			double? xmax = null;
			double? zmin = null;
			double? zmax = null;
			foreach (Edge edge in edges) {
				if (xmin == null || edge.xmin < xmin) {
					xmin = edge.xmin;
				}
				if (xmax == null || edge.xmax > xmax) {
					xmax = edge.xmax;
				}
				if (zmin == null || edge.zmin < zmin) {
					zmin = edge.zmin;
				}
				if (zmax == null || edge.zmax > zmax) {
					zmax = edge.zmax;
				}
			}
			for (double z = Math.floor(zmin); z <= Math.ceil(zmax); z += 1) {
				Point[] ends = {};
				foreach (Edge edge in edges) {
					if (edge.zmin != edge.zmax) {
						// one or zero points intersect the z plane
						var point = edge.slice_z(z);
						if (point != null) {
							ends += point;
						}
					}
				}
				if (ends.length >= 2) {
					var scanline = new Edge(ends[0], ends[1]);
					for (double x = Math.floor(scanline.xmin); x <= Math.ceil(scanline.xmax); x+=1) {
						var y = scanline.sample_y(x);
						if (y != null) {
							// cache a fragment
							push(x,y,z);
						}
					}
					for (double y = Math.floor(scanline.ymin); y <= Math.ceil(scanline.ymax); y+=1) {
						var x = scanline.sample_x(y);
						if (x != null) {
							// cache a fragment
							push(x,y,z);
						}
					}
				}
			}

			for (double x = Math.floor(xmin); x <= Math.ceil(xmax); x += 1) {
				Point[] ends = {};
				foreach (Edge edge in edges) {
					if (edge.xmin != edge.xmax) {
						// one or zero points intersect the x plane
						var point = edge.slice_x(x);
						if (point != null) {
							ends += point;
						}
					}
				}
				if (ends.length >= 2) {
					var scanline = new Edge(ends[0], ends[1]);
					for (double y = Math.floor(scanline.ymin); y <= Math.ceil(scanline.ymax); y+=1) {
						var z = scanline.sample_z(y);
						if (z != null) {
							// cache a fragment
							push(x,y,z);
						}
					}
				}
			}

		}
	}
}