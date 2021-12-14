use std;
use std::cmp;
use std::sync;
use std::thread;
use std::vec;

use image::{ Rgb, RgbImage,
             GenericImage, GenericImageView };

use crate::base::{ range, clamp };
use crate::image::{ RgbF };


pub fn horizontal_box(source : &RgbImage, radius : u32) -> RgbImage {
    let width    = source.width();
    let height   = source.height();
    let scalar   = 1f64 / ((radius * 2 + 1) as f64);
    let i_radius = radius as i32;

    let mut horizontals = RgbImage::new(width, height);

    for y in range(0, height) {
        let mut average = RgbF::from(source.get_pixel(0, y));

        for i in range(1, radius + 1) {
            let left  = RgbF::from(source.get_pixel(0, y));
            let right = RgbF::from(source.get_pixel(clamp(i as i32, width), y));

            average += left + right;
        }

        horizontals.put_pixel(0, y, average.to_rgb(scalar));

        for x in range(1, width) {
            let i_x    = x as i32;
            let left   = RgbF::from(source.get_pixel(clamp(i_x - i_radius - 1, width), y));
            let right  = RgbF::from(source.get_pixel(clamp(i_x + i_radius, width), y));

            average -= left;
            average += right;

            horizontals.put_pixel(x, y, average.to_rgb(scalar));
        }
    }

    horizontals
}

pub fn vertical_box(source : &RgbImage, radius : u32) -> RgbImage {
    let width    = source.width();
    let height   = source.height();
    let scalar   = 1f64 / ((radius * 2 + 1) as f64);
    let i_radius = radius as i32;

    let mut verticals = RgbImage::new(width, height);

    for x in range(0, width) {
        let mut average = RgbF::from(source.get_pixel(x, 0));

        for i in range(1, radius + 1) {
            let left  = RgbF::from(source.get_pixel(x, 0));
            let right = RgbF::from(source.get_pixel(x, clamp(i as i32, height)));

            average += left + right;
        }

        verticals.put_pixel(x, 0, average.to_rgb(scalar));

        for y in range(1, height) {
            let i_y    = y as i32;
            let left   = RgbF::from(source.get_pixel(x, clamp(i_y - i_radius - 1, height)));
            let right  = RgbF::from(source.get_pixel(x, clamp(i_y + i_radius, height)));

            average -= left;
            average += right;

            verticals.put_pixel(x, y, average.to_rgb(scalar));
        }
    }

    verticals
}


pub fn r#box(source : &RgbImage, radius : u32, iterations : u32) -> RgbImage {
    let width  = source.width();
    let height = source.height();

    let mut image = RgbImage::new(width, height);
    image.copy_from(source, 0, 0);

    for _ in range(0, iterations) {
        image = horizontal_box(&image, radius);
    }

    for _ in range(0, iterations) {
        image = vertical_box(&image, radius);
    }

    image
}


pub fn subimage_horizontal_box(source : sync::Arc<RgbImage>, radius : u32, iterations : u32, top : u32, height : u32) -> RgbImage {
    let width = source.width();

    let mut subimage = RgbImage::new(width, height);
    subimage.copy_from(&source.view(0, top, width, height), 0, 0);

    for _ in range(0, iterations) {
        subimage = horizontal_box(&subimage, radius);
    }

    subimage
}


pub fn subimage_vertical_box(source : sync::Arc<RgbImage>, radius : u32, iterations : u32, left : u32, width : u32) -> RgbImage {
    let height = source.height();

    let mut subimage = RgbImage::new(width, height);
    subimage.copy_from(&source.view(left, 0, width, height), 0, 0);

    for _ in range(0, iterations) {
        subimage = vertical_box(&subimage, radius);

    }

    subimage
}


pub fn horizontal_box_parallel(source : RgbImage, radius : u32, iterations : u32, threads : u32) -> RgbImage {
    let threads_s = threads as usize;
    let width     = source.width();
    let height    = source.height();

    let subimage_height      = height / threads;
    let subimage_height_rest = height % threads;

    let source      = sync::Arc::new(source);
    let (send, rec) = sync::mpsc::channel::<(usize, u32, RgbImage)>();
    let mut handles = Vec::with_capacity(threads_s);

    let source_arc = source.clone();
    let send_clone = send.clone();
    let handle     = thread::spawn(move || {
        let subimage = subimage_horizontal_box(source_arc, radius, iterations, 0, subimage_height + subimage_height_rest);
        match send_clone.send((0, 0, subimage)) {
            Ok(_)  => true,
            Err(_) => false,
        }
    });
    handles.push(handle);


    for i in range(1, threads_s) {
        let source_arc = source.clone();
        let send_clone = send.clone();
        let top = i as u32 * subimage_height + subimage_height_rest;

        let handle     = thread::spawn(move || {
            let subimage = subimage_horizontal_box(source_arc, radius, iterations, top, subimage_height);
            send_clone.send((i, top, subimage)).is_ok()
        });
        handles.push(handle);
    }

    let mut image = RgbImage::new(width, height);

    let mut recieved = Vec::new();
    let mut failed   = 0;

    while recieved.len() + failed != threads_s {
        match rec.recv() {
            Err(_) => failed += 1,
            Ok((index, top, subimage)) => {
                recieved.push(index);
                image.copy_from(&subimage, 0, top);
            }
        }
    }

    image
}


pub fn vertical_box_parallel(source : RgbImage, radius : u32, iterations : u32, threads : u32) -> RgbImage {
    let threads_s = threads as usize;
    let width     = source.width();
    let height    = source.height();

    let subimage_width      = width / threads;
    let subimage_width_rest = width % threads;

    let source      = sync::Arc::new(source);
    let (send, rec) = sync::mpsc::channel::<(usize, u32, RgbImage)>();
    let mut handles = vec::Vec::with_capacity(threads_s);

    let source_arc = source.clone();
    let send_clone = send.clone();
    let handle     = thread::spawn(move || {
        let subimage = subimage_vertical_box(source_arc, radius, iterations, 0, subimage_width + subimage_width_rest);
        match send_clone.send((0, 0, subimage)) {
            Ok(_)  => true,
            Err(_) => false,
        }
    });
    handles.push(handle);

    for i in range(1, threads_s) {
        let source_arc = source.clone();
        let send_clone = send.clone();
        let left = i as u32 * subimage_width + subimage_width_rest;

        let handle     = thread::spawn(move || {
            let subimage = subimage_vertical_box(source_arc, radius, iterations, i as u32 * subimage_width + subimage_width_rest, subimage_width);
            send_clone.send((i, left, subimage)).is_ok()
        });
        handles.push(handle);
    }

    let mut image = RgbImage::new(width, height);

    let mut recieved = Vec::new();
    let mut failed   = 0;

    while recieved.len() + failed != threads_s {
        match rec.recv() {
            Err(_) => failed += 1,
            Ok((index, left, subimage)) => {
                recieved.push(index);
                image.copy_from(&subimage, left, 0);
            }
        }
    }

    image
}


pub fn box_parallel(source : RgbImage, radius : u32, iterations : u32, threads : u32) -> RgbImage {
    let horizontals = horizontal_box_parallel(source, radius, iterations, threads);
    vertical_box_parallel(horizontals, radius, iterations, threads)
}