import os
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter

import autovrai


def handle_tiles(model, image, low_res_depth):
    autovrai.print_current_datetime("Starting combine process")
    if not os.path.exists("combined"):
        os.makedirs("combined")

    low_res_scaled_depth = 2**16 - (
        low_res_depth - np.min(low_res_depth)
    ) * 2**16 / (np.max(low_res_depth) - np.min(low_res_depth))
    autovrai.print_current_datetime("After scaling low res depth map")

    low_res_depth_map_image = Image.fromarray(
        (0.999 * low_res_scaled_depth).astype("uint16")
    )
    autovrai.print_current_datetime("After converting low res depth map to image")

    low_res_depth_map_image.save("zoe_depth_map_16bit_low.png")
    autovrai.print_current_datetime("After saving low res depth map image")

    im, filters, tile_sizes = generate_filters(image, save_filter_images=True)
    autovrai.print_current_datetime("After generating filters")

    compiled_tiles_list = apply_filters(
        model, im, filters, tile_sizes, low_res_scaled_depth, save_tiled_depth_map=True
    )
    autovrai.print_current_datetime("After applying filters")

    combined_result = combine_depthmaps(im, compiled_tiles_list, low_res_scaled_depth)
    autovrai.print_current_datetime("After combining depth maps")

    # not working as expected yet
    # inverted = cv2.bitwise_not(combined_result)
    # autovrai.print_current_datetime("After inverting depth map")

    return combined_result


def generate_filters(image, save_filter_images):
    # store filters in lists
    im = np.asarray(image)
    tile_sizes = [[4, 4], [8, 8]]
    filters = []
    # save_filter_images = True
    # save_tiled_depth_map = True

    for tile_size in tile_sizes:
        num_x = tile_size[0]
        num_y = tile_size[1]

        M = im.shape[0] // num_x
        N = im.shape[1] // num_y

        filter_dict = {}
        filter_dict["right_filter"] = np.zeros((M, N))
        filter_dict["left_filter"] = np.zeros((M, N))
        filter_dict["top_filter"] = np.zeros((M, N))
        filter_dict["bottom_filter"] = np.zeros((M, N))
        filter_dict["top_right_filter"] = np.zeros((M, N))
        filter_dict["top_left_filter"] = np.zeros((M, N))
        filter_dict["bottom_right_filter"] = np.zeros((M, N))
        filter_dict["bottom_left_filter"] = np.zeros((M, N))
        filter_dict["filter"] = np.zeros((M, N))

        # left_filter = np.zeros((M, N))
        # top_filter = np.zeros((M, N))
        # bottom_filter = np.zeros((M, N))

        # top_right_filter = np.zeros((M, N))
        # top_left_filter = np.zeros((M, N))
        # bottom_right_filter = np.zeros((M, N))
        # bottom_left_filter = np.zeros((M, N))

        # filter = np.zeros((M, N))

        for i in range(M):
            for j in range(N):
                x_value = 0.998 * np.cos((abs(M / 2 - i) / M) * np.pi) ** 2
                y_value = 0.998 * np.cos((abs(N / 2 - j) / N) * np.pi) ** 2

                if j > N / 2:
                    filter_dict["right_filter"][i, j] = x_value
                else:
                    filter_dict["right_filter"][i, j] = x_value * y_value

                if j < N / 2:
                    filter_dict["left_filter"][i, j] = x_value
                else:
                    filter_dict["left_filter"][i, j] = x_value * y_value

                if i < M / 2:
                    filter_dict["top_filter"][i, j] = y_value
                else:
                    filter_dict["top_filter"][i, j] = x_value * y_value

                if i > M / 2:
                    filter_dict["bottom_filter"][i, j] = y_value
                else:
                    filter_dict["bottom_filter"][i, j] = x_value * y_value

                if j > N / 2 and i < M / 2:
                    filter_dict["top_right_filter"][i, j] = 0.998
                elif j > N / 2:
                    filter_dict["top_right_filter"][i, j] = x_value
                elif i < M / 2:
                    filter_dict["top_right_filter"][i, j] = y_value
                else:
                    filter_dict["top_right_filter"][i, j] = x_value * y_value

                if j < N / 2 and i < M / 2:
                    filter_dict["top_left_filter"][i, j] = 0.998
                elif j < N / 2:
                    filter_dict["top_left_filter"][i, j] = x_value
                elif i < M / 2:
                    filter_dict["top_left_filter"][i, j] = y_value
                else:
                    filter_dict["top_left_filter"][i, j] = x_value * y_value

                if j > N / 2 and i > M / 2:
                    filter_dict["bottom_right_filter"][i, j] = 0.998
                elif j > N / 2:
                    filter_dict["bottom_right_filter"][i, j] = x_value
                elif i > M / 2:
                    filter_dict["bottom_right_filter"][i, j] = y_value
                else:
                    filter_dict["bottom_right_filter"][i, j] = x_value * y_value

                if j < N / 2 and i > M / 2:
                    filter_dict["bottom_left_filter"][i, j] = 0.998
                elif j < N / 2:
                    filter_dict["bottom_left_filter"][i, j] = x_value
                elif i > M / 2:
                    filter_dict["bottom_left_filter"][i, j] = y_value
                else:
                    filter_dict["bottom_left_filter"][i, j] = x_value * y_value

                filter_dict["filter"][i, j] = x_value * y_value

        filters.append(filter_dict)

        if save_filter_images:
            for filter in list(filter_dict.keys()):
                filter_image = Image.fromarray(
                    (filter_dict[filter] * 2**16).astype("uint16")
                )
                filter_image.save(
                    os.path.join("combined", f"mask_{filter}_{num_x}_{num_y}.png")
                )

    return im, filters, tile_sizes


