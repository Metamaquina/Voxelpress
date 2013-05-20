using Gee;


namespace libvoxelpress.vectors {
	public class Mat3: GLib.Object {
		public double[,] data = {{1, 0, 0}, 
								 {0, 1, 0}, 
								 {0, 0, 1}};
		public Vec3 multiply(Vec3 vector) {
			var result = new Vec3.with_coords(0,0,0);
			for (int y = 0; y<3; y+=1) {
				double cache = 0;
				for (int x = 0; x<3; x+=1) {
					cache += this.data[y,x] * vector.data[x];
				}
				result.data[y] = cache;
			}
			return result;
		}
	}

	public double mix (double x, double y, double a) {
		return x*(1.0-a) + y*a;
	}

	public Vec3 mix_Vec3 (Vec3 x, Vec3 y, double a) {
		return new Vec3.with_coords(
			mix(x.data[0], y.data[0], a),
			mix(x.data[1], y.data[1], a),
			mix(x.data[2], y.data[2], a)
			);
	}

	public double radians ( double degrees ) {
		return degrees * 0.0174532925;
	}

	private Vec3 basic_skew (Vec3 coord, Mat3 skew_matrix) {
		double x = coord.data[0];
		double y = coord.data[1];
		double z = coord.data[2];
		var flat = new Vec3.with_coords(x, y, 1);
		var next = skew_matrix.multiply(flat);
		next.data[2] = z;
		return next;
	}

	public Vec3 x_skew (Vec3 coord, double a) {
		var skew = new Mat3();
		skew.data[0,1] = Math.tan(radians(a));
		return basic_skew(coord, skew);
	}

	public Vec3 y_skew (Vec3 coord, double a) {
		var skew = new Mat3();
		skew.data[1,0] = Math.tan(radians(a));
		return basic_skew(coord, skew);
	}
}