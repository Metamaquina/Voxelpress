using Gee;
using libvoxelpress.plugins;
using libvoxelpress.vectors;


namespace voxelcore {
	public class ImportStage: GLib.Object {
		public PluginRepository<ImportPlugin> repository {get; private set;}
		public int face_count { get; private set; default = 0; }
		public signal void new_face(Face face);
		public signal void done();

		public ImportStage (string search_path) {
			repository = new PluginRepository<ImportPlugin> (search_path + "/import");
		}

		private void feed (Face face) {
			face_count += 1;
			new_face(face);
		}

		public void import (string[] paths) {
			foreach (var path in paths) {
				// FIXME intelligently guess the correct loader, instead of doing this:
				VectorModel? model = null;
				foreach (var plugin in repository.plugins) {
					model = plugin.create_new();
					model.new_face.connect(feed);
					try {
						model.load(path);
					} catch (Error e) {
						continue;
					}
					break;
				}
			}
			done();
		}
	}
}