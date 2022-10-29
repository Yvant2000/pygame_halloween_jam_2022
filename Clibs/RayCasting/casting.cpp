#include <Python.h>
#define _USE_MATH_DEFINES
#include <cmath>

#define EPSILON 0.001f

#define ALPHA 1
#define RED 0
#define GREEN -1
#define BLUE -2

#define P_RED 3
#define P_GREEN 2
#define P_BLUE 1
#define P_ALPHA 0

#define MIN(a, b) ((a) < (b) ? (a) : (b))
#define MAX(a, b) ((a) > (b) ? (a) : (b))

typedef struct t_RayCasterObject{
    PyObject_HEAD
    struct Surface *surfaces = nullptr;
    struct Light *lights = nullptr;
    bool use_lighting = false;
} RayCasterObject;

typedef struct vec3 {
    /*
        y
        |  z
        | /
        O --- x
    */
    float x;
    float y;
    float z;
} vec3;

struct pos2 {
    /* For a segment, the start point and end point.
        A [---------] B
    */
    /* For a line, a point and a direction.
        ------ A ------ B ->
    */
    vec3 A;
    vec3 B;
};

struct pos3 {
    /* For a rectangle, the two opposite corners and the normal
        A ------ *
        |  C ->  |
        * ------ B
    */
    vec3 A;
    vec3 B;
    vec3 C;
};

struct Light {
    vec3 pos;  // Position of the light in the scene
    vec3 direction;  // Direction of the light in the scene
    float intensity; // Intensity of the light (= the distance of lightning)
    float r; // Red component of the light
    float g; // Green component of the light
    float b; // Blue component of the light
    struct Light *next;
};


struct Surface {
    struct Surface *next;  // The next surface in the list
    PyObject *parent;  // The parent py_object
    struct pos3 pos;  // The position of the surface
    vec3 bc;  // barycentric coordinates
    Py_buffer buffer;  // The buffer of the surface
    float distance;
    bool del;  // If the surface is volatile and need to be deleted
};

inline void free_surface(struct Surface *surface) {
    PyBuffer_Release(&(surface->buffer));
    Py_DECREF(surface->parent);
    free(surface);
}

inline void free_temp_surfaces(struct Surface **surfaces) {
    /*
     * Takes a double ptr surfaces and remove from the chained list all surfaces
     * that have the "del" attribute set to true.
     * When a surface is removed, it needs to be freed with the free_surface function.
     * If the new list is empty, surfaces is set to nullptr.
     */

    struct Surface *prev = nullptr;
    struct Surface *next;
    for (struct Surface *current = *surfaces; current != nullptr; current = next) {
        next = current->next;
        if (current->del) {
            free_surface(current);
            if (prev == nullptr)
                *surfaces = next;
            else
                prev->next = next;
        } else
            prev = current;
    }

}

// static struct Surface *SURFACES = nullptr;

inline vec3 vec3_add(vec3 a, vec3 b) {
    vec3 result = {a.x + b.x, a.y + b.y, a.z + b.z};
    return result;
}

/*
 * A - B
 */
inline vec3 vec3_sub(vec3 a, vec3 b) {
    vec3 result = {a.x - b.x, a.y - b.y, a.z - b.z};
    return result;
}

inline float vec3_dot(vec3 a, vec3 b) {
    return a.x * b.x + a.y * b.y + a.z * b.z;
}

inline vec3 vec3_dot_float(vec3 a, float b) {
    vec3 result = {a.x * b, a.y * b, a.z * b};
    return result;
}

inline vec3 vec3_cross(vec3 a, vec3 b) {
    vec3 result = {a.y * b.z - a.z * b.y,
                   a.z * b.x - a.x * b.z,
                   a.x * b.y - a.y * b.x};
    return result;
}

inline float vec3_length(vec3 a) {
    return sqrtf(a.x * a.x + a.y * a.y + a.z * a.z);
}

