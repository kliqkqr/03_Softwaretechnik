use image::{ RgbImage,
             GenericImage, GenericImageView, Pixel };

use crate::base::{ range, clamp, uclamp };
use crate::img::{ RgbF };

// fn blur_box_horizontal(foreground : &RgbImage, left : i32, top : i32, width : u32, height : u32,
//                        horizontal_radii : &[u32])
//                        -> RgbImage {
//
//     let mut bubble = RgbImage::new(width, height);
//
//     for y_bubble in range(0, height) {
//         let y_foreground = top + y_bubble;
//
//         let x_clamped = clamp(left, foreground.width());
//         let y_clamped = clamp(y_foreground, foreground.height());
//         let mut average = RgbF::from(foreground.get_pixel(x_clamped, y_clamped));
//
//         let radius = horizontal_radii[0];
//         for i in range(1, radius + 1) {
//             let x_left    = clamp(left - i, foreground.width());
//             let x_right   = clamp(left + i, foreground.width());
//
//             let left  = RgbF::from(foreground.get_pixel(x_left,  y_clamped));
//             let right = RgbF::from(foreground.get_pixel(x_right, y_clamped));
//
//             average += left + right;
//         }
//
//         let scalar = 1f64 / ((radius * 2 + 1) as f64);
//         bubble.put_pixel(0, y_bubble, average.to_rgb(scalar));
//
//         let mut last_radius = radius;
//         for x in range(1, width) {
//             let radius     = horizontal_radii[x];
//             let radius_dif = last_radius as i32 - radius as i32;
//
//             let x_last_left  = x as i32 - 1 - last_radius;
//             let x_last_right = x as i32 - 1 + last_radius;
//
//             for x_sub in range(x_last_left, x_last_left + radius_dif + 1) {
//                 let x_clamped = clamp(x_sub, foreground.width());
//                 left_sub = RgbF::from(foreground.get_pixel(x_clamped, y_clamped));
//
//                 average -= left_sub;
//             }
//
//             for x_add in range(x_last_right, x_last_right - radius_dif + 1) {
//                 let x_clamped = clamp(x_add, foreground.width());
//                 left_add = RgbF::from(foreground.get_pixel(x_clamped, y_clamped));
//
//                 average += left_add;
//             }
//
//             let scalar = 1f64 ((radius * 2 + 1) as f64);
//             bubble.put_pixel(x, y_bubble, average.to_rgb(scalar));
//
//             last_radius = radius;
//         }
//     }
//
//     bubble
// }

// fn blur_box_horizontal(foreground : &RgbImage, left : i32, top : i32, width : u32, height : u32,
//                        horizontal_radii : &[u32])
//                        -> RgbImage {
//
//     let mut image = RgbImage::new(width, height);
//
//     for y_rectangle in range(0, height) {
//         let y_foreground = top + y_rectangle;
//
//         let x_clamped = clamp(left, foreground.width());
//         let y_clamped = clamp(y_foreground, foreground.height());
//         let mut average = RgbF::from(foreground.get_pixel(x_clamped, y_clamped));
//
//         let radius = horizontal_radii[0];
//         for i in range(1, radius + 1) {
//             let x_left  = clamp(left - i, foreground.width());
//             let x_right = clamp(left + i, foreground.width());
//
//             let left  = RgbF::from(foreground.get_pixel(x_left,  y_clamped));
//             let right = RgbF::from(foreground.get_pixel(x_right, y_clamped));
//
//             average += left + right;
//         }
//
//         let scalar = 1f64 / ((radius * 2 + 1) as f64);
//         image.put_pixel(0, y_rectangle, average.to_rgb(scalar));
//
//         let mut last_radius = radius;
//         for x in range(1, width) {
//             let radius     = horizontal_radii[x];
//             let radius_dif = last_radius as i32 - radius as i32;
//
//             let x_last_left  = x as i32 - 1 - last_radius;
//             let x_last_right = x as i32 - 1 + last_radius;
//
//             for x_sub in range(x_last_left, x_last_left + radius_dif + 1) {
//                 let x_clamped = clamp(x_sub, foreground.width());
//                 let left_sub = RgbF::from(foreground.get_pixel(x_clamped, y_clamped));
//
//                 average -= left_sub;
//             }
//
//             for x_add in range(x_last_right, x_last_right - radius_dif + 1) {
//                 let x_clamped = clamp(x_add, foreground.width());
//                 let right_add = RgbF::from(foreground.get_pixel(x_clamped, y_clamped));
//
//                 average += right_add;
//             }
//
//             let scalar = 1f64 ((radius * 2 + 1) as f64);
//             image.put_pixel(x, y_rectangle, average.to_rgb(scalar));
//
//             last_radius = radius;
//         }
//     }
//
//     image
// }

