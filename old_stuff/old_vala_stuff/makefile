#### Makefile for libvoxelpress and voxelcore

# commands
VC = valac
CC = gcc

# paths
libvp = libvoxelpress
vcore = voxelcore
plugin = voxelcore/plugins

# compiler flags
COMMON_VFLAGS = --pkg gee-1.0 --pkg gio-2.0 --pkg gmodule-2.0
PLUGIN_VFLAGS = bin/libvoxelpress.vapi -C
PLUGIN_CFLAGS = -shared -fPIC $$(pkg-config --cflags --libs glib-2.0 gmodule-2.0 gee-1.0 gio-2.0) -I./bin libvoxelpress.so
LIBVPRESS_VFLAGS = --library=libvoxelpress -H bin/libvoxelpress.h -X -lm -X -fPIC -X -shared -o libvoxelpress.so
VOXELCORE_VFLAGS = --thread bin/libvoxelpress.vapi --pkg json-glib-1.0 -X libvoxelpress.so -X -I./bin -o bin/voxelpress

# source code files
LIBVPRESS_SRC = $(libvp)/debug.vala \
		$(libvp)/vector_model.vala \
		$(libvp)/vector_math.vala \
		$(libvp)/fragments.vala \
		$(libvp)/voxel_model.vala \
		$(libvp)/plugin_api.vala \
		$(libvp)/btree.vala

VOXELCORE_SRC = $(vcore)/plugin_repository.vala \
		$(vcore)/import_stage.vala \
		$(vcore)/vector_stage.vala \
		$(vcore)/voxel_stage.vala \
		$(vcore)/vector_fragmentation.vala \
		$(vcore)/threading.vala \
		$(vcore)/export_demo.vala \
		$(vcore)/voxelcore.vala

# plugin specific stuff
IMPORT_OBJ_VFLAGS = $(plugin)/import/obj_model.vala
IMPORT_OBJ_CFLAGS = $(plugin)/import/obj_model.c -o bin/plugins/import/obj_model.so

VECTOR_DERP_VFLAGS = $(plugin)/vector/derp.vala
VECTOR_DERP_CFLAGS = $(plugin)/vector/derp.c -o bin/plugins/vector/derp.so

VECTOR_SCALE_VFLAGS = $(plugin)/vector/scale.vala
VECTOR_SCALE_CFLAGS =  $(plugin)/vector/scale.c -o bin/plugins/vector/scale.so




#### targets

all: reset_build build_folder libvoxelpress voxelcore plugins quick_run


libvoxelpress:
	echo ""
	echo "------ libvoxelpress ------"
	$(VC) $(COMMON_VFLAGS) $(LIBVPRESS_VFLAGS) $(LIBVPRESS_SRC)
	mv libvoxelpress.vapi bin/
	cp libvoxelpress.so bin/


voxelcore:
	echo ""
	echo "------ voxelcore ------"
	$(VC) $(COMMON_VFLAGS) $(VOXELCORE_VFLAGS) $(VOXELCORE_SRC)


plugins: import_plugins vector_plugins
	echo ""
	echo "------ cleanup stray .c files for plugins ------"
	rm $(plugin)/*/*.c


import_plugins:
	echo ""
	echo "------ import plugin obj-model ------"
	$(VC) $(PLUGIN_VFLAGS) $(IMPORT_OBJ_VFLAGS) $(COMMON_VFLAGS)
	$(CC) $(PLUGIN_CFLAGS) $(IMPORT_OBJ_CFLAGS)


vector_plugins:
	echo ""
	echo "------ vector plugin derp-adjustment ------"
	$(VC) $(PLUGIN_VFLAGS) $(VECTOR_DERP_VFLAGS) $(COMMON_VFLAGS)
	$(CC) $(PLUGIN_CFLAGS) $(VECTOR_DERP_CFLAGS)

	echo ""
	echo "------ vector plugin scale ------"
	$(VC) $(PLUGIN_VFLAGS) $(VECTOR_SCALE_VFLAGS) $(COMMON_VFLAGS)
	$(CC) $(PLUGIN_CFLAGS) $(VECTOR_SCALE_CFLAGS)


reset_build: 
	rm --force test_voxelpress.sh
	rm --force -R bin


build_folder:
	mkdir bin
	mkdir bin/plugins
	mkdir bin/plugins/import
	mkdir bin/plugins/vector
	mkdir bin/plugins/voxel
	mkdir bin/plugins/export
	mkdir bin/backends


quick_run:
	rm libvoxelpress.so
	echo ""
	echo "------ generating quickrun script ------"
	echo "cd bin; LD_LIBRARY_PATH=. ./voxelpress \$$@" >> test_voxelpress.sh
	chmod +x test_voxelpress.sh
