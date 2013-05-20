using Gee;
using libvoxelpress.plugins;
using libvoxelpress.vectors;




namespace voxelcore {
	public class AssemblyStage: GLib.Object {
		private WorkerPool<Vec3> thread_pool {get; set;}
		private AsyncQueue<Vec3?> fragments = new AsyncQueue<Vec3?>();

		public signal void done();
	}
}