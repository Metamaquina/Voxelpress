using libvoxelpress.vectors;


namespace libvoxelpress.plugins {


	public delegate bool ValidityTest ();


	public interface PluginMetaData : GLib.Object {
		public abstract Type object_type {get; set;}
		public abstract string name {get; set;}
	}


	public class ImportMetaData : GLib.Object, PluginMetaData {
		public Type object_type {get; set;}
		public string name {get; set;}
		public string[] extensions {get; set;}
	}


	public class VectorMetaData : GLib.Object, PluginMetaData {
		public Type object_type {get; set;}
		public string name {get; set;}
		public ValidityTest condition {get; set; default = () => { return true; }; }
		public OptionEntry[] options {get; set; default={};}
	}


    public interface ImportPlugin : VectorModel {
        public abstract void load(string path) throws IOError, VectorModelError;
    }


    public interface VectorPlugin : GLib.Object {
        public abstract void transform(Face face) throws VectorModelError;
    }
}