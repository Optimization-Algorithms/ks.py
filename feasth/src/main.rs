mod error;
mod file_utils;
mod log_parser;
mod mps_parser;

use std::path::PathBuf;
use structopt::{StructOpt, clap::ArgGroup};

#[derive(Debug, StructOpt)]
#[structopt(group = ArgGroup::with_name("file").required(true))]
struct ModelSize {
    #[structopt(help="Specify model size directly", name="Model size", short="s", long="size", group = "file")]
    size: Option<usize>,
    #[structopt(help="Specify MPS file and compute model size automatically", short="i", name="Model File", long="instance", group = "file")]
    file: Option<PathBuf>

}

#[derive(Debug, StructOpt)]
#[structopt(about = "Compute Continuous and Integer Feasibility Threshold")]
struct Arguments {
    #[structopt(flatten)]
    mps_file: ModelSize,
    #[structopt(help = "CSV log file from Feature Kernel `LOG_FILE`")]
    log_file: PathBuf,
}


fn average(counter: log_parser::TotalCount) -> Option<f64> {
    if counter.count == 0 {
        None
    } else {
        Some((counter.total as f64) / (counter.count as f64))
    }
    
    
}

fn get_ratio(counter: log_parser::TotalCount, size: usize) -> Option<f64> {
    let avg = average(counter)?;
    Some(avg / (size as f64))
}

fn print_index(name: &str, value: Option<f64>) {
    print!("{}: ", name);
    if let Some(value) = value {
        println!("{}", value);   
    } else {
        println!("UNDEFINED");
    }
}

fn run_file_parse(args: Arguments) -> Result<(usize, log_parser::TotalSize), error::ParseError> {
    let count = if let Some(count) = args.mps_file.size {
        count
    } else if let Some(file) = args.mps_file.file {
        mps_parser::get_variable_count(&file)?
    } else {
        unreachable!()
    };
    let tot_size = log_parser::get_average_sizes(&args.log_file)?;
    Ok((count, tot_size))
}

fn largest_index(cft: &Option<f64>, ift: &Option<f64>) -> Option<f64> {
    match (cft, ift) {
        (Some(cft), Some(ift)) => Some(if cft > ift {*cft} else {*ift}),
        (Some(cft), None) => Some(*cft),
        (None, Some(ift)) => Some(*ift),
        (None, None) => None
    }
}

fn warn_size(cft: &Option<f64>, ift: &Option<f64>) {
    let avg = largest_index(cft, ift);
    if let Some(avg) = avg {
        if avg > 1.0 {
            println!("Model is smaller than the average sub model size");
            println!("Possible Causes:");
            println!("\tMPS is not standard");
            println!("\tMPS and CSV are not for the same problem");
            println!("Consider to provide the model size directly");
        }
    }
}

fn run() -> Result<(), error::ParseError> {
    let args = Arguments::from_args();

    let (count, tot_size) = run_file_parse(args)?;
    println!("Model Size: {}", count);

    let continuous_threshold = get_ratio(tot_size.continuous, count);
    let integer_threshold = get_ratio(tot_size.integer, count);

    warn_size(&continuous_threshold, &integer_threshold);

    print_index("CFT", continuous_threshold);
    print_index("IFT", integer_threshold);
    Ok(())
}

fn main() {

    match run() {
        Ok(()) => {}
        Err(err) => println!("{}", err),
    }
}
