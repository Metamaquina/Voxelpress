using Gee;
using libvoxelpress.fragments;
using libvoxelpress.etc;


namespace libvoxelpress.fragments {

    public interface VoxelModel: Object {
        public abstract Coordinate? min {get; set;}
        public abstract Coordinate? max {get; set;}
        public abstract Fragment? seek (int x, int y, int z);
        public abstract void push(int x, int y, int z, Fragment voxel);
    }


    /*
    // ... in progress ...

    public class BlockedLayer: Object {
        public Fragment? min {get; private set; default=null;}
        public Fragment? max {get; private set; default=null;}
        public Fragment? seek (int x, int y) {
            return null;
        }
        public void push (Fragment? voxel) {
        }
        public static Object? create() {
            return new BlockedLayer();
        }
    }
    */


    public class CacheLayer: Object {
        /* pdq layer type, replace with BlockedLayer once it is written */
        public BTree<Coordinate, Fragment> data {get; private set;}
        
        public CacheLayer () {
            data = new BTree<Coordinate, Fragment>(Coordinate.cmp_2D, Fragment.create);
        }
        public Fragment? seek (Coordinate coords) {
            Fragment? frag;
            lock(data) {
                frag = data.fetch_or_create(coords);
            }
            return frag;
        }
        public void push (Coordinate coords, Fragment? voxel) {
            lock(data) {
                data.push(coords, voxel);
            }
        }
        public static Object? create() {
            return new CacheLayer();
        }
    }


    public class BlockedModel: Object, VoxelModel {
        public BTree<int,CacheLayer> layers {get; private set;}

        public Coordinate? min {get; set; default=null;}
        public Coordinate? max {get; set; default=null;}

		private Mutex min_lock = new Mutex();
		private Mutex max_lock = new Mutex();

        public BlockedModel () {
            layers = new BTree<int,CacheLayer>(
                (lhs, rhs) => {return (lhs<rhs) ? -1 : (lhs>rhs) ? 1 : 0;}, 
                CacheLayer.create);
        }

        public Fragment? seek (int x, int y, int z) {
            CacheLayer layer;
            lock(layers) {
                layer = layers.fetch_or_create(z);
            }
            return layer.seek(new Coordinate (x, y, z));
        }
        public void push(int x, int y, int z, Fragment voxel) {
            var coords = new Coordinate (x, y, z);
            CacheLayer layer;
            lock (layers) {
                layer = layers.fetch_or_create(z);
            }
            layer.push(coords, voxel);
			min_lock.lock();
			if (min == null) {
				min = new Coordinate(coords.x, coords.y, coords.z);
			}
			else {
				if (coords.x < min.x) {
					min.x = coords.x;
				}
				if (coords.y < min.y) {
					min.y = coords.y;
				}
				if (coords.z < min.z) {
					min.z = coords.z;
				}
			}
			min_lock.unlock();
			max_lock.lock();
			if (max == null) {
				max = new Coordinate(coords.x, coords.y, coords.z);
			}
			else {
				if (coords.x > max.x) {
					max.x = coords.x;
				}
				if (coords.y > max.y) {
					max.y = coords.y;
				}
				if (coords.z > max.z) {
					max.z = coords.z;
				}
			}
			max_lock.unlock();
        }
    }
}