inline float vec3_dist(vec3 dot1, vec3 dot2) {
    return sqrtf(powf(dot1.x - dot2.x, 2) + powf(dot1.y - dot2.y, 2) + powf(dot1.z - dot2.z, 2));
}

inline void get_norm_of_plane(vec3 A, vec3 B, vec3 C, vec3 *norm) {

    vec3 AC = vec3_sub(A, C);
    vec3 BC = vec3_sub(B, C);

    *norm = vec3_cross(AC, BC);
}


/*
 * Returns the distance from a point to a line.
 */
inline float line_point_distance(vec3 point, vec3 line_point, vec3 line_direction) {
    vec3 s = vec3_sub(line_direction, line_point);
    vec3 w = vec3_sub(point, line_point);
    float ps = vec3_dot(w, s);

    if (ps <= 0)
        return vec3_length(w);

    float l2 = vec3_dot(s, s);
    if (ps >= l2)
        return vec3_length(vec3_sub(point, line_direction));

    return vec3_length(vec3_sub(point, vec3_add(line_point, vec3_dot_float(s, ps / l2))));
}


inline bool line_plane_collision(vec3 plane_point, vec3 plane_normal,
                                 vec3 line_point, vec3 line_direction,
                                 vec3* intersection) {
    /*
        Compute the intersection of a line and a plane.
        The line is defined by a point and a direction
        The plane is defined by a point and a normal
        The intersection is the point (vec3) where the line intersects the plane

        @return: true if the line intersects the plane, false otherwise
    */
    float normal_dot_direction = vec3_dot(plane_normal, line_direction);
    if (abs(normal_dot_direction) < EPSILON)
        return false; // The line is parallel to the plane.

    vec3 w = vec3_sub(line_point, plane_point);
    float fac = -vec3_dot(plane_normal, w) / normal_dot_direction;
    if (fac < 0 || fac > 1) // The intersection is outside the segment
        return false;
    *intersection = vec3_add(
                        line_point,
                        vec3_dot_float(
                            line_direction,
                            fac)
                        );

    return true;
}

/*
    Compute the intersection of a segment and a surface.
    @param segment: the segment
    The segment is defined by it's start point, a direction/end point
        segment.A = point
        segment.B = direction
    @param plane: the surface
    The surface is defined by it's start point, an end point and a normal.
        plane.A = point
        plane.B = end point
        plane.C = normal
    @param intersection: the point where the segment intersects the plane
    The intersection is set if the line intersects with the plane, even if
    the segment does not intersect with the surface.
        intersection.(x,y,z) = point

    @return: true if the segment intersects the surface, false otherwise
*/
inline bool segment_plane_collision(struct pos3 plane, struct pos2 segment,
                                    vec3 *intersection, float *distance) {

    if (!line_plane_collision(plane.A, plane.C, segment.A, segment.B, intersection))
        return false; // The segment is parallel to the plane.

    *distance = vec3_dist(segment.A, *intersection);

    if (*distance > vec3_length(segment.B))
        return false; // The intersection is outside the segment.

    if (*distance < EPSILON)
        return false; // The distance is null.

    vec3 i = *intersection;
    // Now we need to check if the intersection is between the surface's points.
    if (
        (EPSILON < plane.A.x-i.x && EPSILON < plane.B.x-i.x) || (i.x-plane.A.x > EPSILON && i.x-plane.B.x > EPSILON)
        || (EPSILON < plane.A.y-i.y && EPSILON < plane.B.y-i.y) || (i.y-plane.A.y > EPSILON && i.y-plane.B.y > EPSILON)
        || (EPSILON < plane.A.z-i.z && EPSILON < plane.B.z-i.z) || (i.z-plane.A.z > EPSILON && i.z-plane.B.z > EPSILON)
       )
        return false; // The intersection is outside the surface.

    return true;

}