// fn blur_box_vertical(foreground : &RgbImage, left : i32, top : i32, width : u32, height : u32,
//                      vertical_radii : &[u32])
//                      -> RgbImage {
//
//     let mut image = RgbImage::new(foreground.width(), foreground.height());
//
//     for y_rectangle in range(0, height) {
//         let y_foreground = top + y_rectangle;
//
//         let x_clamped = clamp(left, foreground.width());
//         let y_clamped = clamp(y_foreground, foreground.height());
//         let mut average = RgbF::from(foreground.get_pixel(x_clamped, y_clamped));
//
//         let radius = horizontal_radii[0];
//         for i in range(1, radius + 1) {
//             let x_left    = clamp(left - i, foreground.width());
//             let x_right   = clamp(left + i, foreground.width());
//
//             let left  = RgbF::from(foreground.get_pixel(x_left,  y_clamped));
//             let right = RgbF::from(foreground.get_pixel(x_right, y_clamped));
//
//             average += left + right;
//         }
//
//         let scalar = 1f64 / ((radius * 2 + 1) as f64);
//         image.put_pixel(0, y_rectangle, average.to_rgb(scalar));
//
//         let mut last_radius = radius;
//         for x in range(1, width) {
//             let radius     = horizontal_radii[x];
//             let radius_dif = last_radius as i32 - radius as i32;
//
//             let x_last_left  = x as i32 - 1 - last_radius;
//             let x_last_right = x as i32 - 1 + last_radius;
//
//             for x_sub in range(x_last_left, x_last_left + radius_dif + 1) {
//                 let x_clamped = clamp(x_sub, foreground.width());
//                 let left_sub = RgbF::from(foreground.get_pixel(x_clamped, y_clamped));
//
//                 average -= left_sub;
//             }
//
//             for x_add in range(x_last_right, x_last_right - radius_dif + 1) {
//                 let x_clamped = clamp(x_add, foreground.width());
//                 let left_add = RgbF::from(foreground.get_pixel(x_clamped, y_clamped));
//
//                 average += left_add;
//             }
//
//             let scalar = 1f64 ((radius * 2 + 1) as f64);
//             image.put_pixel(x, y_rectangle, average.to_rgb(scalar));
//
//             last_radius = radius;
//         }
//     }
//
//     image
// }

// fn relevant_rectangle(left : i32, top : i32, width : u32, height : u32,
//                       left_radii : &[u32], top_radii : &[u32], outside_radius : u32, iterations : u32)
//                       -> (i32, i32, u32, u32, u32, u32) {
//
//     if iterations == 0 {
//         return (left, top, width, height, 0, 0);
//     }
//
//     let left_extension = left_radii.iter().enumerate().fold(0, |acc, (index, left_radius)| std::cmp::max(acc, left_radius - index));
//     let top_extension  =  top_radii.iter().enumerate().fold(0, |acc, (index, top_radius)|  std::cmp::max(acc, top_radius  - index));
//
//     let left_extension = left_extension + (iterations - 1) * outside_radius;
//     let top_extension  = top_extension  + (iterations - 1) * outside_radius;
//
//     (left - left_extension, top - top_extension, width + left_extension, height + top_extension, left_extension, top_extension)
// }

fn relevant_rectangle_extensions(left : i32, top : i32, width : u32, height : u32,
                                 left_radii : &[u32], top_radii : &[u32], outside_radius : u32, iterations : u32)
                                 -> (u32, u32) {

    if iterations == 0 {
        return (0, 0)
    }

    let left_extension = left_radii.iter().enumerate().fold(0, |acc, (index, left_radius)| std::cmp::max(acc, *left_radius - index as u32));
    let top_extension  =  top_radii.iter().enumerate().fold(0, |acc, (index, top_radius)|  std::cmp::max(acc, *top_radius  - index as u32));

    let left_extension = left_extension + (iterations - 1) * outside_radius;
    let top_extension  = top_extension  + (iterations - 1) * outside_radius;

    (left_extension, top_extension)
}

fn radii_vector(border_radii : &[u32], size : u32, extension : u32, inside_radius : u32, outside_radius : u32) -> Vec<u32> {
    let mut radii = Vec::with_capacity(size as usize);

    let inside_size     = size as usize - 2 * border_radii.len() - 2 * extension as usize;
    let inside_radii    = std::iter::repeat(inside_radius).take(inside_size);
    let extension_radii = std::iter::repeat(outside_radius).take(extension as usize);

    radii.extend(extension_radii.clone());
    radii.extend(border_radii.iter());
    radii.extend(inside_radii);
    radii.extend(border_radii.iter().rev());
    radii.extend(extension_radii);

    radii
}

