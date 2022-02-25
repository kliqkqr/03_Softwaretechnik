use std::cmp;

pub fn range<A>(start : A, end : A) -> std::ops::Range<A> {
    start .. end
}

pub fn clamp(index : i32, size : u32) -> u32 {
    cmp::max(0, cmp::min(index , (size - 1) as i32)) as u32
}

pub fn uclamp(index : u32, size : u32) -> u32 {
    cmp::min(index, size - 1)
}

pub fn contains(dimensions: &(u32, u32), x : i32, y : i32) -> bool {
    if x < 0 || y < 0 {
        return false;
    }

    let (width, height) = dimensions;
    (x as u32) < *width && (y as u32) < *height
}