inline unsigned char *get_pixel_3d(struct Surface *surface, vec3 point) {
    vec3 ab = vec3_sub(surface->bc, surface->pos.A);
    vec3 av = vec3_sub(point, surface->pos.A);

    float x_dist = vec3_length(vec3_cross(ab, av)) / vec3_length(ab);
    float x_len = vec3_dist(surface->bc, surface->pos.B);
    Py_ssize_t width = surface->buffer.shape[0];
    Py_ssize_t x = (Py_ssize_t)(x_dist * width / x_len);
    if (x < 0 || x >= width)
        return nullptr;

    vec3 bc = vec3_sub(surface->pos.B, surface->bc);
    vec3 bv = vec3_sub(point, surface->bc);

    float y_dist = vec3_length(vec3_cross(bc, bv)) / vec3_length(bc);
    float y_len = vec3_dist(surface->bc, surface->pos.A);
    Py_ssize_t height = surface->buffer.shape[1];
    Py_ssize_t y = height - (Py_ssize_t)(y_dist * height / y_len);

    if (y >= height || y < 0)
        return nullptr;

    long *buf = (long *)surface->buffer.buf;
    long *pixel = buf + (y * width + x);
    return (unsigned char*) pixel;
}


inline unsigned long get_pixel_sum(struct pos2 ray, struct Surface *surface, struct Light *lights, float max_dist, bool use_lights) {
    unsigned long pixel = 0;  // alloc 4 bytes for the pixel

    unsigned char *pixel_ptr = (unsigned char*)&pixel;  // Get the pointer to the pixel
    float min_distance = max_dist;  // The distance to the closest surface found so far
    vec3 inter;
    for (; surface != nullptr; surface = surface->next) {  // For each surface

        vec3 intersection;
        float distance;
        if (!segment_plane_collision(surface->pos, ray, &intersection, &distance))  // Make sure the ray intersects the surface
            continue;

        if (distance >= min_distance)  // Then check if the surface is closer than the closest one found so far
            continue;  // If the surface is further than the closest one, skip it

        unsigned char *new_pixel_ptr = get_pixel_3d(surface, intersection);  // Get the pixel from the surface
        if (new_pixel_ptr == nullptr || new_pixel_ptr[ALPHA] == 0)  // If for some reason the pixel is null or transparent, skip it
            continue;

        min_distance = distance;  // We found a closer surface, so update the min_distance
        inter = intersection;

        float quotient = (1.0f - distance / max_dist);

        pixel_ptr[P_BLUE] = (unsigned char)(new_pixel_ptr[BLUE] * quotient);  // Set the pixel's blue value
        pixel_ptr[P_GREEN] = (unsigned char)(new_pixel_ptr[GREEN] * quotient);  // Set the pixel's green value
        pixel_ptr[P_RED] = (unsigned char)(new_pixel_ptr[RED] * quotient);  // Set the pixel's red value
        //pixel = (unsigned long)(*((unsigned long *)(new_pixel_ptr - 3)));  // Copy the pixel to the pixel pointer
    }

    if (use_lights && pixel) {
        float red = 0.0f;
        float green = 0.0f;
        float blue = 0.0f;
        for (struct Light* temp_light = lights; temp_light != nullptr; temp_light = temp_light->next) {
            float dist = vec3_dist(temp_light->pos, inter);  // distance between the light and the intersection
            float ratio;
            if (temp_light->direction.x == FP_NAN){  // if the light is a point light, calculate the ratio
                ratio = dist / temp_light->intensity;
            } else {  // if the light is a directional light, calculate the ratio
                float dist2 = line_point_distance(inter, temp_light->pos, temp_light->direction);  // distance between the direction and the intersection
                float dist3 = vec3_dist(temp_light->pos, temp_light->direction);  // distance between the light and the direction (further = concentrated)
                ratio = (dist2*dist3) / (dist*temp_light->intensity);
            }

            if (ratio < 1.0f) {  // ratio > 1 means the light is too far away, we don't see anything
                float temp = 1.0f - ratio;
                red += temp * temp_light->r;
                green += temp * temp_light->g;
                blue += temp * temp_light->b;
            }
        }
        // Prevent the pixel from being too bright
        if (red > 1.0f)
            red = 1.0f;
        if (green > 1.0f)
            green = 1.0f;
        if (blue > 1.0f)
            blue = 1.0f;

        pixel_ptr[P_BLUE] = (unsigned char)(pixel_ptr[P_BLUE] * blue);
        pixel_ptr[P_GREEN] = (unsigned char)(pixel_ptr[P_GREEN] * green);
        pixel_ptr[P_RED] = (unsigned char)(pixel_ptr[P_RED] * red);
    }

    pixel_ptr[P_ALPHA] = 0;  // Make sure the alpha is 0

    return pixel;
}

