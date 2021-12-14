use std::sync;
use std::thread;
use std::time;

use image::{ Rgb, RgbImage, GenericImage, GenericImageView };

use crate::base::{ range };
use crate::image::{ RgbU };

pub fn pixelate(source : RgbImage, diameter : u32) -> RgbImage {
    let width          = source.width();
    let height         = source.height();

    let width_rest   = width  % diameter;
    let height_rest  = height & diameter;
    let pixel_width  = if width_rest  == 0 {width  / diameter} else {1 + width  / diameter};
    let pixel_height = if height_rest == 0 {height / diameter} else {1 + height / diameter};

    let mut pixels = range(0, pixel_width)
        .map(|_| range(0, pixel_height).map(|_| (0, RgbU::new(0, 0, 0))).collect::<Vec<(u64, RgbU)>>())
        .collect::<Vec<_>>();

    for y in range(0, height) {
        let pixel_y = (y / diameter) as usize;

        for x in range(0, width) {
            let pixel_x = (x / diameter) as usize;
            pixels[pixel_x][pixel_y].0 += 1;
            pixels[pixel_x][pixel_y].1 += RgbU::from(source.get_pixel(x, y));
        }
    }

    let pixels = pixels.iter()
        .map(|vec| vec.iter().map(|(area, rgb)| rgb.to_rgb(1f64 / (*area as f64))).collect::<Vec<Rgb<u8>>>())
        .collect::<Vec<_>>();

    let mut image  = RgbImage::new(width, height);

    for y in range(0, height) {
        let pixel_y = (y / diameter) as usize;

        for x in range(0, width) {
            let pixel_x = (x / diameter) as usize;
            image.put_pixel(x, y, pixels[pixel_x][pixel_y]);
        }
    }

    image
}

pub fn pixelate_subimage_horizontal(source : sync::Arc<RgbImage>, diameter : u32, top : u32, height : u32, pixel_width : u32, pixel_height : u32) -> RgbImage {
    let width  = source.width();

    let pixels = range(0, pixel_height)
        .map(|y| {
            let height_pixel = std::cmp::min(diameter, height - y * diameter);
            let y_offset     = y * diameter + top;

            range(0, pixel_width)
                .map(|x| {
                    let width_pixel = std::cmp::min(diameter, width - x * diameter);
                    let area        = height_pixel * width_pixel;
                    let x_offset    = x * diameter;

                    let x_range = range(x_offset, x_offset + width_pixel);
                    let y_range = range(y_offset, y_offset + height_pixel);

                    x_range
                        .fold(RgbU::new(0, 0, 0), |acc, x| {
                            y_range.clone().fold(acc.clone(), |acc, y| {
                                acc + RgbU::from(source.get_pixel(x, y))
                            })
                        })
                        .to_rgb(1f64 / (area as f64))
                })
                .collect::<Vec<Rgb<u8>>>()
        })
        .collect::<Vec<_>>();

    let mut subimage = RgbImage::new(width, height);

    for y in range(0, height) {
        let pixel_y = (y / diameter) as usize;

        for x in range(0, width) {
            let pixel_x = (x / diameter) as usize;
            subimage.put_pixel(x, y, pixels[pixel_y][pixel_x])
        }
    }

    subimage
}

pub fn pixelate_parallel_horizontal(source : RgbImage, diameter : u32, threads : u32, pixel_width : u32, pixel_height : u32, vertical_rest : u32) -> RgbImage {
    let width  = source.width();
    let height = source.height();

    let source      = sync::Arc::new(source);
    let (send, rec) = sync::mpsc::channel::<(u32, u32, RgbImage)>();

    let mut handles      = Vec::new();
    let mut height_rest  = height;
    let mut top          = 0u32;

    let instant = time::Instant::now();

    for i in range(0, threads) {
        let source       = source.clone();
        let pixel_height = (pixel_height / threads) + if vertical_rest != 0 {1 - i / vertical_rest} else {0} ;
        let height       = std::cmp::min(pixel_height * diameter, height_rest);
        let send         = send.clone();

        let handle = thread::spawn(move || {
            let subimage = pixelate_subimage_horizontal(source, diameter, top, height, pixel_width, pixel_height);
            send.send((i, top, subimage));
        });

        handles.push(handle);
        top          += height;
        height_rest  -= height;
    }

    let mut image    = RgbImage::new(width, height);
    let mut recieved = 0;
    let mut failed   = 0;

    while recieved + failed != threads {
        match rec.recv() {
            Err(_)                 => failed += 1,
            Ok((_, top, subimage)) => {
                recieved += 1;
                image.copy_from(&subimage, 0, top);
            }
        }
    }

    println!("pixelate_parallel_horizontal: {:?}", instant.elapsed());

    image
}

pub fn pixelate_parallel_vertical(source : RgbImage, diameter : u32, threads : u32) -> RgbImage {
    unimplemented!()
}

pub fn pixelate_parallel(source : RgbImage, diameter : u32, threads : u32) -> RgbImage {
    let instant = time::Instant::now();

    let width  = source.width();
    let height = source.height();

    let width_rest  = width  % diameter;
    let height_rest = height % diameter;

    let pixel_width  = if width_rest  == 0 {width  / diameter} else {1 + width  / diameter};
    let pixel_height = if height_rest == 0 {height / diameter} else {1 + height / diameter};

    let horizontal_rest = pixel_width  % threads;
    let vertical_rest   = pixel_height % threads;

    let horizontal_distance = std::cmp::min(horizontal_rest, threads - horizontal_rest);
    let vertical_distance   = std::cmp::min(vertical_rest  , threads - vertical_rest);

    // TODO: vertial pixelate
    let image = match horizontal_distance < vertical_distance {
        _ => pixelate_parallel_horizontal(source, diameter, threads, pixel_width, pixel_height, vertical_rest)
    };

    println!("pixelate_parallel: {:?}", instant.elapsed());

    image
}