using Gee;
using libvoxelpress.plugins;
using libvoxelpress.vectors;
using libvoxelpress.fragments;



namespace voxelcore {
    public class VectorStage: GLib.Object {
		private WorkerPool<Face> thread_pool {get; set;}
        public PluginRepository<VectorPlugin> repository {get; private set;}
        public ArrayList<VectorPlugin> pipeline {get; set;}
		private AsyncQueue<Face?> faces = new AsyncQueue<Face?>();
		private BlockedModel cache = new BlockedModel();

		public Coordinate? min { get { return cache.min; } }
		public Coordinate? max { get { return cache.max; } }
		public BlockedModel debug { get { return cache; } } // FIXME: REMOVE

		public bool started { get { return thread_pool.running; } }
		public bool active { get { return thread_pool.running && !thread_pool.dry_up; } }

		public signal void done();


        public VectorStage (string search_path, ImportStage import_stage) {
            repository = new PluginRepository<VectorPlugin> (search_path + "/vector");
            pipeline = new ArrayList<VectorPlugin>();
            try {
				thread_pool = new WorkerPool<Face> (faces, 1, true);
            } catch (ThreadError e) {
                stdout.printf("Failed to create thread pool.\n");
            }
			import_stage.new_face.connect(feed);
			thread_pool.event_hook.connect(worker_func);
        }


		public void setup_pipeline(double resolution, double thickness) {
            foreach (var plugin in repository.plugins) {
				var info = (VectorMetaData) plugin.meta_data;
				if (info.condition()) {
					pipeline.add(plugin.create_new());
				}
				else {
					stdout.printf(" - ignored: %s\n", info.name);
				}
            }
			pipeline.add(new Vector2Fragment(resolution, thickness, cache));
			thread_pool.start();
		}


		public OptionGroup get_plugin_options () {
			OptionEntry[] entries = {};
			foreach (var plugin in repository.plugins) {
				var info = (VectorMetaData) plugin.meta_data;
				foreach (var option in info.options) {
					entries += option;
				}
			 }
			entries.resize(entries.length + 1); // crashes if you don't do this

			var group = new OptionGroup(
				"vector-plugins",
				"Vector Plugin Options",
				"Show help entries for the vector plugins",
				null,
				null);

			group.add_entries(entries);
			return group;
		}

		
		private void feed (Face face) {
			faces.push(face);
		}


		public void speed_up () {
			thread_pool.increase_pool(2);
		}


		public void join () {
			if (active) {
				thread_pool.join_all();
			}
			done();
		}


		private void worker_func (Face face) {
			foreach (VectorPlugin stage in pipeline) {
				try {
					stage.transform(face);
				} catch (VectorModelError e) {
					// FIXME do something useful here
				}
			}
		}
    }
}