/*
 * Get the closest intersection between a ray and a list of surfaces.
 */
float get_closest_intersection(pos2 ray, float max_distance, struct Surface *surfaces) {
    float min_distance = max_distance;
    for (; surfaces != nullptr; surfaces = surfaces->next) {
        vec3 temp_intersection;
        float distance;
        if (!segment_plane_collision(surfaces->pos, ray, &temp_intersection, &distance))
            continue;

        if (distance >= min_distance)
            continue;

        unsigned char *new_pixel_ptr = get_pixel_3d(surfaces, temp_intersection);
        if (new_pixel_ptr == nullptr || new_pixel_ptr[ALPHA] == 0)
            continue;

        min_distance = distance;
    }

    return min_distance;
}

inline bool _get_3DBuffer_from_Surface(PyObject *img, Py_buffer *buffer) {
    PyObject * get_view_method = PyObject_GetAttrString(img, "get_view");
    if (get_view_method == NULL) {
        return true;
    }

    PyObject *arg = Py_BuildValue("y", "3");
    PyObject * view = PyObject_CallOneArg(get_view_method, arg); // array of width * height * RGBA

    Py_DECREF(arg);
    Py_DECREF(get_view_method);

    if (PyObject_GetBuffer(view, buffer, PyBUF_STRIDES) == -1) {
        Py_DECREF(view);
        return true;
    }

    Py_DECREF(view);

    return false;
}

//inline int count_surfaces(struct Surface *surface) {
//    int count;
//    for (count = 0; surface != nullptr; surface = surface->next)
//        count++;
//    return count;
//}
//
//inline void print_surfaces(struct Surface *surface) {
//    for (int i = 0; surface != nullptr; surface = surface->next, i++)
//        printf("Surface %d: %p\n", i, surface);
//    printf("\n");
//}

inline float get_closest(vec3 camera_pos, struct Surface *surface) {
//    float a_dist = vec3_dist(camera_pos, surface->pos.A);
//    float b_dist = vec3_dist(camera_pos, surface->pos.B);
//    return a_dist < b_dist ? a_dist : b_dist;
    return fabsf( vec3_dot(surface->pos.C, surface->pos.A) - vec3_dot(surface->pos.C, camera_pos)) / vec3_length(surface->pos.C);
}


/*
 * Sort all given Surface objects by their distance to the camera.
 */
inline void depth_sort(vec3 camera_pos, RayCasterObject* caster) {
    for (struct Surface *temp_surface = caster->surfaces; temp_surface != nullptr; temp_surface = temp_surface->next) {
        temp_surface->distance = get_closest(camera_pos, temp_surface);
    }

    bool swapped = true;
    while (swapped) {
        swapped = false;
        struct Surface *prev = nullptr;
        for (struct Surface *temp_surface = caster->surfaces; temp_surface->next != nullptr; temp_surface = temp_surface->next) {
            if (temp_surface->distance > temp_surface->next->distance) {
                swapped = true;
                struct Surface *temp = temp_surface->next;
                if (prev == nullptr) {
                    caster->surfaces = temp;
                    temp_surface->next = temp->next;
                    temp->next = temp_surface;
                } else {
                    prev->next = temp;
                    temp_surface->next = temp->next;
                    temp->next = temp_surface;
                }
                break;
            }

            prev = temp_surface;
        }
    }
}


