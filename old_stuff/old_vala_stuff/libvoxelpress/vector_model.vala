using Gee;


namespace libvoxelpress.vectors {
	public errordomain VectorModelError {
		PARSER_FAILURE,
		DISCARD_FACE
	}

	public interface Vector: GLib.Object {
		public abstract double[] data {get; set;}
		public void scale(double amount) {
			for (int i=0; i<data.length; i+=1) {
				data[i] = data[i] * amount;
			}
		}
	}

	public class Vec3: GLib.Object, Vector {
		public double[] data { get; set; default = new double[] {0, 0, 0}; }
		public Vec3() {
		}
		public Vec3.with_coords (double a, double b, double c) {
			data[0] = a;
			data[1] = b;
			data[2] = c;
		}
	}
	
	public class Vec4: GLib.Object, Vector {
		public double[] data { get; set; default = new double[] {0, 0, 0}; }
		public Vec4() {
		}
		public Vec4.with_coords (double a, double b, double c, double d) {
			data[0] = a;
			data[1] = b;
			data[2] = c;
			data[3] = d;
		}
	}

	public class Face: GLib.Object {
		public Vec3[] vertices = new Vec3[] { new Vec3(), new Vec3(), new Vec3() };
		public Vec3[] normals = new Vec3[] { new Vec3(), new Vec3(), new Vec3() };
	}

	public abstract class VectorModel : GLib.Object {
		public signal void new_face (Face face);
		public abstract int face_count { get; private set; }
		public abstract void load(string path) throws IOError, VectorModelError;
	}
}