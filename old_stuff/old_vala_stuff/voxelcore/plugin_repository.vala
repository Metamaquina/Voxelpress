using Gee;
using libvoxelpress.plugins;


namespace voxelcore {
    public class PluginModule<SomePlugin> : Object {
        public PluginMetaData meta_data;
        private Module module;
        private delegate PluginMetaData RegisterPluginFunc (Module module);
        
        public PluginModule (string path) {
            module = Module.open(path, ModuleFlags.BIND_LAZY);
            assert(module != null);
            void* function;
            module.symbol("register_plugin", out function);
            RegisterPluginFunc register_plugin = (RegisterPluginFunc) function;
            meta_data = register_plugin(module);        
            //stdout.printf(" - loaded \"%s\"\n", meta_data.name);
        }
        
        public SomePlugin create_new () {
            return (SomePlugin) Object.new(meta_data.object_type);
        }
    }
   

    public class PluginRepository<SomePlugin> : Object {
        public ArrayList<PluginModule<SomePlugin>> plugins {get; private set;}  

        public PluginRepository (string search_path) {
            plugins = new ArrayList<PluginModule<SomePlugin>>();
            try {
                var dir = File.new_for_path(search_path);
                var enumerator = dir.enumerate_children(FILE_ATTRIBUTE_STANDARD_NAME, 0);
                FileInfo info;
                while ((info = enumerator.next_file()) != null) {
                    plugins.add(new PluginModule<SomePlugin>(search_path + "/" + info.get_name()));
                }
            }
            catch (Error e) {
                stderr.printf ("Error: %s\n", e.message);
            }
        }
    }
}