static PyObject *method_add_surface(RayCasterObject *self, PyObject *args, PyObject *kwargs) {
    PyObject *surface_image;

    float A_x;
    float A_y;
    float A_z;

    float B_x;
    float B_y;
    float B_z;

    float C_x = FP_NAN;
    float C_y = FP_NAN;
    float C_z = FP_NAN;

    bool del = false;

    static char *kwlist[] = {"image", "A_x", "A_y", "A_z", "B_x", "B_y", "B_z","C_x", "C_y", "C_z", "rm",NULL};
    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "Offffff|fffp", kwlist,
                                     &surface_image, &A_x, &A_y, &A_z, &B_x, &B_y, &B_z, &C_x, &C_y, &C_z, &del))
        return NULL;

    struct Surface *surface = (Surface *) malloc(sizeof(struct Surface));
    surface->pos.A.x = A_x;
    surface->pos.A.y = A_y;
    surface->pos.A.z = A_z;
    surface->pos.B.x = B_x;
    surface->pos.B.y = B_y;
    surface->pos.B.z = B_z;
    surface->parent = surface_image;
    surface->del = del;

    if (_get_3DBuffer_from_Surface(surface_image, &(surface->buffer))) {
        PyErr_SetString(PyExc_ValueError, "Not a valid surface");
        free(surface);
        return NULL;
    }
    Py_INCREF(surface_image); // We need to keep the surface alive to make sure the buffer is valid.

    surface->next = self->surfaces; // Push the surface on top of the stack.
    self->surfaces = surface;

    vec3 C;
    if (C_x == FP_NAN || C_y == FP_NAN || C_z == FP_NAN)
        C = {A_x, B_y, A_z}; // define a new vector C bellow A and at the same level as B
    else
        C = {C_x, C_y, C_z};

    surface->bc = C;

    get_norm_of_plane(surface->pos.A, surface->pos.B, C, &(surface->pos.C));

    Py_RETURN_NONE;
}

static PyObject *method_add_light(RayCasterObject *self, PyObject *args, PyObject *kwargs) {

    float light_x;
    float light_y;
    float light_z;

    float light_intensity = 1.0;

    float red = 1.0;
    float green = 1.0;
    float blue = 1.0;

    float direction_x = FP_NAN;
    float direction_y = FP_NAN;
    float direction_z = FP_NAN;

    static char *kwlist[] = {"x", "y", "z", "intensity", "red", "green", "blue", "direction_x", "direction_y", "direction_z", NULL};
    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "fff|fffffff", kwlist, &light_x, &light_y, &light_z, &light_intensity,
                                     &red, &green, &blue, &direction_x, &direction_y, &direction_z))
        return NULL;

    if (red > 1.0f)
        red = 1.0f;
    if (green > 1.0f)
        green = 1.0f;
    if (blue > 1.0f)
        blue = 1.0f;

    struct Light *light = (Light *) malloc(sizeof(struct Light));
    light->pos.x = light_x;
    light->pos.y = light_y;
    light->pos.z = light_z;
    light->intensity = light_intensity;
    light->r = red;
    light->g = green;
    light->b = blue;
    light->direction.x = direction_x;
    light->direction.y = direction_y;
    light->direction.z = direction_z;
    light->next = self->lights;

    self->use_lighting = true;
    self->lights = light;

    Py_RETURN_NONE;
}

static PyObject *method_clear_surfaces(RayCasterObject *self) {
    struct Surface *next;
    for (struct Surface *surface = self->surfaces; surface != nullptr; surface = next) {
        next = surface->next;
        free_surface(surface);
    }
    self->surfaces = nullptr;
    Py_RETURN_NONE;
}

