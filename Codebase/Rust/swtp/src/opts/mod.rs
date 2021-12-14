use std::string::{ String };

use serde_json as sj;

pub struct BoxBlur {
    pub source     : String,
    pub target     : String,
    pub radius     : u32,
    pub iterations : u32,
    pub threads    : u32
}

pub struct Pixelate {
    pub source   : String,
    pub target   : String,
    pub diameter : u32,
    pub threads  : u32
}

pub enum Filter {
    BoxBlur(BoxBlur),
    Pixelate(Pixelate)
}

pub enum Action {
    Filter(Filter)
}


pub fn parse_box_blur(options : sj::Value) -> Option<BoxBlur> {
    let source     = String::from(options.get("source")?.as_str()?);
    let target     = String::from(options.get("target")?.as_str()?);
    let radius     = options.get("radius")?.as_u64()? as u32;
    let iterations = options.get("iterations")?.as_u64()? as u32;
    let threads    = options.get("threads")?.as_u64()? as u32;

    Some(BoxBlur{source, target, radius, iterations, threads})
}


pub fn parse_pixelate(options : sj::Value) -> Option<Pixelate> {
    let source   = String::from(options.get("source")?.as_str()?);
    let target   = String::from(options.get("target")?.as_str()?);
    let diameter = options.get("diameter")?.as_u64()? as u32;
    let threads  = options.get("threads")?.as_u64()? as u32;

    Some(Pixelate{source, target, diameter, threads})
}


pub fn parse_filter(options : sj::Value) -> Option<Filter> {
    match options.get("filter")?.as_str()? {
        "box_blur"  => parse_box_blur(options).map(Filter::BoxBlur),
        "pixelate"  => parse_pixelate(options).map(Filter::Pixelate),
        _           => { println!("parse_filter: {:?}", options); None }
    }
}

pub fn parse_action(options : sj::Value) -> Option<Action> {
    match options.get("action")?.as_str()? {
        "filter" => parse_filter(options).map(Action::Filter),
        _        => { println!("parse_action: {:?}", options); None }
    }
}

pub fn parse(options : String) -> Option<Action> {
    match sj::from_str::<sj::Value>(&options) {
        Ok(options) => parse_action(options),
        Err(_)      => { println!("parse: {}", options); None }
    }
}