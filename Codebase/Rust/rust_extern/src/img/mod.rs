pub mod bubble;
pub mod filter;

use std::path::{ Path };

use image::{ Rgb, DynamicImage, GenericImageView };
use image::io::{ Reader };

pub struct RgbU {
    r : u64,
    g : u64,
    b : u64
}

pub struct RgbF {
    r : f64,
    g : f64,
    b : f64
}


impl RgbU {
    pub fn new(r : u64, g : u64, b : u64) -> RgbU {
        RgbU{r, g, b}
    }

    pub fn from(rgb : &Rgb<u8>) -> RgbU {
        let r = rgb[0] as u64;
        let g = rgb[1] as u64;
        let b = rgb[2] as u64;
        RgbU{r, g, b}
    }

    pub fn to_rgb(&self, scalar : f64) -> Rgb<u8> {
        let r = (self.r as f64 * scalar) as u8;
        let g = (self.g as f64 * scalar) as u8;
        let b = (self.b as f64 * scalar) as u8;
        Rgb::from([r, g, b])
    }
}

impl RgbF {
    pub fn new(r : f64, g : f64, b : f64) -> RgbF {
        RgbF{r, g, b}
    }

    pub fn from(rgb : &Rgb<u8>) -> RgbF {
        let r = rgb[0] as f64;
        let g = rgb[1] as f64;
        let b = rgb[2] as f64;
        RgbF{r, g, b}
    }

    pub fn to_rgb(&self, scalar : f64) -> Rgb<u8> {
        let r = (self.r * scalar) as u8;
        let g = (self.g * scalar) as u8;
        let b = (self.b * scalar) as u8;
        Rgb::from([r, g, b])
    }
}



impl std::clone::Clone for RgbU {
    fn clone(&self) -> Self {
        RgbU::new(self.r, self.g, self.b)
    }
}

impl std::ops::Add for RgbU {
    type Output = RgbU;
    fn add(self, rhs : RgbU) -> RgbU {
        RgbU{r : self.r + rhs.r, g : self.g + rhs.g, b : self.b + rhs.b}
    }
}

impl std::ops::AddAssign for RgbU {
    fn add_assign(&mut self, rhs: Self) {
        self.r += rhs.r;
        self.g += rhs.g;
        self.b += rhs.b;
    }
}

impl std::ops::Add for RgbF {
    type Output = RgbF;
    fn add(self, rhs : RgbF) -> RgbF {
        RgbF{r : self.r + rhs.r, g : self.g + rhs.g, b : self.b + rhs.b}
    }
}

impl std::ops::AddAssign for RgbF {
    fn add_assign(&mut self, rhs: Self) {
        self.r += rhs.r;
        self.g += rhs.g;
        self.b += rhs.b;
    }
}

impl std::ops::Sub for RgbF {
    type Output = RgbF;
    fn sub(self, rhs : RgbF) -> RgbF {
        RgbF{r : self.r - rhs.r, g : self.g - rhs.g, b : self.b - rhs.b}
    }
}

impl std::ops::Sub for &RgbF {
    type Output = RgbF;
    fn sub(self, rhs : &RgbF) -> RgbF {
        RgbF{r : self.r - rhs.r, g : self.g - rhs.g, b : self.b - rhs.b}
    }
}

impl std::ops::SubAssign for RgbF {
    fn sub_assign(&mut self, rhs: Self) {
        self.r -= rhs.r;
        self.g -= rhs.g;
        self.b -= rhs.b;
    }
}

impl std::ops::Mul<f64> for RgbF {
    type Output = RgbF;
    fn mul(self, rhs: f64) -> Self::Output {
        RgbF::new(self.r * rhs, self.g * rhs, self.b * rhs)
    }
}


pub fn open_image<A : AsRef<Path>>(path : A) -> Option<DynamicImage> {
    Reader::open(path).ok().and_then(|stream| stream.decode().ok())
}