def apply_filters(
    model, im, filters, tile_sizes, low_res_scaled_depth, save_tiled_depth_map
):
    compiled_tiles_list = []
    for i in range(len(filters)):
        num_x = tile_sizes[i][0]
        num_y = tile_sizes[i][1]

        M = im.shape[0] // num_x
        N = im.shape[1] // num_y

        compiled_tiles = np.zeros((im.shape[0], im.shape[1]))

        x_coords = list(range(0, im.shape[0], im.shape[0] // num_x))[:num_x]
        y_coords = list(range(0, im.shape[1], im.shape[1] // num_y))[:num_y]

        x_coords_between = list(
            range((im.shape[0] // num_x) // 2, im.shape[0], im.shape[0] // num_x)
        )[: num_x - 1]
        y_coords_between = list(
            range((im.shape[1] // num_y) // 2, im.shape[1], im.shape[1] // num_y)
        )[: num_y - 1]

        x_coords_all = x_coords + x_coords_between
        y_coords_all = y_coords + y_coords_between

        autovrai.print_current_datetime(
            f"Starting tiles for filter {i} of {len(filters)}"
        )
        print("--- AutoVR.ai ---", "x_coords_all:", x_coords_all)
        print("--- AutoVR.ai ---", "y_coords_all:", y_coords_all)

        for x in x_coords_all:
            for y in y_coords_all:
                autovrai.print_current_datetime(f"Starting tile {x} {y}")

                depth = model.infer_pil(
                    Image.fromarray(np.uint8(im[x : x + M, y : y + N]))
                )

                scaled_depth = 2**16 - (depth - np.min(depth)) * 2**16 / (
                    np.max(depth) - np.min(depth)
                )

                if y == min(y_coords_all) and x == min(x_coords_all):
                    selected_filter = filters[i]["top_left_filter"]
                elif y == min(y_coords_all) and x == max(x_coords_all):
                    selected_filter = filters[i]["bottom_left_filter"]
                elif y == max(y_coords_all) and x == min(x_coords_all):
                    selected_filter = filters[i]["top_right_filter"]
                elif y == max(y_coords_all) and x == max(x_coords_all):
                    selected_filter = filters[i]["bottom_right_filter"]
                elif y == min(y_coords_all):
                    selected_filter = filters[i]["left_filter"]
                elif y == max(y_coords_all):
                    selected_filter = filters[i]["right_filter"]
                elif x == min(x_coords_all):
                    selected_filter = filters[i]["top_filter"]
                elif x == max(x_coords_all):
                    selected_filter = filters[i]["bottom_filter"]
                else:
                    selected_filter = filters[i]["filter"]

                compiled_tiles[x : x + M, y : y + N] += selected_filter * (
                    np.mean(low_res_scaled_depth[x : x + M, y : y + N])
                    + np.std(low_res_scaled_depth[x : x + M, y : y + N])
                    * ((scaled_depth - np.mean(scaled_depth)) / np.std(scaled_depth))
                )

        compiled_tiles[compiled_tiles < 0] = 0
        compiled_tiles_list.append(compiled_tiles)

        if save_tiled_depth_map:
            tiled_depth_map = Image.fromarray(
                (2**16 * 0.999 * compiled_tiles / np.max(compiled_tiles)).astype(
                    "uint16"
                )
            )
            tiled_depth_map.save(os.path.join("combined", f"tiled_depth_{i}.png"))

    return compiled_tiles_list


def combine_depthmaps(im, compiled_tiles_list, low_res_scaled_depth):
    save_mask_image = False

    grey_im = np.mean(im, axis=2)

    tiles_blur = gaussian_filter(grey_im, sigma=20)
    tiles_difference = tiles_blur - grey_im

    # np.clip(tiles_difference, 0,  np.max(tiles_difference))
    tiles_difference = tiles_difference / np.max(tiles_difference)
    tiles_difference = gaussian_filter(tiles_difference, sigma=40)
    tiles_difference *= 5
    tiles_difference = np.clip(tiles_difference, 0, 0.999)

    if save_mask_image:
        mask_image = Image.fromarray((tiles_difference * 2**16).astype("uint16"))
        mask_image.save(os.path.join("combined", "mask_image.png"))

    combined_result = (
        tiles_difference * compiled_tiles_list[1]
        + (1 - tiles_difference) * ((compiled_tiles_list[0] + low_res_scaled_depth) / 2)
    ) / (2)

    # combined_image = Image.fromarray(
    #     (2**16 * 0.999 * combined_result / np.max(combined_result)).astype("uint16")
    # )
    # combined_image.save(os.path.join("combined", "combined_image.png"))

    return combined_result
