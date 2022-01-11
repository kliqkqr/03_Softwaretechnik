pub mod base;
pub mod img;

use pyo3::prelude::*;
use pyo3::types::{ PyBytes };

use image::{EncodableLayout, RgbImage};

use img::filter::blur::{ r#box, box_parallel };
use img::filter::pixelate::{square, square_parallel};

use img::bubble;

#[pyfunction]
fn bubble_box_blur_rectangle<'a>(py : Python<'a>,
                                 b_width : u32, b_height : u32, b_bytes : &PyBytes,
                                 f_width : u32, f_height : u32, f_bytes : &PyBytes,
                                 left : u32, top : u32, width : u32, height : u32,
                                 left_radii : &PyBytes, top_radii : &PyBytes,
                                 inside_radius : u32, outside_radius : u32,
                                 iterations : u32)
                                 -> &'a PyBytes {

}

#[pyfunction]
fn bubble_rectangle<'a>(py : Python<'a>,
                        b_width : u32, b_height : u32, b_bytes : &PyBytes,
                        f_width : u32, f_height : u32, f_bytes : &PyBytes,
                        left : i32, top : i32, width : u32, height : u32)
                        -> &'a PyBytes {
    let b_buf = Vec::from(b_bytes.as_bytes());
    let f_buf = Vec::from(f_bytes.as_bytes());

    let (b_img, f_img) = match (RgbImage::from_raw(b_width, b_height, b_buf), RgbImage::from_raw(f_width, f_height, f_buf)) {
        (Some(b_img), Some(f_img)) => (b_img, f_img),
        _                          => return PyBytes::new(py, &[])
    };

    let img = bubble::rectangle(b_img, &f_img, left, top, width, height);
    PyBytes::new(py, img.into_raw().as_bytes())
}

#[pyfunction]
fn bubble_ellipse<'a>(py : Python<'a>,
                      b_width : u32, b_height : u32, b_bytes : &PyBytes,
                      f_width : u32, f_height : u32, f_bytes : &PyBytes,
                      left : i32, top : i32, width : u32, height : u32)
                      -> &'a PyBytes {
    let b_buf = Vec::from(b_bytes.as_bytes());
    let f_buf = Vec::from(f_bytes.as_bytes());

    let (b_img, f_img) = match (RgbImage::from_raw(b_width, b_height, b_buf), RgbImage::from_raw(f_width, f_height, f_buf)) {
        (Some(b_img), Some(f_img)) => (b_img, f_img),
        _                          => return PyBytes::new(py, &[])
    };

    let img = bubble::ellipse(b_img, &f_img, left, top, width, height);
    PyBytes::new(py, img.into_raw().as_bytes())
}

#[pyfunction]
fn pixelate_square<'a>(py : Python<'a>, width : u32, height : u32, bytes : &PyBytes, diameter : u32, threads : u32) -> &'a PyBytes {
    let buf = Vec::from(bytes.as_bytes());

    let img = match RgbImage::from_raw(width, height, buf) {
        Some(img) => img,
        None      => return PyBytes::new(py, &[])
    };

    let img = match threads {
        0 => return PyBytes::new(py, &[]),
        1 => square(img, diameter),
        t => square_parallel(img, diameter, t)
    };

    PyBytes::new(py, img.into_raw().as_bytes())
}

#[pyfunction]
fn blur_box<'a>(py : Python<'a>, width : u32, height : u32, bytes : &PyBytes, radius : u32, iterations : u32, threads : u32) -> &'a PyBytes {
    let buf = Vec::from(bytes.as_bytes());

    let img = match RgbImage::from_raw(width, height, buf) {
        Some(img) => img,
        None      => return PyBytes::new(py, &[])
    };

    let img = match threads {
        0 => return PyBytes::new(py, &[]),
        1 => r#box(img, radius, iterations),
        t => box_parallel(img, radius, iterations, t)
    };

    PyBytes::new(py, img.into_raw().as_bytes())
}


/// A Python module implemented in Rust.
#[pymodule]
fn rust_extern(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(blur_box, m)?)?;
    m.add_function(wrap_pyfunction!(pixelate_square, m)?)?;
    m.add_function(wrap_pyfunction!(bubble_rectangle, m)?)?;
    m.add_function(wrap_pyfunction!(bubble_ellipse, m)?)?;
    Ok(())
}
