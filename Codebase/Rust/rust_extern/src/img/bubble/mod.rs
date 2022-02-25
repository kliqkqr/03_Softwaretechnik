pub mod rectangle;

use image::{RgbImage, GenericImage, GenericImageView, Pixel};

use crate::base::{ uclamp, clamp, range, contains };
use crate::img::{ RgbF };

pub fn rectangle(mut background : RgbImage, foreground : &RgbImage, left : i32, top : i32, width : u32, height : u32) -> RgbImage {
    let b_left = clamp(left, background.width());
    let b_top  = clamp(top,  background.height());

    let f_left = clamp(left, foreground.width());
    let f_top  = clamp(top,  foreground.height());

    let width  = uclamp(uclamp(width,  background.width()  - b_left), foreground.width()  - f_left);
    let height = uclamp(uclamp(height, background.height() - b_top),  foreground.height() - f_top);

    let view = foreground.view(f_left, f_top, width, height);
    background.copy_from(&view, b_left, b_top);

    background
}

pub fn ellipse(mut background : RgbImage, foreground : &RgbImage, left : i32, top : i32, width : u32, height : u32) -> RgbImage {
    let ellipse_radius_horizontal = width  as f64 / 2f64;
    let ellipse_radius_vertical   = height as f64 / 2f64;
    let ellipse_center_x = left as f64 + ellipse_radius_horizontal;
    let ellipse_center_y = top  as f64 + ellipse_radius_vertical;

    for x in range(left, left + width as i32) {
        for y in range(top, top + height as i32) {
            let x_norm = x as f64 - ellipse_center_x;
            let y_norm = y as f64 - ellipse_center_y;

            if (x_norm * x_norm) / (ellipse_radius_horizontal * ellipse_radius_horizontal) +
               (y_norm * y_norm) / (ellipse_radius_vertical   * ellipse_radius_vertical)
               <= 1f64 {
                let b_x = clamp(x, background.width());
                let b_y = clamp(y, background.height());
                let f_x = clamp(x, foreground.width());
                let f_y = clamp(y, foreground.height());
                background.put_pixel(b_x, b_y, foreground.get_pixel(f_x, f_y).to_rgb());
            }
        }
    }

    background
}

pub fn power_ellipse_interpolation(mut background : RgbImage, foreground : &RgbImage, left : i32, top : i32, width : u32, height : u32, exponent : f64) -> RgbImage {
    let background_dimensions = background.dimensions();

    let ellipse_radius_horizontal = width  as f64 / 2f64;
    let ellipse_radius_vertical   = height as f64 / 2f64;
    let ellipse_center_x = left as f64 + ellipse_radius_horizontal;
    let ellipse_center_y = top  as f64 + ellipse_radius_vertical;

    for x in range(left, left + width as i32) {
        for y in range(top, top + height as i32) {
            if !contains(&background_dimensions, x, y) {
                continue;
            }

            let x_norm = x as f64 - ellipse_center_x;
            let y_norm = y as f64 - ellipse_center_y;

            let distance_norm = (x_norm * x_norm) / (ellipse_radius_horizontal * ellipse_radius_horizontal)
                + (y_norm * y_norm) / (ellipse_radius_vertical   * ellipse_radius_vertical);
            let distance_norm = distance_norm.sqrt();

            if distance_norm <= 1f64 {
                let b_x = x as u32;
                let b_y = y as u32;
                let b_rgbf = RgbF::from(background.get_pixel(b_x, b_y));

                let f_x = clamp(x, foreground.width());
                let f_y = clamp(y, foreground.height());
                let f_rgbf = RgbF::from(foreground.get_pixel(f_x, f_y));

                let interpolation_coefficient = f64::powf(distance_norm, exponent);
                let interpolated_rgbf = (&b_rgbf - &f_rgbf) * interpolation_coefficient + f_rgbf;

                background.put_pixel(b_x, b_y, interpolated_rgbf.to_rgb(1f64));
            }
        }
    }

    background
}

pub fn power_rectangle_interpolation(mut background : RgbImage, foreground : &RgbImage, left : i32, top : i32, width : u32, height : u32, exponent : f64) -> RgbImage {
    let background_dimensions = background.dimensions();

    let rectangle_radius_horizontal = width as f64 / 2f64;
    let rectangle_radius_vertical = height as f64 / 2f64;
    let rectangle_center_x = left as f64 + rectangle_radius_horizontal;
    let rectangle_center_y = top as f64 + rectangle_radius_vertical;

    for x in range(left, left + width as i32) {
        for y in range(top, top + height as i32) {
            if !contains(&background_dimensions, x, y) {
                continue;
            }

            let b_x = x as u32;
            let b_y = y as u32;
            let b_rgbf = RgbF::from(background.get_pixel(b_x, b_y));

            let f_x = clamp(x, foreground.width());
            let f_y = clamp(y, foreground.height());
            let f_rgbf = RgbF::from(foreground.get_pixel(f_x, f_y));

            let x_distance = (x as f64 - rectangle_center_x).abs();
            let y_distance = (y as f64 - rectangle_center_y).abs();
            let x_distance_norm = x_distance / rectangle_radius_horizontal;
            let y_distance_norm = y_distance / rectangle_radius_vertical;
            let max_distance_norm = f64::max(x_distance_norm, y_distance_norm);

            let interpolation_coefficient = f64::powf(max_distance_norm, exponent);
            let interpolated_rgbf = (&b_rgbf - &f_rgbf) * interpolation_coefficient + f_rgbf;

            background.put_pixel(b_x, b_y, interpolated_rgbf.to_rgb(1f64));
        }
    }

    background
}
