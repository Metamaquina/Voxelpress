using Gee;
using libvoxelpress.vectors;
using libvoxelpress.plugins;


public class ObjModel : VectorModel, ImportPlugin {
	// Circumstantial use of two different list types to hopefully
	// speed things up a bit for sufficiently large models.
	private Vec3[] vertex_array = {};
	private Vec3[] normal_array = {};
	public override int face_count { get; private set; }
	
	public override void load(string path) throws IOError, VectorModelError {
		var file = File.new_for_path(path);
		
		if (file.query_exists()) {
			parse(file);
		}
		else {
			//throw new IOError("File does not exist.");
			stdout.printf("File does not exist...?\n");
		}
	}
	
	private Vec3 parse_vector(string line) {
		var parts = line.split(" ");
		return new Vec3.with_coords (
			double.parse(parts[1]),
			double.parse(parts[2]),
			double.parse(parts[3])
			);
	}
	
	private void parse(File file) throws IOError, VectorModelError {
		try {
			var IN = new DataInputStream(file.read());
			string line = IN.read_line(null);
			while (line != null) {
				if (line.has_prefix("o ") || line.has_prefix("g ")) {
					// FIXME verify correctness
				}
				if (line.has_prefix("v ")) {
					vertex_array += parse_vector(line);
				}
				if (line.has_prefix("vn ")) {
					normal_array += parse_vector(line);
				}
				if (line.has_prefix("f ")) {
					// FIXME break down quads into triangles.
					Face face = new Face();
					var parts = line.split(" ");
					for (int i=0; i<3; i+=1) {
						var bits = parts[1+i].split("/");
						face.vertices[i] = vertex_array[int.parse(bits[0])-1];
						face.normals[i] = normal_array[int.parse(bits[2])-1];
					}
					//faces.push(face);
					new_face(face);
				}
				line = IN.read_line(null);
			}
			
		} catch (Error e) {
			throw new VectorModelError.PARSER_FAILURE("Parser quit with an error.");
		}
		if (face_count == 0) {
			throw new VectorModelError.PARSER_FAILURE("Parser yielded no faces.");
		}
	}
}


public ImportMetaData register_plugin (Module module) {
	var info = new ImportMetaData();
	info.object_type = typeof (ObjModel);
	info.name = "obj import";
	info.extensions = {".obj"};

	return info;
}