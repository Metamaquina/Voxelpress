using Gee;
using libvoxelpress.vectors;
using libvoxelpress.plugins;


public static double SKEW;




public class DerpAdjustment : GLib.Object, VectorPlugin {
	public void transform (Face face) throws VectorModelError {
		for (int i=0; i<3; i+=1) {
			face.vertices[i] = x_skew(face.vertices[i], SKEW);
		}
	}
}




public VectorMetaData register_plugin (Module module) {
	var info = new VectorMetaData();
	info.object_type = typeof (DerpAdjustment);
	info.name = "Derp Adjustment";

	// The following are optional:
	info.condition = () => { 
		return SKEW != 0;
	};
	info.options = new OptionEntry[] {
		OptionEntry () {
			long_name="skew",
			short_name='d', 
			flags=0,
			arg=OptionArg.DOUBLE,
			arg_data=&SKEW,
			description="Skew for derp adjustment.",
			arg_description="degrees"
		}
	};
	return info;
}