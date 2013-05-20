using Gee;
using libvoxelpress.vectors;


namespace libvoxelpress.fragments {


    public class Coordinate: GLib.Object {
        public int x {get; set;}
        public int y {get; set;}
		public int z {get; set;}

        public Coordinate (int x, int y, int z) {
            this.x = x;
            this.y = y;
            this.z = z;
        }

        public static int cmp_2D (Coordinate lhs, Coordinate rhs) {
            if (lhs.y < rhs.y) {
                return -1;
            }
            else if (lhs.y > rhs.y) {
                return 1;
            }
			else if (lhs.x < rhs.x) {
                return -1;
            }
            else if (lhs.x > rhs.x) {
                return 1;
            }
            else {
                return 0;
            }
        }

		public static int cmp_3D (Coordinate lhs, Coordinate rhs) {
			if (lhs.z < rhs.z) {
				return -1;
			}
			else if (lhs.z > rhs.z) {
				return 1;
			}
			else {
				return cmp_2D (lhs, rhs);
			}
		}
    }


    public class Fragment: GLib.Object {
        public Vec4 color {get; set;}
        public Vec3 normal {get; set;}
        public bool solid {get; set; default=true;}

        public static Object? create() {
            var frag = new Fragment();
            frag.solid = false;
            return frag;
        }
    }
}