static PyObject *method_clear_lights(RayCasterObject *self) {
    struct Light *next;
    for (struct Light *light = self->lights; light != nullptr; light = next) {
        next = light->next;
        free(light);
    }
    self->lights = nullptr;
    self->use_lighting = false;
    Py_RETURN_NONE;
}

static PyObject *method_raycasting(RayCasterObject *self, PyObject *args, PyObject *kwargs) {
    PyObject *screen;

    float x = 0.f;
    float y = 0.f;
    float z = 0.f;

    float angle_x = 0.f;
    float angle_y = 0.f;

    float fov = 120.f;
    float view_distance = 1000.f;
    bool rad = false;

    static char *kwlist[] = {"dst_surface", "x", "y", "z", "angle_x", "angle_y", "fov", "view_distance", "rad", NULL};
    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "O|fffffffip", kwlist,
                                     &screen, &x, &y, &z, &angle_x, &angle_y, &fov, &view_distance, &rad))
        return NULL;

    if(fov <= 0.f) {
        PyErr_SetString(PyExc_ValueError, "fov must be greater than 0");
        return NULL;
    }
    if (view_distance <= 0.f) {
        PyErr_SetString(PyExc_ValueError, "view_distance must be greater than 0");
        return NULL;
    }

    Py_buffer dst_buffer;
    if (_get_3DBuffer_from_Surface(screen, &dst_buffer)) {
        PyErr_SetString(PyExc_ValueError, "dst_surface is not a valid surface");
        return NULL;
    }

    if (!rad) { // If the given angles are in degrees, convert them to radians.
        angle_x = angle_x * (float)M_PI / 180.f;
        angle_y = angle_y * (float)M_PI / 180.f;
        fov = fov * (float)M_PI / 180.f;
    }

    // x_angle is the angle of the ray around the x axis.
    // y_angle is the angle of the ray around the y axis.
    /*    y
        < | >   Λ
    ------ ------ x
          |     V
    */
    // It may be confusing because the x_angle move through the y axis,
    // and the y_angle move through the x axis as shown in the diagram.
    struct pos2 ray;
    ray.A = {x, y, z};


    Py_ssize_t width = dst_buffer.shape[0];  // width of the screen
    Py_ssize_t height = dst_buffer.shape[1];  // height of the screen

    long *buf = (long *)dst_buffer.buf;  // buffer to write the result in

    // TODO: iteration over the images to remove images that are not visible.
    depth_sort(ray.A, self);


    // compute a bunch of variables before the loop to avoid computing them at each iteration.

    float projection_plane_width = 2 * tan(fov);
    float projection_plane_height = projection_plane_width * (float)height / (float)width;

    float forward_x = cosf(angle_y) * view_distance;
    float forward_y = sinf(angle_x) * projection_plane_height * view_distance;
    float forward_z = sinf(angle_y) * view_distance;

    float right_x = -forward_z * projection_plane_width;
    float right_y = projection_plane_height * view_distance;
    float right_z = forward_x * projection_plane_width;

    float d_progress_y = 1.f / (float)height;
    float d_progress_x = 1.f / (float)width;

    float progress_y = 0.5f;

    for (Py_ssize_t dst_y = 0; dst_y < height; ++dst_y) {

        progress_y -= d_progress_y;

        ray.B.y = forward_y + progress_y * right_y;

        float progress_x = 0.5f;
        for (Py_ssize_t dst_x = 0; dst_x < width; ++dst_x) {

            progress_x -= d_progress_x;

            ray.B.x = forward_x + progress_x * right_x;
            ray.B.z = forward_z + progress_x * right_z;

            // Now that the ray is defined, compute the pixel color.
            unsigned long pixel = get_pixel_sum(ray, self->surfaces, self->lights, view_distance, self->use_lighting);
            if (pixel != 0)   // If the pixel is empty, don't write it.
                *((unsigned long *) ((unsigned char *) (buf) - 3)) = pixel;
            buf += 1;
        }
    }

    PyBuffer_Release(&dst_buffer);

    free_temp_surfaces(&(self->surfaces));

    Py_RETURN_NONE;
}


