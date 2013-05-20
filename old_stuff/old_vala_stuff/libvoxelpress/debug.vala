using libvoxelpress.vectors;

namespace libvoxelpress.debug {
    public void print_vector (Vec3 vector) {
        double a = vector.data[0];
        double b = vector.data[1];
        double c = vector.data[2];
        stdout.printf(@" ( $a, $b, $c )");
    }

    public void print_face (Face face) {
        stdout.printf("Vertices:");
        for (int i=0; i<3; i+=1) {
            print_vector(face.vertices[i]);
        }
        stdout.printf("\n");
        stdout.printf("normals:");
        for (int i=0; i<3; i+=1) {
            print_vector(face.normals[i]);
        }
        stdout.printf("\n");
    }
}