fn blur_box_subimage_horizontal(subimage : RgbImage, horizontal_radii : &[u32]) -> RgbImage {
    let width  = subimage.width();
    let height = subimage.height();

    let mut image = RgbImage::new(width, height);

    for y in range(0, height) {
        let radius = horizontal_radii[0];
        let mut average = RgbF::from(subimage.get_pixel(0, y)) * (radius + 1) as f64;

        for i in range(1, radius + 1) {
            let x_right = uclamp(i, subimage.width());
            let right   = RgbF::from(subimage.get_pixel(x_right, y));

            average += right;
        }

        let scalar = 1f64 / ((radius * 2 + 1) as f64);
        image.put_pixel(0, y, average.to_rgb(scalar));

        let mut last_radius = radius;
        for x in range(1, width) {
            let radius     = horizontal_radii[x as usize];
            let radius_dif = last_radius as i32 - radius as i32;

            let x_last_left  = x as i32 - 1 - last_radius as i32;
            let x_last_right = x as i32 - 1 + last_radius as i32;

            for x_sub in range(x_last_left, x_last_left + 1 + radius_dif) {
                let x_clamped = clamp(x_sub, subimage.width());
                let left_sub  = RgbF::from(subimage.get_pixel(x_clamped, y));

                average -= left_sub;
            }

            for x_add in range(x_last_right, x_last_right + 1 - radius_dif) {
                let x_clamped = clamp(x_add, subimage.width());
                let right_add = RgbF::from(subimage.get_pixel(x_clamped, y));

                average += right_add;
            }

            let scalar = 1f64 / ((radius * 2 + 1) as f64);
            image.put_pixel(x, y, average.to_rgb(scalar));

            last_radius = radius;
        }
    }

    image
}

fn blur_box_subimage_vertical(subimage : RgbImage, vertical_radii : &[u32]) -> RgbImage {
    let width  = subimage.width();
    let height = subimage.height();

    let mut image = RgbImage::new(width, height);

    for x in range(0, width) {
        let radius = vertical_radii[0];
        let mut average = RgbF::from(subimage.get_pixel(x, 0)) * (radius + 1) as f64;

        for i in range(1, radius + 1) {
            let y_bot = uclamp(i, subimage.height());
            let bot   = RgbF::from(subimage.get_pixel(x, y_bot));

            average += bot;
        }

        let scalar = 1f64 / ((radius * 2 + 1) as f64);
        image.put_pixel(x, 0, average.to_rgb(scalar));

        let mut last_radius = radius;
        for y in range(1, height) {
            let radius     = vertical_radii[y as usize];
            let radius_dif = last_radius as i32 - radius as i32;

            let y_last_top = y as i32 - 1 - last_radius as i32;
            let y_last_bot = y as i32 - 1 + last_radius as i32;

            for y_sub in range(y_last_top, y_last_top + 1 + radius_dif) {
                let y_clamped = clamp(y_sub, subimage.height());
                let top_sub   = RgbF::from(subimage.get_pixel(x, y_clamped));

                average -= top_sub;
            }

            for y_add in range(y_last_bot, y_last_bot + 1 - radius_dif) {
                let y_clamped = clamp(y_add, subimage.height());
                let bot_add   = RgbF::from(subimage.get_pixel(x, y_clamped));

                average += bot_add;
            }

            let scalar = 1f64 / ((radius * 2 + 1) as f64);
            image.put_pixel(x, y, average.to_rgb(scalar));

            last_radius = radius;
        }
    }

    image
}

pub fn blur_box(mut background : RgbImage, foreground : RgbImage, left : i32, top : i32, width : u32, height : u32,
                left_radii : &[u32], top_radii : &[u32], inside_radius : u32, outside_radius : u32, iterations : u32)
                -> RgbImage {

    let (left_extension, top_extension) = relevant_rectangle_extensions(left, top, width, height, left_radii, top_radii, outside_radius, iterations);

    let left_extended   = left   - left_extension as i32;
    let top_extended    = top    - top_extension as i32;
    let width_extended  = width  + left_extension;
    let height_extended = height + top_extension;

    let mut horizontal_radii = radii_vector(left_radii, width_extended,  left_extension, inside_radius, outside_radius);
    let mut vertical_radii   = radii_vector(top_radii,  height_extended, top_extension,  inside_radius, outside_radius);

    let left_extended_clamped   = clamp(left_extended, foreground.width());
    let top_extended_clamped    = clamp(top_extended,  foreground.height());
    let width_extended_clamped  = uclamp(width_extended,  foreground.width()  - left_extended_clamped);
    let height_extended_clamped = uclamp(height_extended, foreground.height() - top_extended_clamped);

    let view         = foreground.view(left_extended_clamped, top_extended_clamped, width_extended_clamped, height_extended_clamped);
    let mut subimage = RgbImage::new(width_extended_clamped, height_extended_clamped);
    subimage.copy_from(&view, 0, 0);

    for _ in range(0, iterations) {
        subimage = blur_box_subimage_horizontal(subimage, horizontal_radii.as_slice());
        subimage = blur_box_subimage_vertical(subimage, vertical_radii.as_slice());
    }

    let left_clamped   = uclamp(left_extension, subimage.width());
    let top_clamped    = uclamp(top_extension,  subimage.height());
    let width_clamped  = uclamp(width, subimage.width() - left_clamped);
    let height_clamped = uclamp(height, subimage.height() - top_clamped);

    let view = subimage.view(left_clamped, top_clamped, width_clamped, height_clamped);

    let left_clamped   = clamp(left, background.width());
    let top_clamped    = clamp(top,  background.height());
    let width_clamped  = uclamp(width, background.width()   - left_clamped);
    let height_clamped = uclamp(height, background.height() - top_clamped);

    let mut bubble = RgbImage::new(width_clamped, height_clamped);
    bubble.copy_from(&view, 0, 0);

    background.copy_from(&bubble, left_clamped, top_clamped);
    background
}