/*
 *  compute a single raycast and return the position in space of the closest intersection.
 */
static PyObject *method_single_cast(RayCasterObject *self, PyObject *args, PyObject *kwargs) {
    float origin_x = 0.f;
    float origin_y = 0.f;
    float origin_z = 0.f;

    float angle_x = 0.f;
    float angle_y = 0.f;

    float max_distance = 1000.f;

    bool rad = false;

    static char *kwlist[] = {"x", "y", "z", "angle_x", "angle_y", "max_distance", "rad", NULL};
    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "|ffffffp", kwlist,
                                     &origin_x, &origin_y, &origin_z, &angle_x, &angle_y, &max_distance, &rad))
        return NULL;

    if (max_distance <= 0.f) {
        PyErr_SetString(PyExc_ValueError, "max_distance must be greater than 0");
        return NULL;
    }

    if (!rad) { // If the given angles are in degrees, convert them to radians.
        angle_x = angle_x * (float)M_PI / 180.f;
        angle_y = angle_y * (float)M_PI / 180.f;
    }

    struct pos2 ray;
    ray.A = {origin_x, origin_y, origin_z};
    ray.B = {cosf(angle_y) * max_distance, sinf(angle_x) * max_distance, sinf(angle_y) * max_distance};

    return Py_BuildValue("f", get_closest_intersection(ray, max_distance, self->surfaces));
}


void RayCaster_dealloc(RayCasterObject *self) {
    struct Surface *next;
    for (struct Surface *surface = self->surfaces; surface != nullptr; surface = next) {
        next = surface->next;
        free_surface(surface);
    }
    Py_TYPE(self)->tp_free((PyObject *)self);
}


static PyMethodDef CasterMethods[] = {
        {"add_surface", (PyCFunction) method_add_surface, METH_VARARGS | METH_KEYWORDS, "Adds a surface to the caster."},
        {"clear_surfaces", (PyCFunction) method_clear_surfaces, METH_NOARGS, "Clears all surfaces from the caster."},
        {"add_light", (PyCFunction) method_add_light, METH_VARARGS | METH_KEYWORDS, "Adds a light to the scene."},
        {"clear_lights", (PyCFunction) method_clear_lights, METH_NOARGS, "Clears all lights from the caster."},
        {"raycasting", (PyCFunction) method_raycasting, METH_VARARGS | METH_KEYWORDS, "Display the scene using raycasting."},
        {"single_cast", (PyCFunction) method_single_cast, METH_VARARGS | METH_KEYWORDS, "Compute a single raycast and return the position in space of the closest intersection."},
        {NULL, NULL, 0, NULL}
};

static PyTypeObject RayCasterType = {
        .ob_base = PyVarObject_HEAD_INIT(NULL, 0)
        .tp_name = "nostalgiaeraycasting.RayCaster",
        .tp_basicsize = sizeof(RayCasterObject),
        .tp_itemsize = 0,
        .tp_dealloc = (destructor) RayCaster_dealloc,
        .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
        .tp_doc = PyDoc_STR("RayCaster Object"),
        .tp_methods = CasterMethods,
        .tp_new = PyType_GenericNew,
};


static struct PyModuleDef castermodule = {
    PyModuleDef_HEAD_INIT,
    "nostalgiaeraycasting",
    "Python ray casting module for pygame",
    -1,
};


PyMODINIT_FUNC PyInit_nostalgiaeraycasting(void) {
    if (PyType_Ready(&RayCasterType) < 0)
        return NULL;

    PyObject *m = PyModule_Create(&castermodule);

    if (m == NULL)
        return NULL;

    Py_INCREF(&RayCasterType);
    if (PyModule_AddObject(m, "RayCaster", (PyObject *)&RayCasterType) < 0) {
        Py_DECREF(&RayCasterType);
        Py_DECREF(m);
        return NULL;
    }

    return m;
}
