pub mod base;
pub mod img;


use std::time::Instant;

use pyo3::prelude::*;
use pyo3::types::{ PyBytes };

use image::{EncodableLayout, RgbImage};

use img::filter::blur::{ r#box, box_parallel };
use img::filter::pixelate::{square, square_parallel};

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
fn rust(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(blur_box, m)?)?;
    m.add_function(wrap_pyfunction!(pixelate_square, m)?)?;
    Ok(())
}
