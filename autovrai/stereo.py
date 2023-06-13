import numpy as np
from numba import njit, prange
from PIL import Image


def combine_stereo(left, right):
    return Image.fromarray(np.hstack([left, right]))


def combine_anaglyph(left, right):
    return Image.fromarray(generate_anaglyph(left, right))


def combine_padded(left, right, width, height, color):
    left_image = Image.fromarray(left)
    right_image = Image.fromarray(right)

    image = Image.new("RGB", (2 * width, height), color)
    image.paste(
        left_image,
        (width // 2 - left_image.width // 2, height // 2 - left_image.height // 2),
    )
    image.paste(
        right_image,
        (
            width + width // 2 - right_image.width // 2,
            height // 2 - right_image.height // 2,
        ),
    )

    return image


def stereo_eyes(
    image: Image,
    depth: np.ndarray,
    divergence: float,
    fill_technique="polylines_sharp",
):
    original = np.array(image)
    width = original.shape[1]

    depth_min = depth.min()
    depth_max = depth.max()
    depth_normal = (depth - depth_min) / (depth_max - depth_min)

    diverge_pixels = ((divergence / 2) / 100.0) * width

    left = apply_stereo_divergence_polylines(
        original, depth_normal, diverge_pixels, fill_technique
    )
    right = apply_stereo_divergence_polylines(
        original, depth_normal, diverge_pixels * -1, fill_technique
    )

    return left, right


@njit(parallel=True)  # fastmath=True does not reasonably improve performance
def apply_stereo_divergence_polylines(
    original_image, normalized_depth, divergence_px: float, fill_technique
):
    # This code treats rows of the image as polylines
    # It generates polylines, morphs them (applies divergence) to them, and then rasterizes them
    EPSILON = 1e-7
    PIXEL_HALF_WIDTH = 0.45 if fill_technique == "polylines_sharp" else 0.0
    # PERF_COUNTERS = [0, 0, 0]

    h, w, c = original_image.shape
    derived_image = np.zeros_like(original_image)
    for row in prange(h):
        # generating the vertices of the morphed polyline
        # format: new coordinate of the vertex, divergence (closeness), column of pixel that contains the point's color
        pt = np.zeros((5 + 2 * w, 3), dtype=np.float_)
        pt_end: int = 0
        pt[pt_end] = [-3.0 * abs(divergence_px), 0.0, 0.0]
        pt_end += 1
        for col in range(0, w):
            coord_d = (1 - normalized_depth[row][col] ** 2) * divergence_px
            coord_x = col + 0.5 + coord_d
            if PIXEL_HALF_WIDTH < EPSILON:
                pt[pt_end] = [coord_x, abs(coord_d), col]
                pt_end += 1
            else:
                pt[pt_end] = [coord_x - PIXEL_HALF_WIDTH, abs(coord_d), col]
                pt[pt_end + 1] = [coord_x + PIXEL_HALF_WIDTH, abs(coord_d), col]
                pt_end += 2
        pt[pt_end] = [w + 3.0 * abs(divergence_px), 0.0, w - 1]
        pt_end += 1

        # generating the segments of the morphed polyline
        # format: coord_x, coord_d, color_i of the first point, then the same for the second point
        sg_end: int = pt_end - 1
        sg = np.zeros((sg_end, 6), dtype=np.float_)
        for i in range(sg_end):
            sg[i] += np.concatenate((pt[i], pt[i + 1]))
        # Here is an informal proof that this (morphed) polyline does not self-intersect:
        # Draw a plot with two axes: coord_x and coord_d. Now draw the original line - it will be positioned at the
        # bottom of the graph (that is, for every point coord_d == 0). Now draw the morphed line using the vertices of
        # the original polyline. Observe that for each vertex in the new polyline, its increments
        # (from the corresponding vertex in the old polyline) over coord_x and coord_d are in direct proportion.
        # In fact, this proportion is equal for all the vertices and it is equal either -1 or +1,
        # depending on the sign of divergence_px. Now draw the lines from each old vertex to a corresponding new vertex.
        # Since the proportions are equal, these lines have the same angle with an axe and are parallel.
        # So, these lines do not intersect. Now rotate the plot by 45 or -45 degrees and observe that
        # each dot of the polyline is further right from the last dot,
        # which makes it impossible for the polyline to self-interset. QED.

        # sort segments and points using insertion sort
        # has a very good performance in practice, since these are almost sorted to begin with
        for i in range(1, sg_end):
            u = i - 1
            while pt[u][0] > pt[u + 1][0] and 0 <= u:
                pt[u], pt[u + 1] = np.copy(pt[u + 1]), np.copy(pt[u])
                sg[u], sg[u + 1] = np.copy(sg[u + 1]), np.copy(sg[u])
                u -= 1

        # rasterizing
        # at each point in time we keep track of segments that are "active" (or "current")
        csg = np.zeros((5 * int(abs(divergence_px)) + 25, 6), dtype=np.float_)
        csg_end: int = 0
        sg_pointer: int = 0
        # and index of the point that should be processed next
        pt_i: int = 0
        for col in range(
            w
        ):  # iterate over regions (that will be rasterizeed into pixels)
            color = np.full(
                c, 0.5, dtype=np.float_
            )  # we start with 0.5 because of how floats are converted to ints
            while pt[pt_i][0] < col:
                pt_i += 1
            pt_i -= 1  # pt_i now points to the dot before the region start
            # Finding segment' parts that contribute color to the region
            while pt[pt_i][0] < col + 1:
                coord_from = max(col, pt[pt_i][0]) + EPSILON
                coord_to = min(col + 1, pt[pt_i + 1][0]) - EPSILON
                significance = coord_to - coord_from
                # the color at center point is the same as the average of color of segment part
                coord_center = coord_from + 0.5 * significance

                # adding semgents that now may contribute
                while sg_pointer < sg_end and sg[sg_pointer][0] < coord_center:
                    csg[csg_end] = sg[sg_pointer]
                    sg_pointer += 1
                    csg_end += 1
                # removing segments that will no longer contribute
                csg_i = 0
                while csg_i < csg_end:
                    if csg[csg_i][3] < coord_center:
                        csg[csg_i] = csg[csg_end - 1]
                        csg_end -= 1
                    else:
                        csg_i += 1
                # finding the closest segment (segment with most divergence)
                # note that this segment will be the closest from coord_from right up to coord_to, since there
                # no new segments "appearing" inbetween these two and _the polyline does not self-intersect_
                best_csg_i: int = 0
                # PERF_COUNTERS[0] += 1
                if csg_end != 1:
                    # PERF_COUNTERS[1] += 1
                    best_csg_closeness: float = -EPSILON
                    for csg_i in range(csg_end):
                        ip_k = (coord_center - csg[csg_i][0]) / (
                            csg[csg_i][3] - csg[csg_i][0]
                        )
                        # assert 0.0 <= ip_k <= 1.0
                        closeness = (1.0 - ip_k) * csg[csg_i][1] + ip_k * csg[csg_i][4]
                        if best_csg_closeness < closeness and 0.0 < ip_k < 1.0:
                            best_csg_closeness = closeness
                            best_csg_i = csg_i
                # getting the color
                col_l: int = int(csg[best_csg_i][2] + EPSILON)
                col_r: int = int(csg[best_csg_i][5] + EPSILON)
                if col_l == col_r:
                    color += original_image[row][col_l] * significance
                else:
                    # PERF_COUNTERS[2] += 1
                    ip_k = (coord_center - csg[best_csg_i][0]) / (
                        csg[best_csg_i][3] - csg[best_csg_i][0]
                    )
                    color += (
                        original_image[row][col_l] * (1.0 - ip_k)
                        + original_image[row][col_r] * ip_k
                    ) * significance
                pt_i += 1
            derived_image[row][col] = np.asarray(color, dtype=np.uint8)
    # print(PERF_COUNTERS)
    return derived_image


@njit(parallel=True)
def generate_anaglyph(left, right):
    if left.shape != right.shape:
        raise ValueError(
            "Images for the left and right eye must be the same size for an anaglyph"
        )

    height = left.shape[0]
    width = left.shape[1]

    # final image container
    anaglyph = np.zeros((height, width, 3), np.uint8)

    for h in prange(height):
        for w in range(width):
            # red channel is from left image/eye
            anaglyph[h, w, 0] = left[h, w, 0]
            # blue/green channels are from right image/eye
            anaglyph[h, w, 1] = right[h, w, 1]
            anaglyph[h, w, 2] = right[h, w, 2]

    return anaglyph
