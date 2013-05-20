using Gee;
using libvoxelpress.vectors;
using libvoxelpress.plugins;


public static double SCALE = 1;




public class ScaleAdjustment : GLib.Object, VectorPlugin {
	public void transform (Face face) throws VectorModelError {
		for (int i=0; i<3; i+=1) {
			face.vertices[i].scale(SCALE);
		}
	}
}




public VectorMetaData register_plugin (Module module) {
	var info = new VectorMetaData();
	info.object_type = typeof (ScaleAdjustment);
	info.name = "Scale Adjustment";

	// The following are optional:
	info.condition = () => { 
		return SCALE != 1;
	};
	info.options = new OptionEntry[] {
		OptionEntry () {
			long_name="scale",
			short_name='s',
			flags=0,
			arg=OptionArg.DOUBLE,
			arg_data=&SCALE,
			description="Adjust model scale.",
			arg_description="1"
		}
	};
	return info;
}