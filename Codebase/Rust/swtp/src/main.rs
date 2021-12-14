use std::env;
use std::time;

use swtp::image::{ open_image };
use swtp::image::filter::{ blur, pixelate };
use swtp::opts;
use swtp::opts::{ Action, Filter, BoxBlur, Pixelate };

fn action_filter_box_blur(options : BoxBlur) {
    let image = open_image(options.source).expect("coudn't open source").to_rgb8();

    let image = match options.threads {
        0 => panic!("0 threads not valid"),
        1 => blur::r#box(&image, options.radius, options.iterations),
        t => blur::box_parallel(image, options.radius, options.iterations, t)
    };

    image.save(options.target).expect("coudn't save target");
}


fn action_filter_pixelate(options : Pixelate) {
    let instant = time::Instant::now();
    let image = open_image(options.source).expect("coudn't open source").to_rgb8();
    println!("action_filter_pixelate.open: {:?}", instant.elapsed());

    let image = match options.threads {
        0 => panic!("0 threads not valid"),
        1 => pixelate::pixelate(image, options.diameter),
        t => pixelate::pixelate_parallel(image, options.diameter, t)
    };
    println!("action_filter_pixelate.filter: {:?}", instant.elapsed());

    image.save(options.target).expect("coudn't save target");
    println!("action_filter_pixelate.save: {:?}", instant.elapsed());
}


fn main() {
    let instant = time::Instant::now();

    let options = env::args().nth(1).expect("not 2 arguments");
    let action  = opts::parse(options).expect("couldn't parse options");

    match action {
        Action::Filter(filter) => match filter {
            Filter::BoxBlur(box_blur)  => action_filter_box_blur(box_blur),
            Filter::Pixelate(pixelate) => action_filter_pixelate(pixelate)
        }
    }

    println!("main: {:?}", instant.elapsed());
}
